# detection_app/object_detection.py

from ultralytics import YOLO
import cv2

# Load YOLOv8n model (ensure "yolov8n.pt" is in your project root)
model = YOLO("yolov8n.pt")

def detect_objects(frame):
    try:
        # Convert from BGR (OpenCV default) to RGB, as expected by YOLOv8.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print("Error converting frame color:", e)
        return frame

    try:
        # Run inference on the RGB frame.
        results = model.predict(frame_rgb)
    except Exception as e:
        print("Error during YOLOv8 prediction:", e)
        return frame

    # Process detection results
    if results and len(results) > 0:
        result = results[0]
        if result.boxes is not None and len(result.boxes) > 0:
            for idx, box in enumerate(result.boxes.xyxy):
                # Get the coordinates for the detection
                box_np = box.cpu().numpy() if hasattr(box, 'cpu') else box
                x1, y1, x2, y2 = list(map(int, box_np))
                conf = float(result.boxes.conf[idx])
                cls_int = int(result.boxes.cls[idx])
                # Get label (handle names as dict or list)
                label = result.names.get(cls_int, str(cls_int)) if isinstance(result.names, dict) else result.names[cls_int]
                # Draw bounding box and text on the original frame (BGR)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, max(y1 - 10, 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame
