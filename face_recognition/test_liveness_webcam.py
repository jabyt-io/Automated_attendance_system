
import cv2
import face_recognition

from liveness_detection import LivenessDetector, LivenessVote


def main():

    detector = LivenessDetector()
    vote = LivenessVote()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open webcam.")
        return

    print("Liveness webcam test started.")
    print("Show your face to the camera.")
    print("Press Q to exit.")

    try:
        while True:

            success, frame = camera.read()

            if not success:
                print("Could not read webcam frame.")
                break

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            locations = face_recognition.face_locations(
                rgb_frame,
                number_of_times_to_upsample=1,
                model="hog"
            )

            if len(locations) == 1:

                top, right, bottom, left = locations[0]

                bbox = (left, top, right, bottom)

                prediction = detector.predict(
                    frame,
                    bbox
                )

                final_status = vote.update(prediction)

                color = (
                    (0, 255, 0)
                    if final_status == "REAL"
                    else (0, 0, 255)
                    if final_status == "SPOOF"
                    else (0, 255, 255)
                )

                cv2.rectangle(
                    frame,
                    (left, top),
                    (right, bottom),
                    color,
                    2
                )

                text = (
                    f"{final_status} | "
                    f"{prediction['confidence']:.2f}"
                )

                cv2.putText(
                    frame,
                    text,
                    (left, max(25, top - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    color,
                    2
                )

            else:

                vote.reset()

                message = (
                    "NO FACE DETECTED"
                    if len(locations) == 0
                    else "TEST ONE PERSON AT A TIME"
                )

                cv2.putText(
                    frame,
                    message,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

            cv2.imshow(
                "Attendance System - Liveness Test",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
