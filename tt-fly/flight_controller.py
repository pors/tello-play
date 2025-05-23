import time


class FlightController:
    """Handles controller input processing and drone control."""

    def __init__(self, drone):
        # Initialize with any drone that implements the required interface
        self.drone = drone

        # Control parameters from attached documents
        self.deadband = 0.02  # Ignore tiny movements
        self.speed_multiplier = 0.5  # 50% speed to start (safer)

        # State variables
        self.filtered_values = [0.0, 0.0, 0.0, 0.0]  # Filtered joystick values
        self.send_rc_control = False  # Flag to enable RC control
        # Previous button states for edge detection (initialized on first use)
        self.prev_buttons = None

    def process_input(self, controller):
        """Process controller inputs with minimal filtering."""
        if not controller.is_connected():
            return False

        # Get current joystick values
        raw_values = [
            controller.get_axis(0),  # left_x - yaw rotation
            controller.get_axis(1),  # left_y - up/down (throttle)
            controller.get_axis(2),  # right_x - left/right (roll)
            controller.get_axis(3),  # right_y - forward/backward (pitch)
        ]

        # Process button inputs
        self.process_buttons(controller)

        # Apply minimal deadband to prevent drift
        for i in range(4):
            if abs(raw_values[i]) < self.deadband:
                raw_values[i] = 0  # Zero out very small inputs

        self.filtered_values = raw_values.copy()

        # If drone is not flying, auto-disable RC control
        if not self.drone.get_is_flying():
            self.send_rc_control = False

        # Send commands immediately when flying
        if self.send_rc_control and self.drone.get_is_flying():
            # Convert to integer values (-100 to 100), apply speed multiplier
            command_values = [
                int(val * 100 * self.speed_multiplier) for val in self.filtered_values
            ]

            # Invert Y axes for more intuitive control
            command_values[1] = -command_values[1]  # Throttle (left stick Y)
            command_values[3] = -command_values[3]  # Pitch (right stick Y)

            # Send RC command to drone - REORDERED FOR CORRECT MAPPING
            self.drone.send_rc_control(
                command_values[2],  # Roll - right stick X
                command_values[3],  # Pitch - right stick Y
                command_values[1],  # Throttle - left stick Y
                command_values[0],  # Yaw - left stick X
            )

        return True

    def process_buttons(self, controller):
        """Process button inputs from controller with edge detection."""
        # Capture current button states
        curr = [controller.get_button(i) for i in range(controller.get_numbuttons())]
        # On first invocation, avoid spurious triggers if any button is already down
        if self.prev_buttons is None:
            if any(curr):
                self.prev_buttons = curr
                return
            # No buttons pressed: initialize and proceed to detect edges
            self.prev_buttons = curr

        # A button (0) = Takeoff on rising edge
        if curr[0] == 1 and self.prev_buttons[0] == 0:
            print(curr[0], self.prev_buttons[0])
            print("Takeoff button pressed!?!?!")
            print("Flying??? ", self.drone.get_is_flying())
            if not self.drone.get_is_flying():
                if self.drone.takeoff():
                    self.send_rc_control = True
                    print("Flying now??? ", self.drone.get_is_flying())


        # B button (1) = Land on rising edge
        if curr[1] == 1 and self.prev_buttons[1] == 0:
            if self.drone.get_is_flying():
                self.drone.land()
                self.send_rc_control = False

        # X button (2) = Emergency stop on rising edge
        if curr[2] == 1 and self.prev_buttons[2] == 0:
            self.drone.emergency()
            self.send_rc_control = False

        # Y button (3) = Stop on rising edge
        if curr[3] == 1 and self.prev_buttons[3] == 0:
            self.drone.stop()

        # L1 button (4) = Decrease speed on rising edge
        if curr[4] == 1 and self.prev_buttons[4] == 0:
            self.speed_multiplier = max(0.1, self.speed_multiplier - 0.1)
            print(f"Speed: {self.speed_multiplier*100:.0f}%")

        # R1 button (5) = Increase speed on rising edge
        if curr[5] == 1 and self.prev_buttons[5] == 0:
            self.speed_multiplier = min(1.0, self.speed_multiplier + 0.1)
            print(f"Speed: {self.speed_multiplier*100:.0f}%")

        # Update previous button states
        self.prev_buttons = curr

    def get_filtered_values(self):
        """Get the current filtered control values."""
        return self.filtered_values

    def get_speed_multiplier(self):
        """Get the current speed multiplier."""
        return self.speed_multiplier
