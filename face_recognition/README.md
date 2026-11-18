# Face Encoding and Recognition Module

## Overview
This module provides:
- Student face encoding
- Face recognition using stored encodings
- Multi-frame identity verification
- Experimental face liveness detection

## Requirements
Use Python 3.11 and install dependencies from the repository root:

    pip install -r face_recognition/requirements.txt

## Dataset Setup
Create a dataset folder inside face_recognition. Organize authorized student images by student ID:

    face_recognition/
        dataset/
            STUDENT_ID/
                image1.jpg

Do not upload student photographs or biometric encodings to GitHub.

## Face Encoding
From the face_recognition directory, run:

    python encode_faces.py

## Face Recognition
From the face_recognition directory, run:

    python recognize_faces.py

The current recognition implementation supports one face at a time. Simultaneous multi-student classroom recognition requires further integration.

## Multi-frame Verification
The verification module checks repeated recognition results across multiple frames before confirming a student identity.

## Liveness Detection
The liveness module uses the MiniFASNetV2 ONNX model.

The model is not included in this repository. Verify its source and license before using or redistributing it.

Set the model path using the ATTENDANCE_LIVENESS_MODEL environment variable before running the application. For example, in PowerShell:

    $env:ATTENDANCE_LIVENESS_MODEL = "C:\path\to\MiniFASNetV2.onnx"

IMPORTANT: Liveness detection is experimental. The model's preprocessing requirements and REAL/SPOOF output class mapping have not yet been independently verified. Do not treat its output as a validated anti-spoofing guarantee.

## Integration
The recognition module should receive video frames and face locations from the shared detection component. It should return a recognized student ID or an unknown result.

Coordinate the function interfaces with the detection and attendance backend teammates before full integration. Attendance should only be recorded after the required identity and liveness checks pass.

## Privacy and Safety
- Keep student photographs and generated face encodings private.
- Do not commit attendance records or virtual environments.
- Do not commit ONNX model files.
- Use authorized student images and protect biometric data.
