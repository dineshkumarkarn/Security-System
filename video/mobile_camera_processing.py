# detection_app/mobile_camera_processing.py

import cv2
from video_capture.mobile_camera import mobile_camera_instance
from detection.object_detection import detect_objects

def generate_mobile_normal_frames():
    """Generator for mobile normal stream (no processing)."""
    while True:
        frame = mobile_camera_instance.get_frame()
        if frame is None:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def generate_mobile_detect_frames():
    """Generator for mobile object detection stream."""
    while True:
        frame = mobile_camera_instance.get_frame()
        if frame is None:
            continue
        # Work on a copy to avoid modifying the shared frame.
        processed_frame = detect_objects(frame.copy())
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
