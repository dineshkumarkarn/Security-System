from ultralytics import YOLO
import cv2
import numpy as np
import time
import os
from django.core.files import File
from playsound import playsound    # This will play sound via PC speakers.

from Dashboard.models import AnomalyClip
from video_capture.pc_camera import cam_for_anomaly
import pygame
from twilio.rest import Client


# Initialize pygame mixer
pygame.mixer.init()
# Twilio credentials (update these with your actual Twilio details)
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_FROM_NUMBER = "+your_twilio_from_number"      # e.g., "+1234567890"
ALERT_TO_NUMBER = "+recipient_mobile_number"          # e.g., "+19876543210"

def send_sms_alert(severity, clip_url):
    """
    Sends an SMS alert using Twilio.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        if severity == "High":
            message_body = f"ALERT: High severity anomaly detected! Clip: {clip_url}"
        else:
            message_body = f"Notice: Unusual anomaly detected. Clip: {clip_url}"
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=ALERT_TO_NUMBER
        )
        print("SMS alert sent. SID:", message.sid)
    except Exception as e:
        print("Error sending SMS alert:", e)

def send_alert_siren(severity, clip_url):
    """
    Play an audible alert using pygame on the local machine.
    For High severity, use the provided MP3 file path.
    For Unusual, you can also use a different file if desired.
    """
    try:
        # Use an absolute path to the sound file.
        # Given path for hard anomaly:
        hard_siren_path = r"C:\Users\dines\OneDrive\Desktop\ingen dynamics\Security_System\low-battery-alert-sfx-345413.mp3"
        # For the unusual alert, you could use a similar or different file.
        unusual_siren_path = r"C:\Users\dines\OneDrive\Desktop\ingen dynamics\Security_System\low-battery-alert-sfx-345413.mp3"
        
        if severity == "High":
            sound_path = hard_siren_path
        else:
            sound_path = unusual_siren_path
        
        # Load and play the sound via pygame
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
        
        # Wait until the sound finishes playback
        while pygame.mixer.music.get_busy():
            pygame.time.delay(100)
        
        print(f"[ALERT SOUND] {severity} anomaly detected! Clip available at: {clip_url}")
    except Exception as e:
        print("Error playing alert sound with pygame:", e)

class AnomalyDetector:
    def __init__(self, source=0):
        self.camera = cam_for_anomaly()
        self.model = YOLO("yolov8n.pt")
        # Expected safe classes (normal).
        self.safe_classes = ["person", "car", "bicycle", "motorbike", "bus", "truck", "dog", "cat"]
        # Classes triggering high severity alerts.
        self.threat_classes = ["knife", "gun", "fire", "boxing hand", "boxing pose"]
        self.recording = False
        self.recording_frames = []
        self.recording_start_time = None
        self.high_clip_duration = 5.0       # Record 5 seconds for high severity anomalies.
        self.unusual_clip_duration = 5.0    # Record 60 seconds for unusual anomalies.

    def save_clip_db(self, frames, severity):
        if not frames:
            return None
        timestamp = int(time.time())
        clip_filename = os.path.join("media", "anomaly_clips", f"anomaly_{timestamp}.mp4")
        os.makedirs(os.path.dirname(clip_filename), exist_ok=True)
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(clip_filename, fourcc, 20.0, (width, height))
        for frame in frames:
            writer.write(frame)
        writer.release()
        with open(clip_filename, 'rb') as f:
            django_file = File(f, name=os.path.basename(clip_filename))
            clip_instance = AnomalyClip.objects.create(clip_file=django_file, severity=severity)
        return clip_instance.clip_file.url

    def process_frame(self):
        raw_frame = cam_for_anomaly()
        if raw_frame is None:
            return None

        frame = cv2.resize(raw_frame, (640, 480))
        results = self.model(frame, verbose=False)
        annotated = frame.copy()
        anomaly_detected = False
        high_severity = False
        unusual_detected = False

        if results and results[0].boxes is not None and len(results[0].boxes.data) > 0:
            detection_data = results[0].boxes.data.cpu().numpy()
            print("Detection boxes:", detection_data)
            for box in detection_data:
                x1, y1, x2, y2, conf, cls_id = box
                label = self.model.names[int(cls_id)]
                print(f"Detected label: {label} with confidence: {conf:.2f}")
                if label in self.threat_classes:
                    anomaly_detected = True
                    high_severity = True
                    color = (0, 0, 255)
                    text = f"High: {label} {conf:.2f}"
                elif label not in self.safe_classes:
                    anomaly_detected = True
                    unusual_detected = True
                    color = (0, 165, 255)
                    text = f"Unusual: {label} {conf:.2f}"
                else:
                    color = (0, 255, 0)
                    text = f"{label} {conf:.2f}"
                cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(annotated, text, (int(x1), int(y1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            print("No detections returned by model.")

        if anomaly_detected:
            if high_severity:
                cv2.putText(annotated, "High Severity Anomaly Detected", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            elif unusual_detected:
                cv2.putText(annotated, "Anomaly Detected", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
        else:
            cv2.putText(annotated, "No anomaly detected", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            print("No anomaly detected.")

        current_time = time.time()
        effective_duration = self.high_clip_duration if high_severity else self.unusual_clip_duration

        if anomaly_detected:
            if not self.recording:
                self.recording = True
                self.recording_start_time = current_time
                self.recording_frames = []
            self.recording_frames.append(annotated.copy())
        else:
            if self.recording:
                self.recording_frames.append(annotated.copy())

        if self.recording and (current_time - self.recording_start_time >= effective_duration):
            severity = "High" if high_severity else "Unusual"
            clip_url = self.save_clip_db(self.recording_frames, severity)
            send_alert_siren(severity, clip_url)
            # Reset recording state.
            self.recording = False
            self.recording_frames = []
            self.recording_start_time = None

        ret, jpeg = cv2.imencode('.jpg', annotated)
        return jpeg.tobytes()

    def __del__(self):
        if self.camera:
            del self.camera

def generate_frames_normal_for_anomaly(source=0):
    detector = AnomalyDetector(source)
    while True:
        frame = detector.process_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
