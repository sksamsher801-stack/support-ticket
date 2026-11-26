import csv
# Write CSV Report
def write_csv(file_name: str,rows,headers) -> None:

    with open(file_name,"w",newline="",encoding="utf-8") as file:
        writer = csv.DictWriter(file,fieldnames=headers,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
# Employee Summary
# *args = Tuple
# **kwargs = Dictionary
def employee_summary(*groups: list, **names: dict) -> dict:
    summary: dict = {}
    group_names: list[str] = names.get("group_names",["clean", "duplicate", "suspicious", "rejected"])
    for group_name, records in zip(group_names, groups):
        for row in records:
            employee_id: str = row["employee_id"]
            if employee_id not in summary:
                summary[employee_id] = {
                    "clean": 0,
                    "duplicate": 0,
                    "suspicious": 0,
                    "rejected": 0
                }
            summary[employee_id][group_name] += 1
    # Dictionary Comprehension
    summary: dict = {employee: {**counts,"total": sum(counts.values())}
        for employee, counts in summary.items()
    }
    return summary
# Create All Reports
def create_reports(result: dict) -> None:
    clean_headers: list = [
        "employee_id",
        "employee_name",
        "device_ip",
        "punch_type",
        "punch_time",
        "building_code",
        "working_date"
    ]
    rejected_headers: list = [
        "employee_id",
        "employee_name",
        "device_ip",
        "punch_type",
        "punch_time",
        "building_code",
        "reason"
    ]
    write_csv("clean_punches.csv",result["clean"],clean_headers)
    write_csv("rejected_punches.csv",result["rejected"],rejected_headers)
    summary: dict = employee_summary(
        result["clean"],
        result["duplicate"],
        result["suspicious"],
        result["rejected"],
        group_names=[
            "clean",
            "duplicate",
            "suspicious",
            "rejected"
        ]
    )
    with open("audit_summary.txt","w",encoding="utf-8") as file:
        file.write("ATTENDANCE AUDIT SUMMARY\n")
        file.write("========================\n")
        file.write("Total rows: " + str(result["total"]) + "\n")
        file.write("Clean rows: " + str(len(result["clean"])) + "\n")
        file.write("Duplicate count: " +str(len(result["duplicate"])) + "\n")
        file.write("Suspicious count: " +str(len(result["suspicious"])) + "\n")
        file.write("Rejected count: " +str(len(result["rejected"])) + "\n")
        file.write("\nEMPLOYEE WISE SUMMARY\n")
        for employee, counts in summary.items():
            file.write(
                employee
                + " -> Total: " + str(counts["total"])
                + ", Clean: " + str(counts["clean"])
                + ", Duplicate: " + str(counts["duplicate"])
                + ", Suspicious: " + str(counts["suspicious"])
                + ", Rejected: " + str(counts["rejected"])
                + "\n"
            )