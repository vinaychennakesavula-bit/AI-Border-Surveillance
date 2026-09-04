import cv2
import os
from datetime import datetime


class RecordingManager:

    def __init__(self):

        self.recorders = {}
        self.recordings = []

        self.base_directory = os.path.join(
            os.path.dirname(__file__),
            "recordings"
        )

        os.makedirs(
            self.base_directory,
            exist_ok=True
        )

        print(f"Recording directory: {self.base_directory}")


    def start_recording(self, camera_id, frame):

        if camera_id in self.recorders:
            return

        height, width = frame.shape[:2]

        camera_directory = os.path.join(
            self.base_directory,
            f"camera_{camera_id}"
        )

        os.makedirs(
            camera_directory,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = f"camera_{camera_id}_{timestamp}.mp4"

        filepath = os.path.join(
            camera_directory,
            filename
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        fps = 20.0

        writer = cv2.VideoWriter(
            filepath,
            fourcc,
            fps,
            (width, height)
        )

        if not writer.isOpened():

            print(
                f"ERROR: Cannot start recording "
                f"for Camera {camera_id}"
            )

            return

        self.recorders[camera_id] = {

            "writer": writer,
            "filepath": filepath,
            "filename": filename,
            "start_time": datetime.now(),
            "width": width,
            "height": height,
            "fps": fps

        }

        print(f"RECORDING STARTED - CAMERA {camera_id}")
        print(f"File: {filepath}")


    def write_frame(self, camera_id, frame):

        if camera_id not in self.recorders:

            self.start_recording(
                camera_id,
                frame
            )

        recorder = self.recorders.get(camera_id)

        if recorder is None:
            return

        writer = recorder["writer"]

        height, width = frame.shape[:2]

        expected_width = recorder["width"]
        expected_height = recorder["height"]

        if (
            width != expected_width
            or height != expected_height
        ):

            frame = cv2.resize(
                frame,
                (
                    expected_width,
                    expected_height
                )
            )

        try:
            writer.write(frame)

        except Exception as e:
            print(
                f"Recording error Camera {camera_id}: {e}"
            )


    def stop_recording(self, camera_id):

        if camera_id not in self.recorders:
            return None

        recorder = self.recorders[camera_id]

        try:
            recorder["writer"].release()

        except Exception as e:
            print(
                f"Error closing recording Camera "
                f"{camera_id}: {e}"
            )

        end_time = datetime.now()
        start_time = recorder["start_time"]

        duration = (
            end_time - start_time
        ).total_seconds()

        recording_data = {

            "camera_id": camera_id,

            "filename": recorder["filename"],

            "filepath": recorder["filepath"],

            "start_time": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "end_time": end_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "duration_seconds": round(
                duration,
                2
            ),

            "duration_minutes": round(
                duration / 60,
                2
            ),

            "status": "completed"
        }

        self.recordings.insert(
            0,
            recording_data
        )

        del self.recorders[camera_id]

        print(f"RECORDING STOPPED - CAMERA {camera_id}")
        print(
            f"Duration: "
            f"{recording_data['duration_seconds']} seconds"
        )

        return recording_data


    def is_recording(self, camera_id):

        return camera_id in self.recorders


    def get_recordings(self):

        return self.recordings