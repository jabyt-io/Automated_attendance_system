import cv2
import face_recognition
import pickle
import os
import csv
from datetime import datetime


# ============================================================
# STUDENT USNs

STUDENTS = [
    "4AL24CD037",
    "4AL24CD038",
    "4AL24CD039",
    "4AL24CD040"
]


# ============================================================
# CLASS TIMETABLE


CLASS_PERIODS = [
    ("Class 1", "09:00", "09:50"),
    ("Class 2", "09:50", "10:40"),
    ("Class 3", "11:00", "11:50"),
    ("Class 4", "11:50", "12:40"),
    ("Class 5", "13:40", "14:30"),
    ("Class 6", "14:30", "15:20"),
    ("Class 7", "15:20", "16:20"),
]


# ============================================================
# FACE RECOGNITION SETTINGS

TOLERANCE = 0.55

# Helps detect faces that are smaller/farther away.
# Higher values = slower processing.
UPSAMPLE_TIMES = 2


# ============================================================
# FILE NAMES

ENCODINGS_FILE = "encodings.pkl"
ATTENDANCE_FILE = "attendance.csv"


# ============================================================
# LOAD FACE ENCODINGS

if not os.path.exists(ENCODINGS_FILE):

    print("ERROR: encodings.pkl was not found.")
    print("Please run encode_faces.py first.")

    input("Press Enter to exit...")
    exit()


with open(ENCODINGS_FILE, "rb") as file:

    data = pickle.load(file)


known_encodings = data["encodings"]
known_student_ids = data["student_ids"]


print()
print("==========================================")
print(" AUTOMATED STUDENT ATTENDANCE SYSTEM")
print("==========================================")
print(f"Loaded face encodings : {len(known_encodings)}")
print(f"Registered students   : {len(STUDENTS)}")
print("==========================================")
print()


# ============================================================
# CREATE ATTENDANCE CSV

if not os.path.exists(ATTENDANCE_FILE):

    with open(
        ATTENDANCE_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "USN",
            "Date",
            "Period",
            "Start_Time",
            "End_Time",
            "Marked_Time",
            "Status"
        ])


# ============================================================
# GET CURRENT CLASS


def get_current_class():

    current_time = datetime.now().strftime("%H:%M")

    for period_name, start_time, end_time in CLASS_PERIODS:

        if start_time <= current_time < end_time:

            return (
                period_name,
                start_time,
                end_time
            )

    return None


# ============================================================
# CHECK WHETHER ATTENDANCE ALREADY EXISTS


def attendance_exists(
    student_id,
    current_date,
    period_name
):

    if not os.path.exists(ATTENDANCE_FILE):

        return False


    with open(
        ATTENDANCE_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["USN"] == student_id
                and row["Date"] == current_date
                and row["Period"] == period_name
            ):

                return True


    return False


# ============================================================
# MARK STUDENT PRESENT


def mark_present(
    student_id,
    period_name,
    start_time,
    end_time
):

    now = datetime.now()

    current_date = now.strftime("%Y-%m-%d")
    marked_time = now.strftime("%H:%M:%S")


    # Prevent duplicate attendance
    if attendance_exists(
        student_id,
        current_date,
        period_name
    ):

        return


    with open(
        ATTENDANCE_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            student_id,
            current_date,
            period_name,
            start_time,
            end_time,
            marked_time,
            "Present"
        ])


    print(
        f" PRESENT | {student_id} | "
        f"{period_name} | {marked_time}"
    )


# ============================================================
# MARK ABSENT STUDENTS

def mark_absent_students(
    period_name,
    start_time,
    end_time,
    detected_students
):

    current_date = datetime.now().strftime("%Y-%m-%d")


    for student_id in STUDENTS:

        # Student was detected during this period
        if student_id in detected_students:

            continue


        # Do not create duplicate records
        if attendance_exists(
            student_id,
            current_date,
            period_name
        ):

            continue


        with open(
            ATTENDANCE_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                student_id,
                current_date,
                period_name,
                start_time,
                end_time,
                end_time,
                "Absent"
            ])


        print(
            f" ABSENT  | {student_id} | "
            f"{period_name}"
        )


# ============================================================
# OPEN CAMERA


camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Could not open the camera.")

    input("Press Enter to exit...")

    exit()


# ============================================================
# VARIABLES


current_period = None

detected_students = set()


# ============================================================
# MAIN LOOP


