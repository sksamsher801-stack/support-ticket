import time
from audit import audit_file
from reports import create_reports
# Decorator
def show_time(function):
    def wrapper(*args, **kwargs):
        start: float = time.time()
        result = function(*args, **kwargs)
        end: float = time.time()
        execution_time: float = end - start
        print("Execution Time:",round(execution_time, 4),"seconds")
        return result
    return wrapper

@show_time
def main() -> None:
    result: dict = audit_file("raw_punches.csv")
    create_reports(result)
    print("\nAudit Completed Successfully!")
    print("Total Rows:", result["total"])
    print("Clean:", len(result["clean"]))
    print("Duplicate:", len(result["duplicate"]))
    print("Suspicious:", len(result["suspicious"]))
    print("Rejected:", len(result["rejected"]))

if __name__ == "__main__":
        main()