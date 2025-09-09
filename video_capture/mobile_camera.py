# detection_app/mobile_camera.py

import os
import cv2
import numpy as np
from threading import Thread

# Force the FFmpeg backend to use TCP for RTSP.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# Set the RTSP URL (replace with your actual mobile RTSP URL)
RTSP_URL = "rtsp://192.168.1.100:554/live"

class MobileCamera:
    def __init__(self):
        # Attempt to open the RTSP stream using FFmpeg
        self.cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            print(f"ERROR: Could not open RTSP stream: {RTSP_URL}. Using dummy blank frame.")
            # When the stream fails, set the capture to None
            self.cap = None
            # Create a default dummy (black) frame (480x640 pixels)
            self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            self.grabbed, self.frame = self.cap.read()
        self.running = True

        # Start a background thread that continuously fetches frames.
        thread = Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()

    def update(self):
        # If the RTSP stream couldn't be opened, just log and sleep.
        if self.cap is None:
            while self.running:
                print("Warning: RTSP stream is not available. Serving dummy frame.")
                import time
                time.sleep(1)
            return

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            else:
                print("Warning: Failed to grab frame from RTSP stream; using previous frame.")

    def get_frame(self):
        # Return the latest frame (either from the RTSP stream or the dummy frame)
        return self.frame

    def __del__(self):
        self.running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

# Create a global instance of the MobileCamera.
mobile_camera_instance = MobileCamera()
# attendance/video/mobile_cam.py
# attendance/mobile_cam.py
import cv2

def mobile_frame_generator():
    cap = cv2.VideoCapture(1)  # Change to a URL string if using an IP camera stream.
    if not cap.isOpened():
        raise Exception("Mobile camera is not accessible.")
    while True:
        ret, frame = cap.read()
        if not ret:
            # Yield a blank black frame if the mobile cam doesn't return a frame.
            frame = None
        yield frame

