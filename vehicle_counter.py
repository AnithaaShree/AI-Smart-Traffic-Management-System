# vehicle_counter.py
# UPDATED: Now also returns bounding boxes for violation detection

from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

def detect_vehicles(frame):
    """
    Detect vehicles in a given frame.

    Returns:
        - annotated_frame: frame with bounding boxes drawn
        - vehicle_count: total number of vehicles detected
        - detected_classes: list of detected class names
        - bounding_boxes: list of (x1, y1, x2, y2) for each vehicle
    """

    results = model(frame, verbose=False)

    vehicle_count = 0
    detected_classes = []
    bounding_boxes = []   # ✅ NEW
    annotated_frame = frame.copy()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id in VEHICLE_CLASSES and confidence > 0.3:
                vehicle_count += 1
                class_name = VEHICLE_CLASSES[class_id]
                detected_classes.append(class_name)

                # Get coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # ✅ Store bounding box
                bounding_boxes.append((x1, y1, x2, y2))

                # Draw rectangle
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Label
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # ✅ UPDATED return
    return annotated_frame, vehicle_count, detected_classes, bounding_boxes