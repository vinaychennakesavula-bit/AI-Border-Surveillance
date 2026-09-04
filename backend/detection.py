from ultralytics import YOLO
import cv2


class DetectionEngine:

    def __init__(self):

        print("Loading YOLO model...")

        self.model = YOLO("yolov8n.pt")

        print("YOLO model loaded successfully.")


    def detect_and_track(self, frame):

        detections = []

        try:

            results = self.model.track(
                frame,
                persist=True,
                verbose=False,
                classes=[0],
                conf=0.40
            )

            for result in results:

                if result.boxes is None:
                    continue

                for box in result.boxes:

                    confidence = float(box.conf[0])

                    if confidence < 0.40:
                        continue

                    track_id = -1

                    if box.id is not None:
                        track_id = int(box.id[0])

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist()
                    )

                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    detection = {
                        "object": "person",
                        "confidence": round(confidence, 2),
                        "track_id": track_id,
                        "box": [x1, y1, x2, y2],
                        "center": [center_x, center_y]
                    }

                    detections.append(detection)

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    if track_id != -1:
                        label = f"PERSON #{track_id} | {confidence:.2f}"
                    else:
                        label = f"PERSON | {confidence:.2f}"

                    cv2.putText(
                        frame,
                        label,
                        (x1, max(25, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

                    cv2.circle(
                        frame,
                        (center_x, center_y),
                        5,
                        (0, 0, 255),
                        -1
                    )

        except Exception as e:
            print(f"Detection/Tracking error: {e}")

        return frame, detections


    def detect(self, frame):
        return self.detect_and_track(frame)