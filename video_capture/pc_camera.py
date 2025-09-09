import cv2
from detection.object_detection import detect_objects
from video.ingestion import camera_instance




def generate_frames_normal():
    while True:
        frame = camera_instance.get_frame()
        if frame is None:
            continue
        ret2, buffer = cv2.imencode('.jpg', frame)
        if not ret2:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def generate_frames_detect():
    while True:
        frame = camera_instance.get_frame()
        if frame is None:
            continue
        # Pass a copy of the frame to detection so the original remains unaffected.
        processed_frame = detect_objects(frame.copy())
        ret2, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret2:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
# attendance/video/laptop_cam.py

import cv2

def laptop_frame_generator():
    while True:
        frame = camera_instance.get_frame() # Index 0 for the laptop camera
        yield frame


def cam_for_anomaly():
    while True:
        frame =camera_instance.get_frame()
        return frame 
# class Camera:
#     def __init__(self, source=0):
#         self.cap = cv2.VideoCapture(source)
#         if not self.cap.isOpened():
#             raise Exception("Error: Unable to open video capture.")

#     def get_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             return None
#         return frame

#     def __del__(self):
#         if self.cap:
#             self.cap.release()