while True:

    success, frame = camera.read()


    if not success:

        print("ERROR: Could not read camera frame.")

        break


    # --------------------------------------------------------
    # CURRENT DATE AND TIME
    

    now = datetime.now()

    current_date = now.strftime("%Y-%m-%d")

    current_time = now.strftime("%H:%M:%S")

    current_time_short = now.strftime("%H:%M")


    # --------------------------------------------------------
    # GET CURRENT CLASS
    

    class_info = get_current_class()


    # ========================================================
    # AFTER 4:20 PM - CLASS ENDS

    if current_time_short >= "16:20":

        # Finalize Class 7 if necessary
        if current_period is not None:

            previous_period_name = current_period[0]

            previous_start_time = current_period[1]

            previous_end_time = current_period[2]


            mark_absent_students(
                previous_period_name,
                previous_start_time,
                previous_end_time,
                detected_students
            )


            current_period = None

            detected_students = set()


        # ----------------------------------------------------
        # DISPLAY CLASS ENDS
        

        cv2.putText(
            frame,
            "CLASS ENDS",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )


        cv2.putText(
            frame,
            "All classes completed for today",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Date: {current_date}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Time: {current_time}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            "Attendance is closed",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


    # ========================================================
    # CLASS IS CURRENTLY RUNNING

    elif class_info is not None:

        period_name = class_info[0]

        start_time = class_info[1]

        end_time = class_info[2]


        # ----------------------------------------------------
        # NEW PERIOD STARTED
        

        if (
            current_period is None
            or current_period[0] != period_name
        ):


            # Finalize previous period
            if current_period is not None:

                previous_period_name = current_period[0]

                previous_start_time = current_period[1]

                previous_end_time = current_period[2]


                mark_absent_students(
                    previous_period_name,
                    previous_start_time,
                    previous_end_time,
                    detected_students
                )


            # Start new period
            current_period = (
                period_name,
                start_time,
                end_time
            )


            detected_students = set()


            print()
            print("==========================================")
            print(f"STARTED : {period_name}")
            print(f"TIME    : {start_time} - {end_time}")
            print("==========================================")


        # ----------------------------------------------------
        # DISPLAY CLASS INFORMATION
        # 

        cv2.putText(
            frame,
            period_name,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )


        cv2.putText(
            frame,
            f"Current Time: {current_time}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Class Time: {start_time} - {end_time}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Date: {current_date}",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # ====================================================
        # FACE DETECTION
    

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        face_locations = face_recognition.face_locations(
            rgb_frame,
            number_of_times_to_upsample=UPSAMPLE_TIMES,
            model="hog"
        )


        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )


        # ====================================================
        # RECOGNIZE FACES
        

        for face_location, face_encoding in zip(
            face_locations,
            face_encodings
        ):


            # ------------------------------------------------
            # COMPARE WITH KNOWN FACES
            

            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=TOLERANCE
            )


            face_distances = face_recognition.face_distance(
                known_encodings,
                face_encoding
            )


            name = "Unknown"


            # ------------------------------------------------
            # FIND BEST MATCH
            

            if len(face_distances) > 0:

                best_match_index = face_distances.argmin()

                best_distance = face_distances[
                    best_match_index
                ]


                if (
                    matches[best_match_index]
                    and known_student_ids[
                        best_match_index
                    ] in STUDENTS
                ):

                    name = known_student_ids[
                        best_match_index
                    ]


            # ------------------------------------------------
            # FACE COORDINATES
            

            top, right, bottom, left = face_location


            # ------------------------------------------------
            # REGISTER STUDENT
            

            if name != "Unknown":

                detected_students.add(name)


                mark_present(
                    name,
                    period_name,
                    start_time,
                    end_time
                )


            # ------------------------------------------------
            # DISPLAY NAME
            

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )


            cv2.rectangle(
                frame,
                (left, bottom - 35),
                (right, bottom),
                (0, 255, 0),
                cv2.FILLED
            )


            cv2.putText(
                frame,
                name,
                (left + 6, bottom - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )


    # ========================================================
    # BREAK / LUNCH
    

    else:

        # ----------------------------------------------------
        # FINISH PREVIOUS PERIOD
    

        if current_period is not None:

            previous_period_name = current_period[0]

            previous_start_time = current_period[1]

            previous_end_time = current_period[2]


            mark_absent_students(
                previous_period_name,
                previous_start_time,
                previous_end_time,
                detected_students
            )


            current_period = None

            detected_students = set()


        # ----------------------------------------------------
        # DETERMINE BREAK TYPE
        

        if (
            "10:40" <= current_time_short < "11:00"
        ):

            break_message = "MORNING BREAK"


        elif (
            "12:40" <= current_time_short < "13:40"
        ):

            break_message = "LUNCH BREAK"


        else:

            break_message = "NO CLASS"


        # ----------------------------------------------------
        # DISPLAY BREAK
        

        cv2.putText(
            frame,
            break_message,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 255),
            3
        )


        cv2.putText(
            frame,
            f"Current Time: {current_time}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Date: {current_date}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            "Attendance is not recorded",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


    # ========================================================
    # SHOW CAMERA WINDOW
    

    cv2.imshow(
        "Automated Student Attendance System",
        frame
    )


    # ========================================================
    # QUIT WITH Q
    

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        print()
        print("Stopping attendance system...")

        break


# ============================================================
# CLOSE CAMERA


camera.release()

cv2.destroyAllWindows()


print()
print("==========================================")
print(" Attendance System Stopped")
print("==========================================")
print(f"Attendance file: {ATTENDANCE_FILE}")
print()