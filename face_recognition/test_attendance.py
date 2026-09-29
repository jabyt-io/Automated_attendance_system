import csv
import os


ATTENDANCE_FILE = "attendance.csv"


if not os.path.exists(ATTENDANCE_FILE):

    print("attendance.csv not found.")
    exit()


records = []


with open(
    ATTENDANCE_FILE,
    "r",
    newline="",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        records.append(row)


# ============================================================
# CHECK DUPLICATE

seen = set()
duplicates = []


for row in records:

    key = (
        row["USN"],
        row["Date"],
        row["Period"]
    )


    if key in seen:

        duplicates.append(key)

    else:

        seen.add(key)


# ============================================================
# RESULT


print()
print("==========================================")
print(" DUPLICATE ATTENDANCE TEST")
print("==========================================")


if len(duplicates) == 0:

    print(
        "PASS: No duplicate attendance records found."
    )

else:

    print(
        f"WARNING: {len(duplicates)} duplicate(s) found."
    )

    for duplicate in duplicates:

        print(duplicate)