from djitellopy import Tello
import numpy as np


class TelloDrone:
    """Controls a Tello drone using djitellopy."""

    def __init__(self, host=None):
        # Initialize the Tello, optionally with a host
        if host is not None:
            self.tello = Tello(host=host)
        else:
            self.tello = Tello()

        # Match the interface of TelloSimulator
        self.is_connected = False
        self.is_flying = False
        self.position = np.array([0.0, 0.0, 0.0])  # We'll estimate this
        self.rotation = 0.0  # Estimated yaw

    def connect(self):
        """Connect to the physical drone."""
        print("Connecting to Tello...")
        try:
            self.tello.connect()
            self.is_connected = True
            # Initialize IMU/state
            self.tello.streamon()
            print(f"Battery: {self.tello.get_battery()}%")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def get_is_flying(self):
        """Check if drone is flying."""
        # The real drone doesn't have a direct 'is_flying' property
        # We'll use our tracked state
        return self.is_flying

    def takeoff(self):
        """Execute takeoff on the real drone."""
        if not self.is_connected:
            print("Cannot takeoff, not connected")
            return False

        if self.is_flying:
            print("Already flying")
            return False

        try:
            print("Taking off...")
            result = self.tello.takeoff()
            if result:
                self.is_flying = True
                # Start from height of ~0.5m after takeoff
                self.position[2] = 0.5
            return result
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return False

    def land(self):
        """Land the drone."""
        if not self.is_flying:
            print("Cannot land, not flying")
            return False

        try:
            print("Landing...")
            result = self.tello.land()
            if result:
                self.is_flying = False
                self.position[2] = 0.0
            return result
        except Exception as e:
            print(f"Landing failed: {e}")
            return False

    def emergency(self):
        """Emergency stop."""
        try:
            print("EMERGENCY STOP!")
            self.tello.emergency()
            self.is_flying = False
            self.position[2] = 0.0
            return True
        except Exception as e:
            print(f"Emergency command failed: {e}")
            return False

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        """Send RC controls to the real drone."""
        if not self.is_flying:
            print("Cannot send RC commands, not flying")
            return False

        try:
            self.tello.send_rc_control(left_right, forward_backward, up_down, yaw)

            # Update our position estimate
            # (This is just a basic estimation, real drones would use state feedback)
            # Note: real-world implementation would be more complex
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
        if self.is_connected and self.is_flying:
            try:
                # Get state updates from the drone when possible
                state = self.tello.get_current_state()

                # Real implementation would update position estimates
                # from accelerometer, visual odometry, etc.

                # Simple placeholder for position estimation
                pass
            except Exception as e:
                print(f"State update error: {e}")
