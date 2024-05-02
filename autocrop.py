from pytube import YouTube
import cv2
import subprocess
import openai
import numpy as np
import json
import math
import pdb

#Face Detection function
def detect_faces(video_file):
    print("Detecting faces in "+video_file)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("begin Detecting faces in "+video_file)

    # Load the video
    cap = cv2.VideoCapture(video_file)

    faces = []

    # Detect and store unique faces
    while len(faces) < 5:
        ret, frame = cap.read()
        #print(ret, frame)
        if ret:
            print("Found")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Iterate through the detected faces
            for face in detected_faces:
                # Check if the face is already in the list of faces
                if not any(np.array_equal(face, f) for f in faces):
                    faces.append(face)
                    print("Face found")

            # Print the number of unique faces detected so far
            print(f"Number of unique faces detected: {len(faces)}")

    # Release the video capture object
    cap.release()

    # If faces detected, return the list of faces
    if len(faces) > 0:
        return faces

    # If no faces detected, return None
    return None




#Crop Video function
import cv2


import cv2

def crop_video(faces, input_file, output_file):
    try:
        if len(faces) > 0:
            # Constants for cropping
            CROP_RATIO = 0.9  # Adjust the ratio to control how much of the face is visible in the cropped video
            VERTICAL_RATIO = 9 / 16  # Aspect ratio for the vertical video

            # Read the input video
            cap = cv2.VideoCapture(input_file)

            # Get the frame dimensions
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Calculate the target width and height for cropping (vertical format)
            target_height = int(frame_height * CROP_RATIO)
            target_width = int(target_height * VERTICAL_RATIO)

            # Create a VideoWriter object to save the output video
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_video = cv2.VideoWriter(output_file, fourcc, 30.0, (target_width, target_height))

            # Loop through each frame of the input video
            while True:
                ret, frame = cap.read()

                # If no more frames, break out of the loop
                if not ret:
                    break

                # Iterate through each detected face
                for face in faces:
                    # Unpack the face coordinates
                    x, y, w, h = face

                    # Calculate the crop coordinates
                    crop_x = max(0, x + (w - target_width) // 2)  # Adjust the crop region to center the face
                    crop_y = max(0, y + (h - target_height) // 2)
                    crop_x2 = min(crop_x + target_width, frame_width)
                    crop_y2 = min(crop_y + target_height, frame_height)

                    # Crop the frame based on the calculated crop coordinates
                    cropped_frame = frame[crop_y:crop_y2, crop_x:crop_x2]

                    # Resize the cropped frame to the target dimensions
                    resized_frame = cv2.resize(cropped_frame, (target_width, target_height))

                    # Write the resized frame to the output video
                    output_video.write(resized_frame)

            # Release the input and output video objects
            cap.release()
            output_video.release()

            print("Video cropped successfully.")
        else:
            print("No faces detected in the video.")
    except Exception as e:
        print(f"Error during video cropping: {str(e)}")


def crop_video2(faces, input_file, output_file):
    try:
        if len(faces) > 0:
            # Constants for cropping
            CROP_RATIO = 0.9  # Adjust the ratio to control how much of the face is visible in the cropped video
            VERTICAL_RATIO = 9 / 16  # Aspect ratio for the vertical video
            BATCH_DURATION = 5  # Duration of each batch in seconds

            # Read the input video
            cap = cv2.VideoCapture(input_file)

            # Get the frame dimensions
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Calculate the target width and height for cropping (vertical format)
            target_height = int(frame_height * CROP_RATIO)
            target_width = int(target_height * VERTICAL_RATIO)

            # Calculate the number of frames per batch
            frames_per_batch = int(cap.get(cv2.CAP_PROP_FPS) * BATCH_DURATION)

            # Create a VideoWriter object to save the output video
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_video = cv2.VideoWriter(output_file, fourcc, 30.0, (target_width, target_height))

            # Loop through each batch of frames
            while True:
                ret, frame = cap.read()

                # If no more frames, break out of the loop
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert frame to BGR color format
                # Iterate through each detected face
                for face in faces:
                    # Unpack the face coordinates
                    x, y, w, h = face

                    # Calculate the crop coordinates
                    crop_x = max(0, x + (w - target_width) // 2)  # Adjust the crop region to center the face
                    crop_y = max(0, y + (h - target_height) // 2)
                    crop_x2 = min(crop_x + target_width, frame_width)
                    crop_y2 = min(crop_y + target_height, frame_height)

                    # Crop the frame based on the calculated crop coordinates
                    cropped_frame = frame[crop_y:crop_y2, crop_x:crop_x2]

                    # Resize the cropped frame to the target dimensions
                    resized_frame = cv2.resize(cropped_frame, (target_width, target_height))

                    # Write the resized frame to the output video
                    output_video.write(resized_frame)

                    # Check if the current frame index is divisible by frames_per_batch
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) % frames_per_batch == 0:
                        # Analyze the lip movement or facial muscle activity within the batch
                        is_talking = is_talking_in_batch(resized_frame)

                        # Adjust the focus based on the speaking activity
                        adjust_focus(is_talking)

            # Release the input and output video objects
            cap.release()
            output_video.release()

            print("Video cropped successfully.")
        else:
            print("No faces detected in the video.")
    except Exception as e:
        print(f"Error during video cropping: {str(e)}")

def is_talking_in_batch(frames):
    # Calculate the motion between consecutive frames
    motion_scores = []
    for i in range(len(frames) - 1):
        frame1 = frames[i]
        frame2 = frames[i+1]
        motion_score = calculate_motion_score(frame1, frame2)  # Replace with your motion analysis function
        motion_scores.append(motion_score)

    # Determine if talking behavior is present based on motion scores
    threshold = 0.5  # Adjust the threshold as needed
    talking = any(score > threshold for score in motion_scores)

    return talking

def calculate_motion_score(frame1, frame2):
    # Convert frames to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Calculate dense optical flow
    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate magnitude of optical flow vectors
    magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)

    # Calculate motion score as the average magnitude of optical flow vectors
    motion_score = np.mean(magnitude)

    return motion_score

def adjust_focus(frame, talking):
    if talking:
        # Apply visual effects or adjustments to emphasize the speaker
        # For example, you can add a bounding box or overlay text on the frame
        # indicating the speaker is talking
        # You can also experiment with resizing or positioning the frame to
        # focus on the talking person

        # Example: Draw a bounding box around the face region
        face_coordinates = get_face_coordinates(frame)  # Replace with your face detection logic

        if face_coordinates is not None:
            x, y, w, h = face_coordinates
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame
def get_face_coordinates(frame):
    # Load the pre-trained Haar cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Return the coordinates of the first detected face
        x, y, w, h = faces[0]
        return x, y, w, h

    # If no face detected, return None
    return None