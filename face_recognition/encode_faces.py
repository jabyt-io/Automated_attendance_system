import os
import cv2
import pickle
import face_recognition

from student_config import STUDENTS

# SETTINGS

DATASET_PATH = "dataset"
ENCODINGS_FILE = "encodings.pkl"

# Number of times the image is upsampled during face detection
UPSAMPLE_TIMES = 1

# STORAGE

known_encodings = []
known_student_ids = []


# PROCESS STUDENT FOLDERS

for student_id in STUDENTS:

    student_folder = os.path.join(
        DATASET_PATH,
        student_id
    )

    if not os.path.isdir(student_folder):

        print(
            f"WARNING: Folder not found: "
            f"{student_folder}"
        )

        continue

    print()
    print("------------------------------------------")
    print(f"Processing: {student_id}")
    print(f"Name      : {STUDENTS[student_id]}")
    print("------------------------------------------")


    # PROCESS IMAGES

    for image_name in os.listdir(student_folder):

        image_path = os.path.join(
            student_folder,
            image_name
        )

        image = cv2.imread(image_path)

        if image is None:

            print(
                f"Could not read: {image_name}"
            )

            continue


        # Convert BGR to RGB

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )


        # Find faces
    

        face_locations = face_recognition.face_locations(
            rgb_image,
            number_of_times_to_upsample=UPSAMPLE_TIMES,
            model="hog"
        )

        # No face

        if len(face_locations) == 0:

            print(
                f"No face found: {image_name}"
            )

            continue


        # Multiple faces
        

        if len(face_locations) > 1:

            print(
                f"Multiple faces found: {image_name}"
            )

            continue

        # Generate encoding

        encodings = face_recognition.face_encodings(
            rgb_image,
            face_locations
        )

        if len(encodings) == 0:

            print(
                f"Encoding failed: {image_name}"
            )

            continue


        encoding = encodings[0]


        
        # Store encoding
        

        known_encodings.append(encoding)

        known_student_ids.append(student_id)

        print(
            f"Encoded: {image_name}"
        )



# SAVE ENCODINGS


data = {
    "encodings": known_encodings,
    "student_ids": known_student_ids
}


with open(
    ENCODINGS_FILE,
    "wb"
) as file:

    pickle.dump(
        data,
        file
    )


# FINAL RESULT

print()
print("==========================================")
print(" FACE ENCODING COMPLETED")
print("==========================================")
print(
    f"Total encodings : "
    f"{len(known_encodings)}"
)
print(
    f"Students        : "
    f"{len(STUDENTS)}"
)
print(
    f"Saved file      : "
    f"{ENCODINGS_FILE}"
)
print("==========================================")