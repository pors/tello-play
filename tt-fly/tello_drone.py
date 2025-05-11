import time
from djitellopy import Tello
import numpy as np
import logging

logging.getLogger("djitellopy").setLevel(logging.WARNING)


class TelloDrone:
    """Controls a Tello drone using djitellopy."""

    def __init__(self, host=None):
        # Initialize the Tello, optionally with a host
        if host is not None:
            self.tello = Tello(host=host)
        else:
            self.tello = Tello()

        self.last_command_time = time.time()
        self.is_connected = False
        self.frame_read = None

    def connect(self):
        """Connect to the physical drone."""
        print("Connecting to Tello...")
        try:
            self.tello.connect()
            self.is_connected = True

            print(f"Battery: {self.tello.get_battery()}%")

            # Make sure stream is off before turning it on
            try:
                self.tello.streamoff()
                print("Stopped any existing video stream")
            except Exception as e:
                print(f"Note: {e}")

            # Initialize frame reading with low quality settings
            self.tello.set_video_resolution(
                self.tello.RESOLUTION_480P
            )  # TODO Try to use 720P
            self.tello.set_video_fps(
                self.tello.FPS_30
            )  # TODO Lower FPS for reduced bandwidth => use app FR controller
            self.tello.set_video_bitrate(
                self.tello.BITRATE_4MBPS
            )  # TODO Try lower bitrate

            # Now turn on the stream
            self.tello.streamon()

            # Add a delay to allow stream initialization
            time.sleep(1.0)

            # Get the frame reader
            self.frame_read = self.tello.get_frame_read()

            # Add another delay to ensure frame reader is ready
            time.sleep(0.5)

            print("Video stream initialized successfully")

            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def get_is_flying(self):
        """Check if drone is flying."""
        return self.tello.is_flying

    def takeoff(self):
        """Execute takeoff on the drone."""
        if not self.is_connected:
            print("Cannot takeoff, not connected")
            return False

        if self.tello.is_flying:
            print("Already flying")
            return False

        try:
            print("Taking off...")
            self.tello.takeoff()
            return True
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return False

    def land(self):
        """Land the drone."""
        if not self.tello.is_flying:
            print("Cannot land, not flying")
            return False

        try:
            print("Landing...")
            self.tello.land()
        except Exception as e:
            print(f"Landing failed: {e}")
            return False

    def stop(self):
        """Stop the drone."""
        if not self.tello.is_flying:
            print("Cannot stop, not flying")
            return False

        try:
            print("Stopping...")
            self.tello.send_control_command("stop")  # Not implemented in djitellopy
            return True
        except Exception as e:
            print(f"Stop command failed: {e}")
            return False

    def emergency(self):
        """Emergency stop."""
        try:
            print("EMERGENCY STOP!")
            self.tello.emergency()
            return True
        except Exception as e:
            print(f"Emergency command failed: {e}")
            return False

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        """Send RC controls to the drone."""
        if not self.tello.is_flying:
            print("Cannot send RC commands, not flying")
            return False

        try:
            self.tello.send_rc_control(left_right, forward_backward, up_down, yaw)

            self.last_command_time = time.time()

            return True
        except Exception as e:
            print(f"RC command failed: {e}")
            return False

    def get_battery(self):
        """Get battery level."""
        try:
            return self.tello.get_battery()
        except:
            return 0

    def get_video_frame(self):
        """Get the current video frame from the drone."""
        if self.frame_read is None:
            return None

        try:
            frame = self.frame_read.frame
            if frame is None or frame.size == 0:
                print("Warning: Received empty frame")
                return None
            return frame
        except Exception as e:
            print(f"Error getting video frame: {e}")
            return None

    def update(self, dt):
        """Update drone state estimates."""
        # This method interfaces with our FlightController
        if self.is_connected and self.tello.is_flying:
            try:
                # Get state updates from the drone when possible
                state = self.tello.get_current_state()
            except Exception as e:
                print(f"State update error: {e}")
