from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from camera import CameraManager
from detection import DetectionEngine
from recorder import RecordingManager
from analytics import AnalyticsManager

import cv2
import time


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Border Surveillance System",
    description="AI-Based Intelligent Video Analytics Platform",
    version="2.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# INITIALIZE SYSTEMS
# =========================================================

camera_manager = CameraManager()

detection_engine = DetectionEngine()

recording_manager = RecordingManager()

analytics_manager = AnalyticsManager()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Border Surveillance Backend Running",
        "status": "online",
        "cameras": 3,
        "ai_detection": "active",
        "recording": "active",
        "analytics": "active"
    }


# =========================================================
# CAMERA STATUS
# =========================================================

@app.get("/api/cameras")
def get_cameras():

    return camera_manager.get_status()


# =========================================================
# TURN ONE CAMERA ON
# =========================================================

@app.post("/api/camera/{camera_id}/on")
def camera_on(camera_id: int):

    if camera_id not in camera_manager.cameras:

        raise HTTPException(
            status_code=404,
            detail="Camera does not exist"
        )

    success, message = camera_manager.open_camera(
        camera_id
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail=message
        )

    return {
        "success": True,
        "camera_id": camera_id,
        "status": "online",
        "message": message
    }


# =========================================================
# TURN ONE CAMERA OFF
# =========================================================

@app.post("/api/camera/{camera_id}/off")
def camera_off(camera_id: int):

    if camera_id not in camera_manager.cameras:

        raise HTTPException(
            status_code=404,
            detail="Camera does not exist"
        )

    # Stop recording BEFORE closing camera
    recording_data = recording_manager.stop_recording(
        camera_id
    )

    # Clear tracking data for this camera
    analytics_manager.reset_camera(
        camera_id
    )

    success, message = camera_manager.close_camera(
        camera_id
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail=message
        )

    return {
        "success": True,
        "camera_id": camera_id,
        "status": "offline",
        "recording": recording_data,
        "message": message
    }


# =========================================================
# TURN ALL CAMERAS ON
# =========================================================

@app.post("/api/cameras/on")
def all_cameras_on():

    results = {}

    successful = 0

    for camera_id in camera_manager.cameras:

        success, message = camera_manager.open_camera(
            camera_id
        )

        results[str(camera_id)] = {
            "success": success,
            "message": message
        }

        if success:
            successful += 1

    return {
        "success": True,
        "message": f"{successful}/3 cameras started",
        "cameras": results
    }


# =========================================================
# TURN ALL CAMERAS OFF
# =========================================================

@app.post("/api/cameras/off")
def all_cameras_off():

    results = {}

    for camera_id in camera_manager.cameras:

        # Stop recording first
        recording_data = recording_manager.stop_recording(
            camera_id
        )

        # Reset tracking data
        analytics_manager.reset_camera(
            camera_id
        )

        # Close camera
        success, message = camera_manager.close_camera(
            camera_id
        )

        results[str(camera_id)] = {
            "success": success,
            "message": message,
            "recording": recording_data
        }

    return {
        "success": True,
        "message": "All cameras stopped",
        "cameras": results
    }


# =========================================================
# GENERATE VIDEO FRAMES
# =========================================================

