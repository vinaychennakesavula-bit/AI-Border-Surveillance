import cv2
import threading
import time


class CameraManager:

    def __init__(self):

        self.cameras = {

            1: {
                "id": 1,
                "name": "Camera 01",
                "source": 0,  # Laptop / USB webcam
                "cap": None,
                "status": "offline",
                "enabled": False,
                "lock": threading.Lock()
            },

            2: {
                "id": 2,
                "name": "Camera 02",
                "source": "http://192.168.1.7:4747/video",
                "cap": None,
                "status": "offline",
                "enabled": False,
                "lock": threading.Lock()
            },

            3: {
                "id": 3,
                "name": "Camera 03",
                "source": "http://192.168.1.11:4747/video",
                "cap": None,
                "status": "offline",
                "enabled": False,
                "lock": threading.Lock()
            }
        }


    # ==================================================
    # SET CAMERA SOURCE
    # ==================================================

    def set_camera_source(self, camera_id, source):

        if camera_id not in self.cameras:
            return False

        self.cameras[camera_id]["source"] = source

        print(
            f"Camera {camera_id} source set to: {source}"
        )

        return True


    # ==================================================
    # OPEN CAMERA
    # ==================================================

    def open_camera(self, camera_id):

        if camera_id not in self.cameras:
            return False, "Camera does not exist"

        camera = self.cameras[camera_id]

        source = camera["source"]

        if source is None:
            camera["status"] = "offline"
            camera["enabled"] = False

            return False, "No camera source configured"


        # Already running
        if camera["cap"] is not None:

            if camera["cap"].isOpened():

                camera["status"] = "online"
                camera["enabled"] = True

                return True, "Camera already running"


        print(f"Opening {camera['name']}...")

        try:

            cap = cv2.VideoCapture(source)

            # Wait for initialization
            time.sleep(0.5)

            if not cap.isOpened():

                cap.release()

                camera["cap"] = None
                camera["status"] = "offline"
                camera["enabled"] = False

                print(
                    f"{camera['name']} could not be opened."
                )

                return False, "Unable to open camera"


            # Laptop webcam resolution
            if camera_id == 1:

                cap.set(
                    cv2.CAP_PROP_FRAME_WIDTH,
                    1280
                )

                cap.set(
                    cv2.CAP_PROP_FRAME_HEIGHT,
                    720
                )


            camera["cap"] = cap
            camera["status"] = "online"
            camera["enabled"] = True

            print(
                f"{camera['name']} connected."
            )

            return True, "Camera started successfully"


        except Exception as e:

            camera["cap"] = None
            camera["status"] = "offline"
            camera["enabled"] = False

            print(
                f"Error opening Camera {camera_id}: {e}"
            )

            return False, str(e)


    # ==================================================
    # CLOSE CAMERA
    # ==================================================

    def close_camera(self, camera_id):

        if camera_id not in self.cameras:
            return False, "Camera does not exist"

        camera = self.cameras[camera_id]

        print(
            f"Turning OFF {camera['name']}..."
        )

        # IMPORTANT:
        # Set enabled False FIRST.
        # This tells streaming/detection loops to stop.
        camera["enabled"] = False
        camera["status"] = "offline"


        with camera["lock"]:

            if camera["cap"] is not None:

                try:
                    camera["cap"].release()

                except Exception:
                    pass

                camera["cap"] = None


        print(
            f"{camera['name']} is OFF."
        )

        return True, "Camera stopped successfully"


    # ==================================================
    # READ FRAME
    # ==================================================

    def read_frame(self, camera_id):

        if camera_id not in self.cameras:
            return None

        camera = self.cameras[camera_id]


        # NEVER restart automatically
        if not camera["enabled"]:
            return None


        cap = camera["cap"]

        if cap is None:
            return None


        with camera["lock"]:

            # Check again because OFF
            # could have been pressed
            if not camera["enabled"]:
                return None

            success, frame = cap.read()


        if success:

            camera["status"] = "online"

            return frame


        # Camera disconnected
        camera["status"] = "offline"

        return None


    # ==================================================
    # GET STATUS
    # ==================================================

    def get_status(self):

        result = {}


        for camera_id, camera in self.cameras.items():

            result[str(camera_id)] = {

                "id": camera["id"],

                "name": camera["name"],

                "status": camera["status"],

                "enabled": camera["enabled"],

                "source": camera["source"]
            }


        return result


    # ==================================================
    # RELEASE ALL
    # ==================================================

    def release_all(self):

        print("Releasing all cameras...")

        for camera_id in self.cameras:

            self.close_camera(camera_id)

        print("All cameras released.")