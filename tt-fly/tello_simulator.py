import math
import time
import numpy as np


class TelloSimulator:
    """Simulates a Tello drone for testing without a physical drone."""

    def __init__(self):
        # Position (x, y, z) in meters, with (0, 0, 0) as starting point
        self.position = np.array([0.0, 0.0, 0.0])
        # Rotation (yaw) in degrees
        self.rotation = 0.0
        # Velocity components (left/right, forward/back, up/down, yaw)
        self.velocity = np.array([0.0, 0.0, 0.0, 0.0])

        # Drone state
        self.is_connected = False
        self.is_flying = False
        self.battery = 100
        self.last_command_time = time.time()

        # Command history for debugging
        self.command_history = []

        # New variables for takeoff/landing
        self.is_taking_off = False
        self.is_landing = False
        self.takeoff_target_height = 1.0
        self.takeoff_speed = 0.5  # meters per second
        self.landing_speed = 0.5  # meters per second

    def connect(self):
        """Simulate connecting to the drone."""
        print("Simulator: Connecting to Tello...")
        self.is_connected = True
        return True

    def get_is_flying(self):
        """Check if the drone is currently flying."""
        return self.is_flying or self.is_taking_off  # Return True during takeoff too

    def get_position(self):
        """Get the current position of the drone."""
        return self.position.copy()

    def get_rotation(self):
        """Get the current rotation (yaw) of the drone."""
        return self.rotation

    def get_battery(self):
        """Get the current battery level."""
        return int(self.battery)

    def takeoff(self):
        """Simulate drone takeoff."""
        if not self.is_connected:
            print("Simulator: Cannot takeoff, not connected")
            return False

        if self.is_flying or self.is_taking_off:
            print("Simulator: Already flying or taking off")
            return False

        print("Simulator: Taking off...")
        self.is_taking_off = True
        self.command_history.append(("takeoff", time.time()))
        return True

    def land(self):
        """Simulate drone landing."""
        if not self.is_flying:
            print("Simulator: Cannot land, not flying")
            return False

        if self.is_landing:
            print("Simulator: Already landing")
            return False

        print("Simulator: Landing...")
        self.is_landing = True
        self.command_history.append(("land", time.time()))
        return True

    def emergency(self):
        """Emergency stop - immediately stops motors and drops the drone."""
        print("Simulator: EMERGENCY STOP!")

        # Immediately stop all motion
        self.velocity = np.array([0.0, 0.0, 0.0, 0.0])

        # Set landing flags and turn off flying
        self.is_flying = False
        self.is_taking_off = False
        self.is_landing = False

        # Record the command
        self.command_history.append(("emergency", time.time()))

        # In a real emergency stop, the drone would just drop
        # In the simulator, we'll set it to the ground instantly
        self.position[2] = 0

        return True

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        """Simulate sending RC controls to the drone."""

        # debug info
        # print(f"RC command: LR={left_right}, FB={forward_backward}, UD={up_down}, YAW={yaw}")
        # print(f"  - State: flying={self.is_flying}, taking_off={self.is_taking_off}, landing={self.is_landing}")

        if not self.is_flying or self.is_landing or self.is_taking_off:
            # Do not accept RC commands when not in active flight
            print("Simulator: Cannot send RC commands, not in active flight")
            return False

        # Record the command
        cmd = (left_right, forward_backward, up_down, yaw)
        self.command_history.append(("rc", cmd, time.time()))

        # Update velocity (normalize to -1.0 to 1.0 range)
        self.velocity = np.array(
            [left_right / 100.0, forward_backward / 100.0, up_down / 100.0, yaw / 100.0]
        )

        return True

    def update(self, dt):
        """Update the simulated drone position based on current velocity."""

        # Debug state tracking
        # if not self.is_flying and not self.is_taking_off and not self.is_landing:
        # print(f"State: flying={self.is_flying}, taking_off={self.is_taking_off}, landing={self.is_landing}")
        # print(f"Position: z={self.position[2]:.2f}, velocity_up={self.velocity[2]:.2f}")

        if not self.is_flying and not self.is_taking_off and self.position[2] < 0.01:
            # Only allow takeoff through the explicit takeoff() method
            self.is_taking_off = False

        # Handle takeoff sequence
        if self.is_taking_off:
            print("Simulator: Takeoff in progress...")
            # Gradually increase height during takeoff
            self.position[2] += self.takeoff_speed * dt

            # Check if reached target height
            if self.position[2] >= self.takeoff_target_height:
                self.position[2] = self.takeoff_target_height
                self.is_taking_off = False
                self.is_flying = True
                print("Simulator: Takeoff complete")
            return

        # Handle landing sequence
        if self.is_landing:
            # Gradually decrease height during landing
            self.position[2] -= self.landing_speed * dt

            # Check if reached ground
            if self.position[2] <= 0:
                self.position[2] = 0  # Set exactly to zero
                self.velocity = np.array([0.0, 0.0, 0.0, 0.0])  # Reset all velocity
                self.is_landing = False
                self.is_flying = False
                print("Simulator: Landing complete")
            return

        # Important: If not flying, do not update position regardless of velocity
        if not self.is_flying:
            # Ensure velocity is zero when not flying
            self.velocity = np.array([0.0, 0.0, 0.0, 0.0])
            return

        # Rest of the update logic for when the drone is flying...
        # Decrease battery over time
        self.battery -= 0.01 * dt
        if self.battery < 0:
            self.battery = 0
            self.land()  # Auto-land on battery depletion

        # Calculate position changes
        angle_rad = math.radians(self.rotation)
        dx = (
            self.velocity[1] * math.cos(angle_rad)
            + self.velocity[0] * math.sin(angle_rad)
        ) * dt
        dy = (
            self.velocity[1] * math.sin(angle_rad)
            - self.velocity[0] * math.cos(angle_rad)
        ) * dt
        dz = self.velocity[2] * dt

        # Update position
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz

        # Ensure drone doesn't go below ground
        if self.position[2] < 0:
            self.position[2] = 0
            # If we hit the ground with downward velocity, stop the vertical movement
            if self.velocity[2] < 0:
                self.velocity[2] = 0

        # Update rotation (yaw)
        self.rotation += self.velocity[3] * 30 * dt
        self.rotation %= 360  # Keep in 0-360 range
