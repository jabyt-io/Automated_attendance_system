import cv2
import face_recognition
import pickle
import os
import csv

from datetime import datetime

from liveness_detection import (
    LivenessDetector,
    LivenessVote
)

from multi_frame_verification import (
    MultiFrameVerifier
)


# ==========================================
# 1. STUDENT DETAILS
# ==========================================

STUDENTS = [
    "4AL24CD037",
    "4AL24CD038",
    "4AL24CD039",
    "4AL24CD040"
]


# ==========================================
# 2. CLASS TIMETABLE
# ==========================================

CLASS_PERIODS = [

    ("Class 1", "09:00", "09:50"),

    ("Class 2", "09:50", "10:40"),

    ("Class 3", "11:00", "11:50"),

    ("Class 4", "11:50", "12:40"),

    ("Class 5", "13:40", "14:30"),

    ("Class 6", "14:30", "15:20"),

    ("Class 7", "15:20", "16:20")

]


# ==========================================
# 3. SETTINGS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENCODINGS_FILE = os.path.join(
    BASE_DIR, "encodings.pkl"
)

ATTENDANCE_FILE = os.path.join(
    BASE_DIR, "attendance.csv"
)

TOLERANCE = 0.55

UPSAMPLE_TIMES = 2

CAMERA_INDEX = 0


# ==========================================
# 4. LOAD FACE ENCODINGS
# ==========================================

print("Loading face encodings...")

if not os.path.exists(ENCODINGS_FILE):
    raise FileNotFoundError(
        "encodings.pkl not found!"
    )

with open(ENCODINGS_FILE, "rb") as file:

    data = pickle.load(file)

known_encodings = data["encodings"]

known_student_ids = data["student_ids"]

if len(known_encodings) != len(known_student_ids):
    raise ValueError(
        "Encoding and student ID counts do not match."
    )

print("Face encodings loaded successfully!")

print("Total encodings:", len(known_encodings))


# ==========================================
# 5. INITIALIZE LIVENESS AND VERIFICATION
# ==========================================

print("Loading liveness detection model...")

liveness_detector = LivenessDetector()

identity_verifier = MultiFrameVerifier(
    required_matches=5,
    window_size=7
)

liveness_votes = {
    student_id: LivenessVote()
    for student_id in STUDENTS
}

print("Verification systems initialized!")


# ==========================================
# 6. CREATE ATTENDANCE CSV
# ==========================================

CSV_HEADERS = [
    "USN",
    "Date",
    "Period",
    "Start_Time",
    "End_Time",
    "Marked_Time",
    "Status"
]


if not os.path.exists(ATTENDANCE_FILE):

    with open(
        ATTENDANCE_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(CSV_HEADERS)


# ==========================================
# 7. GET CURRENT CLASS
# ==========================================

def get_current_class():

    current_time = datetime.now().strftime("%H:%M")

    for period in CLASS_PERIODS:

        name, start, end = period

        if start <= current_time < end:

            return period

    return None


# ==========================================
# 8. CHECK DUPLICATE ATTENDANCE
# ==========================================

def attendance_exists(student_id, date, period_name):

    if not os.path.exists(ATTENDANCE_FILE):
        return False

    with open(
        ATTENDANCE_FILE,
        "r",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["USN"] == student_id
                and row["Date"] == date
                and row["Period"] == period_name
            ):

                return True

    return False


# ==========================================
# 9. MARK PRESENT
# ==========================================

def mark_present(student_id, period):

    period_name, start, end = period

    current_date = datetime.now().strftime("%Y-%m-%d")

    current_time = datetime.now().strftime("%H:%M:%S")

    if attendance_exists(
        student_id,
        current_date,
        period_name
    ):

        print(
            f"{student_id} attendance already marked."
        )

        return

    with open(
        ATTENDANCE_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            student_id,
            current_date,
            period_name,
            start,
            end,
            current_time,
            "Present"
        ])

    print(
        f"Attendance marked PRESENT for {student_id}"
    )


# ==========================================
# 10. MARK ABSENT STUDENTS
# ==========================================

def mark_absent_students(period, detected_students):

    period_name, start, end = period

    current_date = datetime.now().strftime("%Y-%m-%d")

    current_time = datetime.now().strftime("%H:%M:%S")

    for student_id in STUDENTS:

        if student_id in detected_students:
            continue

        if attendance_exists(
            student_id,
            current_date,
            period_name
        ):
            continue

        with open(
            ATTENDANCE_FILE,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                student_id,
                current_date,
                period_name,
                start,
                end,
                current_time,
                "Absent"
            ])

        print(
            f"Attendance marked ABSENT for {student_id}"
        )


# ==========================================
# 11. RESET VERIFICATION
# ==========================================

def reset_verification():

    identity_verifier.reset()

    for vote in liveness_votes.values():

        vote.reset()


# ==========================================
# 12. FACE RECOGNITION
# ==========================================

