from email import header
import re
from datetime import datetime
from exception import InvalidHeaderError, InvalidTimestampError

# List datatype
HEADERS: list = [
    "employee_id",
    "employee_name",
    "device_ip",
    "punch_type",
    "punch_time",
    "building_code"
]
# Check CSV Header
def check_header(header: list) -> None:
    if header is None:
        raise InvalidHeaderError("Header not found")
    for column in HEADERS:
        if column not in header:
            raise InvalidHeaderError("Missing column: " + column)
# Validate Employee ID
def check_employee_id(employee_id: str) -> bool:
    pattern: str = r"^E[0-9]{3}$"
    if re.fullmatch(pattern, employee_id):
        return True
    return False
# Validate IP Address
def check_ip(ip: str) -> bool:
    pattern: str = r"^([0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.fullmatch(pattern, ip) is None:
        return False
    parts: list[str] = ip.split(".")
    for part in parts:
        if int(part) > 255:
            return False
    return True
# Validate Timestamp
def check_timestamp(value: str) -> datetime:
    try:
        date_time: datetime = datetime.strptime(value,"%d-%m-%Y %H:%M:%S")
        return date_time
    except ValueError:
        raise InvalidTimestampError("Invalid timestamp: " + value)
# Validate Complete Row
def validate_row(row: dict) -> list[str]:
    errors: list = []
    if not check_employee_id(row["employee_id"]):
        errors.append("Invalid Employee ID")
    if not check_ip(row["device_ip"]):
        errors.append("Invalid Device IP")
    if row["punch_type"] not in ["IN", "OUT"]:
        errors.append("Invalid Punch Type")
    if row["employee_name"] == "":
        errors.append("Employee Name Missing")
    if row["building_code"] == "":
        errors.append("Building Code Missing")
    try:
        check_timestamp(row["punch_time"])
    except InvalidTimestampError as error:
        errors.append(str(error))
    return errors