import cv2
import face_recognition

from student_config import STUDENTS


# ============================================================
# SETTINGS

TOLERANCES = [
    0.45,
    0.50,
    0.55,
    0.60
]


# ============================================================
# LOAD ENCODINGS

import pickle

with open(
    "encodings.pkl",
    "rb"
) as file:

    data = pickle.load(file)


known_encodings = data["encodings"]
known_student_ids = data["student_ids"]


# ============================================================
# CAMERA

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()


print()
print("==========================================")
print(" RECOGNITION TOLERANCE TEST")
print("==========================================")
print("Press Q to quit.")
print()


# ============================================================
# CURRENT TOLERANCE

tolerance_index = 2

TOLERANCE = TOLERANCES[tolerance_index]


# ============================================================
# MAIN LOOP


while True:

    success, frame = camera.read()

    if not success:
        break


    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    face_locations = face_recognition.face_locations(
        rgb_frame,
        number_of_times_to_upsample=2,
        model="hog"
    )


    face_encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )


    for face_location, face_encoding in zip(
        face_locations,
        face_encodings
    ):

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
        distance = None


        if len(face_distances) > 0:

            best_match_index = face_distances.argmin()

            distance = face_distances[
                best_match_index
            ]


            if matches[best_match_index]:

                student_id = known_student_ids[
                    best_match_index
                ]

                name = STUDENTS.get(
                    student_id,
                    student_id
                )


        top, right, bottom, left = face_location


        # ----------------------------------------------------
        # Draw face

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )


        # ----------------------------------------------------
        # Display name

        cv2.putText(
            frame,
            name,
            (left, bottom + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # ----------------------------------------------------
        # Display distance

        if distance is not None:

            cv2.putText(
                frame,
                f"Distance: {distance:.3f}",
                (left, bottom + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )


    # ========================================================
    # Display tolerance

    cv2.putText(
        frame,
        f"Tolerance: {TOLERANCE}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )


    cv2.putText(
        frame,
        "Change tolerance: 1=0.45  2=0.50  3=0.55  4=0.60",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    cv2.imshow(
        "Recognition Testing",
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("1"):
        tolerance_index = 0
        TOLERANCE = TOLERANCES[tolerance_index]

    elif key == ord("2"):
        tolerance_index = 1
        TOLERANCE = TOLERANCES[tolerance_index]

    elif key == ord("3"):
        tolerance_index = 2
        TOLERANCE = TOLERANCES[tolerance_index]

    elif key == ord("4"):
        tolerance_index = 3
        TOLERANCE = TOLERANCES[tolerance_index]

    elif key == ord("q"):
        break


# ============================================================
# CLEANUP

camera.release()
cv2.destroyAllWindows()