def recognize_student(rgb_frame, face_location):

    encodings = face_recognition.face_encodings(
        rgb_frame,
        [face_location]
    )

    if not encodings:
        return "Unknown"

    face_encoding = encodings[0]

    distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    if len(distances) == 0:
        return "Unknown"

    best_match_index = distances.argmin()

    best_distance = distances[best_match_index]

    if best_distance <= TOLERANCE:

        return known_student_ids[best_match_index]

    return "Unknown"


# ==========================================
# 13. MAIN WEBCAM SYSTEM
# ==========================================

def main():

    print("\nStarting Automated Attendance System...")

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():

        print("ERROR: Cannot open webcam.")

        return

    detected_students = set()

    previous_period = None

    print("\nCamera started successfully!")

    print("Press Q to quit.")

    try:

        while True:

            ret, frame = camera.read()

            if not ret:

                print("Unable to read camera frame.")

                break

            current_period = get_current_class()

            # ----------------------------------
            # PERIOD CHANGE DETECTION
            # ----------------------------------

            if current_period != previous_period:

                if previous_period is not None:

                    print(
                        "\nClosing:",
                        previous_period[0]
                    )

                    mark_absent_students(
                        previous_period,
                        detected_students
                    )

                    reset_verification()

                    detected_students.clear()

                previous_period = current_period

                if current_period is not None:

                    print(
                        "\nStarting:",
                        current_period[0]
                    )

            # ----------------------------------
            # DISPLAY CLASS INFORMATION
            # ----------------------------------

            if current_period is None:

                cv2.putText(
                    frame,
                    "BREAK / OUTSIDE CLASS HOURS",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 165, 255),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    current_period[0],
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

            # ----------------------------------
            # FACE DETECTION
            # ----------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            face_locations = face_recognition.face_locations(
                rgb_frame,
                number_of_times_to_upsample=UPSAMPLE_TIMES,
                model="hog"
            )

            frame_seen = set()

            # ----------------------------------
            # SINGLE STUDENT TEST MODE
            # ----------------------------------

            if len(face_locations) > 1:

                cv2.putText(
                    frame,
                    "MULTIPLE FACES: TEST ONE STUDENT AT A TIME",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2
                )

                reset_verification()

            elif len(face_locations) == 1:

                face_location = face_locations[0]

                top, right, bottom, left = face_location

                student_id = recognize_student(
                    rgb_frame,
                    face_location
                )

                # ----------------------------------
                # UNKNOWN STUDENT
                # ----------------------------------

                if student_id == "Unknown":

                    reset_verification()

                    label = "UNKNOWN STUDENT"

                    color = (0, 0, 255)

                else:

                    frame_seen.add(student_id)

                    # ----------------------------------
                    # LIVENESS DETECTION
                    # ----------------------------------

                    prediction = liveness_detector.predict(
                        frame,
                        (left, top, right, bottom)
                    )

                    live_status = liveness_votes[
                        student_id
                    ].update(prediction)

                    if live_status == "REAL":

                        confirmed_id = identity_verifier.update(
                            student_id
                        )

                        if confirmed_id is not None:

                            label = (
                                confirmed_id + " - VERIFIED"
                            )

                            color = (0, 255, 0)

                            if current_period is not None:

                                mark_present(
                                    confirmed_id,
                                    current_period
                                )

                                detected_students.add(
                                    confirmed_id
                                )

                        else:

                            label = (
                                student_id + " - VERIFYING"
                            )

                            color = (0, 255, 255)

                    elif live_status == "SPOOF":

                        identity_verifier.reset(
                            student_id
                        )

                        label = "POSSIBLE SPOOF"

                        color = (0, 0, 255)

                    else:

                        label = (
                            student_id + " - CHECKING LIVENESS"
                        )

                        color = (0, 165, 255)

                # ----------------------------------
                # DRAW FACE RECTANGLE
                # ----------------------------------

                cv2.rectangle(
                    frame,
                    (left, top),
                    (right, bottom),
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    label,
                    (left, max(25, top - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

            else:

                # No face detected: clear old test history.
                reset_verification()

                cv2.putText(
                    frame,
                    "NO FACE DETECTED",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 165, 255),
                    2
                )

            # ----------------------------------
            # RESET IF RECOGNIZED STUDENT
            # IS NO LONGER VISIBLE
            # ----------------------------------

            if len(face_locations) == 1:

                for student_id in STUDENTS:

                    if student_id not in frame_seen:

                        identity_verifier.reset(
                            student_id
                        )

                        liveness_votes[
                            student_id
                        ].reset()

            # ----------------------------------
            # DISPLAY ATTENDANCE COUNT
            # ----------------------------------

            cv2.putText(
                frame,
                "Present: " + str(len(detected_students)),
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Automated Student Attendance System",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                print("\nCamera stopped by user.")

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        print("Webcam released.")

    # Do not mark students absent just because the user
    # pressed Q before the class period ended.


# ==========================================
# 14. RUN PROGRAM
# ==========================================

if __name__ == "__main__":

    main()