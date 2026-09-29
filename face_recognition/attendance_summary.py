import csv
import os

from student_config import STUDENTS


# FILES

ATTENDANCE_FILE = "attendance.csv"
SUMMARY_FILE = "attendance_summary.csv"


# CHECK FILE

if not os.path.exists(ATTENDANCE_FILE):

    print("ERROR: attendance.csv was not found.")

    print(
        "Run recognize_faces.py first."
    )

    input(
        "\nPress Enter to exit..."
    )

    exit()


# READ ATTENDANCE


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


# CALCULATE SUMMARY

summary = []


for student_id, student_name in STUDENTS.items():

    total_classes = 0
    present = 0
    absent = 0


    for row in records:

        if row["USN"] != student_id:
            continue


        total_classes += 1


        if row["Status"] == "Present":

            present += 1

        elif row["Status"] == "Absent":

            absent += 1


    if total_classes > 0:

        percentage = (
            present /
            total_classes
        ) * 100

    else:

        percentage = 0


    summary.append({
        "USN": student_id,
        "Name": student_name,
        "Total": total_classes,
        "Present": present,
        "Absent": absent,
        "Percentage": percentage
    })


# DISPLAY

print()
print("==============================================================")
print("                 ATTENDANCE SUMMARY")
print("==============================================================")

print(
    f"{'USN':<15}"
    f"{'Name':<20}"
    f"{'Total':<8}"
    f"{'Present':<9}"
    f"{'Absent':<8}"
    f"{'Percentage':<12}"
)

print("-" * 72)


for student in summary:

    print(
        f"{student['USN']:<15}"
        f"{student['Name']:<20}"
        f"{student['Total']:<8}"
        f"{student['Present']:<9}"
        f"{student['Absent']:<8}"
        f"{student['Percentage']:.2f}%"
    )


# SAVE CSV

with open(
    SUMMARY_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)


    writer.writerow([
        "USN",
        "Student Name",
        "Total Classes",
        "Present",
        "Absent",
        "Attendance Percentage"
    ])


    for student in summary:

        writer.writerow([
            student["USN"],
            student["Name"],
            student["Total"],
            student["Present"],
            student["Absent"],
            f"{student['Percentage']:.2f}"
        ])


print()
print(
    "Summary saved as:",
    SUMMARY_FILE
)

print()