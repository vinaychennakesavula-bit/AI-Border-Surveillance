import time
from datetime import datetime


class AnalyticsManager:

    def __init__(self):

        # Total people entering
        self.people_in = 0

        # Total people exiting
        self.people_out = 0

        # Total alerts
        self.active_alerts = 0

        # Event history
        self.events = []

        # Tracking information
        self.person_data = {}

        # Virtual border line
        self.line_y = 350

        # Loitering alert after 30 seconds
        self.loitering_seconds = 30


    def process_person(
        self,
        camera_id,
        track_id,
        center_x,
        center_y
    ):

        key = f"{camera_id}_{track_id}"

        current_time = time.time()

        # New person
        if key not in self.person_data:

            self.person_data[key] = {

                "camera_id": camera_id,

                "track_id": track_id,

                "first_seen": current_time,

                "last_seen": current_time,

                "previous_y": center_y,

                "current_y": center_y,

                "entered": False,

                "exited": False,

                "loitering_alert": False

            }

            return


        person = self.person_data[key]

        previous_y = person["current_y"]

        person["previous_y"] = previous_y
        person["current_y"] = center_y
        person["last_seen"] = current_time


        # ==========================================
        # IN COUNT
        # Top to Bottom
        # ==========================================

        if (
            previous_y < self.line_y
            and center_y >= self.line_y
            and not person["entered"]
        ):

            self.people_in += 1

            person["entered"] = True

            self.add_event(
                camera_id,
                "IN",
                f"Person {track_id} entered the surveillance zone"
            )


        # ==========================================
        # OUT COUNT
        # Bottom to Top
        # ==========================================

        elif (
            previous_y > self.line_y
            and center_y <= self.line_y
            and not person["exited"]
        ):

            self.people_out += 1

            person["exited"] = True

            self.add_event(
                camera_id,
                "OUT",
                f"Person {track_id} exited the surveillance zone"
            )


        # ==========================================
        # LOITERING ALERT
        # ==========================================

        staying_time = (
            current_time - person["first_seen"]
        )

        if (
            staying_time >= self.loitering_seconds
            and not person["loitering_alert"]
        ):

            person["loitering_alert"] = True

            self.active_alerts += 1

            self.add_event(
                camera_id,
                "ALERT",
                f"Person {track_id} staying for more than "
                f"{self.loitering_seconds} seconds"
            )


    def add_event(
        self,
        camera_id,
        event_type,
        message
    ):

        event = {

            "id": len(self.events) + 1,

            "camera_id": camera_id,

            "type": event_type,

            "message": message,

            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        self.events.insert(0, event)

        # Keep only latest 100 events
        if len(self.events) > 100:
            self.events = self.events[:100]


    def get_people_staying(self):

        current_time = time.time()

        staying = 0

        for person in self.person_data.values():

            # Person seen within last 5 seconds
            if current_time - person["last_seen"] < 5:
                staying += 1

        return staying


    def get_stats(self):

        return {

            "people_in": self.people_in,

            "people_out": self.people_out,

            "people_staying":
                self.get_people_staying(),

            "active_alerts":
                self.active_alerts
        }


    def get_events(self):

        return self.events


    def reset_camera(self, camera_id):

        keys_to_remove = []

        for key, person in self.person_data.items():

            if person["camera_id"] == camera_id:

                keys_to_remove.append(key)

        for key in keys_to_remove:

            del self.person_data[key]