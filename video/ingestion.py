# detection_app/video_camera.py

import cv2
from threading import Thread

class VideoCamera:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise Exception("Error: Unable to open video capture.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def __del__(self):
        if self.cap:
            self.cap.release()

# Create a global instance to be shared
camera_instance = VideoCamera()
