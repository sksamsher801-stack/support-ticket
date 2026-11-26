import csv
from datetime import datetime, timedelta, date
from validators import (HEADERS, check_header, check_timestamp, validate_row)


def audit_file(file_name: str) -> dict:
# List datatypes
    clean: list[dict] = []
    duplicate: list[dict] = []
    suspicious: list[dict] = []
    rejected: list[dict] = []
# Read CSV File
    with open(file_name, "rb") as file:
        raw_data: bytes = file.read()
# Check CSV Encoding
    try:
        text_data: str = raw_data.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text_data: str = raw_data.decode("utf-16")
        except UnicodeDecodeError:
            text_data: str = raw_data.decode("utf-16-be")
    reader = csv.DictReader(text_data.splitlines())
    print("Actual CSV Headers:", reader.fieldnames)
    # Check Header
    check_header([
    column.strip().replace("\ufeff", "")
    for column in reader.fieldnames
    ])
    rows: list[dict] = []
    for row in reader:
        new_row: dict = {}
        for key in HEADERS:
            new_row[key] = row[key].strip()
        rows.append(new_row)
# Step 1: Validate Rows
    valid_rows: list[dict] = []
    for row in rows:
        errors: list[str] = validate_row(row)
        if len(errors) > 0:
            bad_row: dict = row.copy()
            bad_row["reason"] = ", ".join(errors)
            rejected.append(bad_row)
        else:
            valid_rows.append(row.copy())
# Step 2: Find Duplicate Records
    checked: list[dict] = []
    seen_punches: list[dict] = []
    for row in valid_rows:
        current_time: datetime = check_timestamp(row["punch_time"])
        found_duplicate: bool = False
        for old_row in seen_punches:
            old_time: datetime = check_timestamp(old_row["punch_time"])
            same_employee: bool = (row["employee_id"] == old_row["employee_id"])
            same_type: bool = (row["punch_type"] == old_row["punch_type"])
            same_device: bool = (row["device_ip"] == old_row["device_ip"])
            difference: float = abs((current_time - old_time).total_seconds())
            if (
                same_employee
                and same_type
                and same_device
                and difference <= 60
            ):
                found_duplicate = True
                break
        seen_punches.append(row.copy())
        if found_duplicate:
            duplicate.append(row.copy())
        else:
            checked.append(row.copy())
# Step 3: Day Rollover
    for row in checked:
        punch_time: datetime = check_timestamp(row["punch_time"])
        if row["punch_type"] == "OUT" and punch_time.hour < 4:
            previous_date: date = (punch_time.date() - timedelta(days=1))
            row["working_date"] = previous_date.strftime("%Y-%m-%d")
        else:
            row["working_date"] = punch_time.strftime("%Y-%m-%d")
# Step 4: Find Building Switch
    employee_buildings: dict = {}
    for row in checked:
        punch_date: str = row["working_date"]
        key: tuple = (row["employee_id"], punch_date)
        if key not in employee_buildings:
            employee_buildings[key] = set()
        employee_buildings[key].add(row["building_code"])
# Set Comprehension
    suspicious_keys: set = {
        key
        for key, buildings in employee_buildings.items()
        if len(buildings) > 1
    }
# Step 5: Separate Clean and Suspicious
    for row in checked:
        key: tuple = (
            row["employee_id"],
            row["working_date"]
        )
        if key in suspicious_keys:
            suspicious.append(row.copy())
        else:
            clean.append(row.copy())
# Return Dictionary
    result: dict = {
        "total": len(rows),
        "clean": clean,
        "duplicate": duplicate,
        "suspicious": suspicious,
        "rejected": rejected
    }
    return result
