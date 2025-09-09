import os
import cv2
import numpy as np
import datetime
from Dashboard.models import Attendance
from video_capture.pc_camera import laptop_frame_generator
from video_capture.mobile_camera import mobile_frame_generator
from ultralytics import YOLO

# YOLOv8 Face Detection Model
model = YOLO("yolov8n.pt")  # Ensure you have the trained model

# Define the directory to store known face images.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")

# Global lists for known face images and names.
known_face_images = {}
known_face_names = []

# Dictionary to throttle attendance logging (log once per 60 seconds per face).
last_logged = {}

def refresh_known_faces():
    """
    Loads known face images from the KNOWN_FACES_DIR directory.
    Uses filename as the person's name.
    """
    global known_face_images, known_face_names
    known_face_images.clear()
    known_face_names.clear()

    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(KNOWN_FACES_DIR, filename)
            image = cv2.imread(file_path)
            if image is not None:
                name = os.path.splitext(filename)[0]
                known_face_images[name] = image
                known_face_names.append(name)

# Load the known faces on module import.
refresh_known_faces()

def match_face(detected_face):
    """
    Compares the detected face with known face images using ORB feature matching.
    Returns the matched person's name or 'Unknown'.
    """
    orb = cv2.ORB_create()

    detected_keypoints, detected_descriptors = orb.detectAndCompute(detected_face, None)

    best_match = ("Unknown", float("inf"))

    for name, known_face in known_face_images.items():
        known_keypoints, known_descriptors = orb.detectAndCompute(known_face, None)
        
        if known_descriptors is not None and detected_descriptors is not None:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(detected_descriptors, known_descriptors)
            match_score = sum([m.distance for m in matches]) / max(len(matches), 1)
            
            if match_score < best_match[1]:  # Lower score means better match
                best_match = (name, match_score)

    return best_match[0]

def process_frame(frame):
    """
    Detects faces using YOLOv8n, recognizes known faces with image similarity techniques,
    and annotates the frame with rectangles and names.
    """
    if frame is None:
        return np.zeros((480, 640, 3), dtype=np.uint8)

    results = model(frame)
    
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            detected_face = frame[y1:y2, x1:x2]

            name = match_face(detected_face)

            now = datetime.datetime.now()
            if name != "Unknown" and (name not in last_logged or (now - last_logged[name]).seconds > 60):
                Attendance.objects.create(name=name)
                last_logged[name] = now

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 1)

    return frame

def generate_combined_stream():
    """
    Uses the laptop and mobile camera frame generators,
    processes each frame for face recognition,
    combines the frames side by side, encodes the result as JPEG,
    and yields a byte stream formatted for MJPEG streaming.
    """
    laptop_gen = laptop_frame_generator()
    

    while True:
        frame_laptop = next(laptop_gen)
        

        processed_laptop = process_frame(frame_laptop)
        

        # if processed_laptop.shape[0] != processed_mobile.shape[0]:
        #     processed_mobile = cv2.resize(processed_mobile, (processed_laptop.shape[1], processed_laptop.shape[0]))

        # combined_frame = np.hstack((processed_laptop, processed_mobile))

        ret, buffer = cv2.imencode(".jpg", processed_laptop)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

def add_new_face(name, face_image_file):
    """
    Saves an uploaded face image to the KNOWN_FACES_DIR folder with the provided name.
    Refreshes the known faces so the new face is available for recognition.
    """
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)

    file_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    with open(file_path, "wb+") as destination:
        for chunk in face_image_file.chunks():
            destination.write(chunk)

    refresh_known_faces()