def generate_frames(camera_id):

    while True:

        # Check camera exists
        if camera_id not in camera_manager.cameras:
            break

        camera = camera_manager.cameras[camera_id]

        # Stop streaming when camera is OFF
        if not camera["enabled"]:
            break

        # Read frame
        frame = camera_manager.read_frame(
            camera_id
        )

        if frame is None:

            time.sleep(0.05)

            continue


        # =================================================
        # AI DETECTION + TRACKING
        # =================================================

        detections = []

        try:

            processed_frame, detections = (
                detection_engine.detect_and_track(frame)
            )

        except Exception as e:

            print(
                f"Detection error Camera {camera_id}: {e}"
            )

            processed_frame = frame.copy()


        # =================================================
        # ANALYTICS PROCESSING
        # =================================================

        for detection in detections:

            track_id = detection.get(
                "track_id",
                -1
            )

            # Skip invalid tracking ID
            if track_id == -1:
                continue

            center = detection.get(
                "center",
                [0, 0]
            )

            center_x = center[0]
            center_y = center[1]

            analytics_manager.process_person(
                camera_id,
                track_id,
                center_x,
                center_y
            )


        # =================================================
        # VIRTUAL BORDER LINE
        # =================================================

        line_y = analytics_manager.line_y

        frame_height = processed_frame.shape[0]

        # If camera resolution is smaller
        if line_y >= frame_height:
            line_y = frame_height // 2

        cv2.line(
            processed_frame,
            (0, line_y),
            (processed_frame.shape[1], line_y),
            (0, 0, 255),
            3
        )

        cv2.putText(
            processed_frame,
            "VIRTUAL BORDER LINE",
            (20, max(30, line_y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


        # =================================================
        # GET LIVE STATISTICS
        # =================================================

        stats = analytics_manager.get_stats()


        # =================================================
        # CAMERA LABEL
        # =================================================

        cv2.putText(
            processed_frame,
            f"CAMERA {camera_id}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )


        # =================================================
        # DETECTION COUNT
        # =================================================

        cv2.putText(
            processed_frame,
            f"DETECTIONS: {len(detections)}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # =================================================
        # IN
        # =================================================

        cv2.putText(
            processed_frame,
            f"IN: {stats['people_in']}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        # =================================================
        # OUT
        # =================================================

        cv2.putText(
            processed_frame,
            f"OUT: {stats['people_out']}",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 255),
            2
        )


        # =================================================
        # STAYING
        # =================================================

        cv2.putText(
            processed_frame,
            f"STAYING: {stats['people_staying']}",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


        # =================================================
        # ALERTS
        # =================================================

        cv2.putText(
            processed_frame,
            f"ALERTS: {stats['active_alerts']}",
            (20, 215),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


        # =================================================
        # RECORD VIDEO
        # =================================================

        try:

            recording_manager.write_frame(
                camera_id,
                processed_frame
            )

        except Exception as e:

            print(
                f"Recording error Camera {camera_id}: {e}"
            )


        # =================================================
        # RECORDING INDICATOR
        # =================================================

        if recording_manager.is_recording(camera_id):

            cv2.circle(
                processed_frame,
                (processed_frame.shape[1] - 120, 32),
                8,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                processed_frame,
                "REC",
                (processed_frame.shape[1] - 100, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )


        # =================================================
        # ENCODE FRAME
        # =================================================

        success, buffer = cv2.imencode(
            ".jpg",
            processed_frame
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()


        # =================================================
        # STREAM FRAME
        # =================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


# =========================================================
# CAMERA STREAM ENDPOINT
# =========================================================

@app.get("/api/camera/{camera_id}/stream")
def camera_stream(camera_id: int):

    if camera_id not in camera_manager.cameras:

        raise HTTPException(
            status_code=404,
            detail="Camera does not exist"
        )

    camera = camera_manager.cameras[camera_id]

    if not camera["enabled"]:

        raise HTTPException(
            status_code=400,
            detail="Camera is OFF. Press ON first."
        )

    return StreamingResponse(
        generate_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# =========================================================
# SYSTEM STATUS
# =========================================================

@app.get("/api/status")
def system_status():

    cameras = camera_manager.get_status()

    online = 0

    for camera in cameras.values():

        if camera["status"] == "online":
            online += 1

    active_recordings = 0

    for camera_id in camera_manager.cameras:

        if recording_manager.is_recording(camera_id):
            active_recordings += 1

    return {
        "system": "online",
        "total_cameras": 3,
        "online_cameras": online,
        "offline_cameras": 3 - online,
        "active_recordings": active_recordings,
        "ai_engine": "active",
        "analytics_engine": "active"
    }


# =========================================================
# ANALYTICS STATISTICS
# =========================================================

@app.get("/api/stats")
def get_stats():

    stats = analytics_manager.get_stats()

    active_recordings = 0

    for camera_id in camera_manager.cameras:

        if recording_manager.is_recording(camera_id):
            active_recordings += 1

    stats["active_recordings"] = active_recordings

    return stats


# =========================================================
# EVENTS
# =========================================================

@app.get("/api/events")
def get_events():

    return analytics_manager.get_events()


# =========================================================
# RECORDINGS
# =========================================================

@app.get("/api/recordings")
def get_recordings():

    return recording_manager.get_recordings()


# =========================================================
# RECORDING STATUS
# =========================================================

@app.get("/api/recording-status")
def recording_status():

    result = {}

    for camera_id in camera_manager.cameras:

        result[str(camera_id)] = {
            "recording":
                recording_manager.is_recording(camera_id)
        }

    return result


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event("shutdown")
def shutdown():

    print("Shutting down surveillance system...")

    # Stop recordings first
    for camera_id in camera_manager.cameras:

        recording_manager.stop_recording(
            camera_id
        )

    # Release cameras
    camera_manager.release_all()

    print(
        "All cameras and recordings released."
    )