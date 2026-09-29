import csv
import os

from student_config import STUDENTS


ATTENDANCE_FILE = "attendance.csv"


if not os.path.exists(ATTENDANCE_FILE):

    print("attendance.csv not found.")
    exit()



# READ DATA


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



# DISPLAY


print()
print("================================================")
print("              PERIOD-WISE ATTENDANCE")
print("================================================")


for student_id, student_name in STUDENTS.items():

    print()
    print(
        f"{student_id} - {student_name}"
    )

    print("-----------------------------------------------")


    student_records = [
        row
        for row in records
        if row["USN"] == student_id
    ]


    if len(student_records) == 0:

        print("No attendance records.")

        continue


    for row in student_records:

        print(
            f"{row['Date']} | "
            f"{row['Period']} | "
            f"{row['Status']}"
        )