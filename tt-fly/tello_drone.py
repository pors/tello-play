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
        self.position = np.array(
            [0.0, 0.0, 0.0]
        )  # We'll estimate this  # TODO: use tello info
        self.rotation = 0.0  # Estimated yaw # TODO: use tello info

    def connect(self):
        """Connect to the physical drone."""
        print("Connecting to Tello...")
        try:
            self.tello.connect()
            self.is_connected = True
            # Initialize IMU/state
            self.tello.streamon()  # TODO make sure it is not already on
            print(f"Battery: {self.tello.get_battery()}%")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def get_is_flying(self):
        """Check if drone is flying."""
        return self.tello.is_flying

    def takeoff(self):
        """Execute takeoff on the real drone."""
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
            self.position[2] = 0.0  # TODO: use tello info
            return True
        except Exception as e:
            print(f"Emergency command failed: {e}")
            return False

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        """Send RC controls to the real drone."""
        if not self.tello.is_flying:
            print("Cannot send RC commands, not flying")
            return False

        try:
            self.tello.send_rc_control(left_right, forward_backward, up_down, yaw)

            self.last_command_time = time.time()

            # TODO Update our position estimate
            # (This is just a basic estimation, real drones would use state feedback)
            return True
        except Exception as e:
            print(f"RC command failed: {e}")
            return False

    def get_position(self):
        """Get estimated position of the drone."""
        # For a real drone, you'd compute this from sensor data
        # This is just a placeholder - real implementation would be more complex
        return self.position.copy()

    def get_rotation(self):
        """Get estimated yaw of the drone."""
        try:
            # Try to get actual yaw from the drone
            # This only works in newer firmware versions
            state = self.tello.get_current_state()
            if "yaw" in state:
                self.rotation = float(state["yaw"])
            return self.rotation
        except:
            # Fall back to our estimate if failed
            return self.rotation

    def get_battery(self):
        """Get battery level."""
        try:
            return self.tello.get_battery()
        except:
            return 0

    def update(self, dt):
        """Update drone state estimates."""
        # For real drone, we'd update position estimates based on sensor data
        # This method interfaces with your FlightController
        if self.is_connected and self.tello.is_flying:
            try:
                # Get state updates from the drone when possible
                state = self.tello.get_current_state()

                # Real implementation would update position estimates
                # from accelerometer, visual odometry, etc.

                # Simple placeholder for position estimation
                pass
            except Exception as e:
                print(f"State update error: {e}")
