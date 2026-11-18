import cv2
import os
import numpy as np
import onnxruntime as ort

from pathlib import Path
from collections import deque
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(
    os.environ.get(
        "ATTENDANCE_LIVENESS_MODEL",
        BASE_DIR / "models" / "MiniFASNetV2.onnx"
    )
)



CROP_SCALE = 2.7

REAL_THRESHOLD = 0.80
SPOOF_THRESHOLD = 0.80

VOTE_WINDOW = 5
REQUIRED_VOTES = 4
MIN_VOTE_FRAMES = 5


class LivenessDetector:

    def __init__(self, model_path=MODEL_PATH):

        if not Path(model_path).is_file():
            raise FileNotFoundError(
                f"Liveness model not found: {model_path}"
            )

        self.session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"]
        )

        model_input = self.session.get_inputs()[0]
        model_output = self.session.get_outputs()[0]

        self.input_name = model_input.name
        self.output_name = model_output.name

        shape = model_input.shape

        if len(shape) != 4:
            raise ValueError(
                f"Unexpected model input shape: {shape}"
            )

        if shape[2] != 80 or shape[3] != 80:
            raise ValueError(
                f"Expected 80x80 model input, received {shape}"
            )

        print("MiniFASNetV2 loaded successfully!")

    def crop_face(self, frame, bbox):

        x1, y1, x2, y2 = map(float, bbox)

        height, width = frame.shape[:2]

        box_width = x2 - x1
        box_height = y2 - y1

        if box_width <= 1 or box_height <= 1:
            return None

        scale = min(
            (height - 1) / box_height,
            (width - 1) / box_width,
            CROP_SCALE
        )

        new_width = box_width * scale
        new_height = box_height * scale

        center_x = x1 + box_width / 2
        center_y = y1 + box_height / 2

        cx1 = max(
            0, int(center_x - new_width / 2)
        )

        cy1 = max(
            0, int(center_y - new_height / 2)
        )

        cx2 = min(
            width - 1,
            int(center_x + new_width / 2)
        )

        cy2 = min(
            height - 1,
            int(center_y + new_height / 2)
        )

        if cx2 <= cx1 or cy2 <= cy1:
            return None

        face = frame[cy1:cy2 + 1, cx1:cx2 + 1]

        if face.size == 0:
            return None

        return cv2.resize(face, (80, 80))

    def preprocess(self, face):

        face = face.astype(np.float32)

        face = np.transpose(face, (2, 0, 1))

        face = np.expand_dims(face, axis=0)

        return np.ascontiguousarray(face)

    @staticmethod
    def softmax(logits):

        shifted = logits - np.max(
            logits, axis=1, keepdims=True
        )

        exp_values = np.exp(shifted)

        return exp_values / np.sum(
            exp_values, axis=1, keepdims=True
        )

    def predict(self, frame, bbox):

        face = self.crop_face(frame, bbox)

        if face is None:
            return {
                "status": "UNCERTAIN",
                "confidence": 0.0,
                "live_score": 0.0,
                "spoof_score": 0.0
            }

        tensor = self.preprocess(face)

        outputs = self.session.run(
            [self.output_name],
            {self.input_name: tensor}
        )

        logits = outputs[0]

        if logits.ndim != 2 or logits.shape[1] != 3:
            raise ValueError(
                f"Unexpected model output shape: {logits.shape}"
            )

        probabilities = self.softmax(logits)[0]

        predicted_class = int(np.argmax(probabilities))

        confidence = float(
            probabilities[predicted_class]
        )

        # Assumption: class 1 represents REAL.
        live_score = float(probabilities[1])

        spoof_score = float(
            max(probabilities[0], probabilities[2])
        )

        if (
            predicted_class == 1
            and confidence >= REAL_THRESHOLD
        ):
            status = "REAL"

        elif (
            predicted_class != 1
            and confidence >= SPOOF_THRESHOLD
        ):
            status = "SPOOF"

        else:
            status = "UNCERTAIN"

        return {
            "status": status,
            "confidence": confidence,
            "live_score": live_score,
            "spoof_score": spoof_score
        }


class LivenessVote:

    def __init__(self):

        self.history = deque(maxlen=VOTE_WINDOW)

    def update(self, prediction):

        self.history.append(prediction)

        real_votes = [
            item["confidence"]
            for item in self.history
            if item["status"] == "REAL"
        ]

        spoof_votes = [
            item["confidence"]
            for item in self.history
            if item["status"] == "SPOOF"
        ]

        if len(self.history) < MIN_VOTE_FRAMES:
            return "UNCERTAIN"

        if (
            len(real_votes) >= REQUIRED_VOTES
            and np.mean(real_votes) >= REAL_THRESHOLD
        ):
            return "REAL"

        if (
            len(spoof_votes) >= REQUIRED_VOTES
            and np.mean(spoof_votes) >= SPOOF_THRESHOLD
        ):
            return "SPOOF"

        return "UNCERTAIN"

    def reset(self):

        self.history.clear()