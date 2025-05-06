import pygame
import time
import sys
import numpy as np
import math
from gamesir_t1d import GameSirT1dPygame


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


class FlightController:
    """Handles controller input processing and drone control."""

    def __init__(self, drone):
        self.drone = drone

        # Control parameters from attached documents
        self.filter_strength = 0.8  # Smoothing factor (higher = more smoothing)
        self.deadband = 0.03  # Ignore tiny movements
        self.command_interval = 0.05  # 20Hz command rate
        self.speed_multiplier = 0.5  # 50% speed to start (safer)

        # State variables
        self.last_command_time = 0
        self.filtered_values = [0.0, 0.0, 0.0, 0.0]  # Filtered joystick values
        self.send_rc_control = False  # Flag to enable RC control
        # Previous button states for edge detection (initialized on first use)
        self.prev_buttons = None

    def process_input(self, controller):
        """Process controller inputs with filtering and deadbanding."""
        if not controller.is_connected():
            return False

        # Debug controller input
        buttons = [controller.get_button(i) for i in range(controller.get_numbuttons())]
        axes = [controller.get_axis(i) for i in range(controller.get_numaxes())]
        print(f"Raw input - Buttons: {buttons}, Axes: {axes}")


        # Get current joystick values - EUROPEAN STYLE MAPPING
        raw_values = [
            controller.get_axis(2),  # right_x - left/right (roll)
            controller.get_axis(3),  # right_y - forward/backward (pitch)
            controller.get_axis(1),  # left_y - up/down (throttle)
            controller.get_axis(0),  # left_x - yaw rotation
        ]

        # Process button inputs
        self.process_buttons(controller)

        # Apply deadband and filtering
        for i in range(4):
            if abs(raw_values[i]) < self.deadband:
                raw_values[i] = 0  # Zero out very small inputs

            # Apply smoothing filter
            self.filtered_values[i] = (
                self.filter_strength * self.filtered_values[i]
                + (1 - self.filter_strength) * raw_values[i]
            )

            # Apply deadband again after filtering to prevent drift
            if abs(self.filtered_values[i]) < self.deadband:
                self.filtered_values[i] = 0

        # If drone is not flying, auto-disable RC control
        if not self.drone.get_is_flying():
            self.send_rc_control = False

        # Send commands at appropriate intervals when flying
        current_time = time.time()
        if (
            current_time - self.last_command_time >= self.command_interval
            and self.send_rc_control
            and self.drone.get_is_flying()
        ):

            # Convert to integer values (-100 to 100), apply speed multiplier
            command_values = [
                int(val * 100 * self.speed_multiplier) for val in self.filtered_values
            ]

            # Invert y-axis values for more intuitive control (push up = forward)
            command_values[1] = -command_values[1]
            command_values[2] = -command_values[2]

            # Send RC command to drone
            self.drone.send_rc_control(
                command_values[0],  # left/right (roll)
                command_values[1],  # forward/backward (pitch)
                command_values[2],  # up/down (throttle)
                command_values[3],  # yaw
            )

            self.last_command_time = current_time

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

        # B button (1) = Land on rising edge
        if curr[1] == 1 and self.prev_buttons[1] == 0:
            if self.drone.get_is_flying():
                self.drone.land()
                self.send_rc_control = False

        # X button (2) = Emergency stop on rising edge
        if curr[2] == 1 and self.prev_buttons[2] == 0:
            self.drone.emergency()
            self.send_rc_control = False

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


class DroneSimulatorApp:
    """Main application integrating controller, simulator and visualization."""

    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set up display
        self.screen_width, self.screen_height = 1024, 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tello Drone Simulator")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

        # Initialize controller
        print("Initializing GameSir T1d controller...")
        try:
            self.controller = GameSirT1dPygame("Gamesir-T1d-39BD")
            if not self.controller.init():
                print("Failed to initialize controller. Continuing without controller.")
                self.controller = None
        except Exception as e:
            print(f"Failed to initialize controller: {e}")
            self.controller = None

        # Initialize simulator
        self.simulator = TelloSimulator()
        self.simulator.connect()

        # Initialize flight controller
        self.flight_controller = FlightController(self.simulator)

        # Tracking for visual trail
        self.position_history = []
        self.max_trail_length = 100

        # Colors
        self.bg_color = (20, 20, 30)
        self.grid_color = (40, 40, 50)
        self.drone_color = (0, 255, 0)
        self.text_color = (200, 200, 200)
        self.trail_color = (0, 200, 100, 128)  # With alpha

    def run(self):
        """Main application loop."""
        running = True
        last_time = time.time()

        try:
            while running:
                # Calculate delta time
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                # Process controller input if available
                if self.controller and self.controller.is_connected():
                    self.flight_controller.process_input(self.controller)

                # Update simulator
                self.simulator.update(dt)

                # Record position for trail
                if self.simulator.get_is_flying():
                    self.position_history.append(self.simulator.get_position().copy())
                    if len(self.position_history) > self.max_trail_length:
                        self.position_history.pop(0)

                # Draw everything
                self.draw()

                # Cap at 60 FPS
                self.clock.tick(60)

        except KeyboardInterrupt:
            print("Program stopped by user")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Clean up
            if self.controller:
                self.controller.quit()
            pygame.quit()
            sys.exit()

    def draw(self):
        """Draw the visualization."""
        self.screen.fill(self.bg_color)

        # Draw grid
        self.draw_grid()

        # Draw drone views
        self.draw_top_view()
        self.draw_side_view()

        # Draw telemetry and controls
        self.draw_telemetry()
        self.draw_controller_state()

        # Update display
        pygame.display.flip()

    def draw_grid(self):
        """Draw background grid."""
        grid_spacing = 50
        for x in range(0, self.screen_width, grid_spacing):
            pygame.draw.line(
                self.screen, self.grid_color, (x, 0), (x, self.screen_height)
            )
        for y in range(0, self.screen_height, grid_spacing):
            pygame.draw.line(
                self.screen, self.grid_color, (0, y), (self.screen_width, y)
            )

    def draw_top_view(self):
        """Draw top-down view of drone."""
        # Top view area
        view_rect = pygame.Rect(50, 50, 500, 500)
        pygame.draw.rect(self.screen, (30, 30, 40), view_rect)

        # Center point and scale
        center_x, center_y = view_rect.centerx, view_rect.centery
        scale = 50  # pixels per meter

        # Draw coordinate axes
        pygame.draw.line(
            self.screen,
            (150, 0, 0),
            (center_x - 250, center_y),
            (center_x + 250, center_y),
            1,
        )
        pygame.draw.line(
            self.screen,
            (0, 0, 150),
            (center_x, center_y - 250),
            (center_x, center_y + 250),
            1,
        )

        # Draw label
        label = self.font.render("Top View (X-Y)", True, self.text_color)
        self.screen.blit(label, (view_rect.x + 10, view_rect.y + 10))

        # Draw position trail
        if len(self.position_history) > 1:
            points = [
                (center_x + pos[0] * scale, center_y - pos[1] * scale)
                for pos in self.position_history
            ]
            pygame.draw.lines(self.screen, self.trail_color, False, points, 2)

        # Get drone position and rotation
        pos = self.simulator.get_position()
        rot = self.simulator.get_rotation()

        # Draw drone (as triangle pointing in direction of rotation)
        drone_x = center_x + pos[0] * scale
        drone_y = center_y - pos[1] * scale  # Y is inverted in pygame

        # Create triangle points
        angle_rad = math.radians(rot)
        p1_x = drone_x + 10 * math.cos(angle_rad)
        p1_y = drone_y - 10 * math.sin(angle_rad)
        p2_x = drone_x + 5 * math.cos(angle_rad + 2.5)
        p2_y = drone_y - 5 * math.sin(angle_rad + 2.5)
        p3_x = drone_x + 5 * math.cos(angle_rad - 2.5)
        p3_y = drone_y - 5 * math.sin(angle_rad - 2.5)

        pygame.draw.polygon(
            self.screen, self.drone_color, [(p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y)]
        )

    def draw_side_view(self):
        """Draw side view (altitude)."""
        # Side view area
        view_rect = pygame.Rect(50, 600, 500, 150)
        pygame.draw.rect(self.screen, (30, 30, 40), view_rect)

        # Label
        label = self.font.render("Side View (X-Z)", True, self.text_color)
        self.screen.blit(label, (view_rect.x + 10, view_rect.y + 10))

        # Get drone position
        pos = self.simulator.get_position()

        # Center and scale
        center_x = view_rect.x + 250
        ground_y = view_rect.y + 120
        scale_x = 50  # pixels per meter
        scale_z = 30  # pixels per meter

        # Draw ground line
        pygame.draw.line(
            self.screen,
            (100, 80, 0),
            (view_rect.x, ground_y),
            (view_rect.x + 500, ground_y),
            2,
        )

        # Draw position trail for altitude
        if len(self.position_history) > 1:
            points = [
                (center_x + pos[0] * scale_x, ground_y - pos[2] * scale_z)
                for pos in self.position_history
            ]
            pygame.draw.lines(self.screen, self.trail_color, False, points, 2)

        # Draw drone
        drone_x = center_x + pos[0] * scale_x
        drone_y = ground_y - pos[2] * scale_z

        pygame.draw.circle(
            self.screen, self.drone_color, (int(drone_x), int(drone_y)), 5
        )

    def draw_telemetry(self):
        """Draw telemetry information."""
        # Telemetry area
        panel_rect = pygame.Rect(580, 50, 400, 200)
        pygame.draw.rect(self.screen, (30, 30, 40), panel_rect)

        # Title
        title = self.font.render("Drone Telemetry", True, self.text_color)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))

        # Get drone data
        pos = self.simulator.get_position()
        rot = self.simulator.get_rotation()
        bat = self.simulator.get_battery()
        state = "Flying" if self.simulator.get_is_flying() else "Landed"

        # Format text
        lines = [
            f"Status: {state}",
            f"Position: X={pos[0]:.2f}m, Y={pos[1]:.2f}m, Z={pos[2]:.2f}m",
            f"Rotation: {rot:.1f}°",
            f"Battery: {bat}%",
            f"Velocity: LR={self.simulator.velocity[0]:.2f}, FB={self.simulator.velocity[1]:.2f}, UD={self.simulator.velocity[2]:.2f}, YAW={self.simulator.velocity[3]:.2f}",
        ]

        # Draw each line
        for i, line in enumerate(lines):
            text = self.font.render(line, True, self.text_color)
            self.screen.blit(text, (panel_rect.x + 20, panel_rect.y + 40 + i * 30))

        # Draw battery indicator
        bat_x = panel_rect.x + 300
        bat_y = panel_rect.y + 40
        bat_width = 50
        bat_height = 20

        # Battery outline
        pygame.draw.rect(
            self.screen, self.text_color, (bat_x, bat_y, bat_width, bat_height), 1
        )

        # Battery level
        bat_level = max(0, min(1, bat / 100))
        bat_color = (
            (0, 255, 0) if bat > 50 else (255, 255, 0) if bat > 20 else (255, 0, 0)
        )
        pygame.draw.rect(
            self.screen,
            bat_color,
            (bat_x + 1, bat_y + 1, int((bat_width - 2) * bat_level), bat_height - 2),
        )

    def draw_controller_state(self):
        """Draw controller state information."""
        # Controller panel
        panel_rect = pygame.Rect(580, 280, 400, 420)
        pygame.draw.rect(self.screen, (30, 30, 40), panel_rect)

        # Title
        if self.controller:
            conn_state = self.controller.get_connection_state()
            title = self.font.render(
                f"Controller: {conn_state}",
                True,
                (
                    (0, 255, 0)
                    if conn_state == "connected"
                    else (255, 255, 0) if conn_state == "connecting" else (255, 0, 0)
                ),
            )
        else:
            title = self.font.render("Controller: Not Available", True, (255, 0, 0))
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))

        # Draw controller instructions
        instructions = [
            "Controls:",
            "A: Takeoff",
            "B: Land",
            "X: Emergency Stop",
            "L1/R1: Decrease/Increase Speed",
            "Left Stick: Yaw (Rotation), Up/Down (Throttle)",
            "Right Stick: Left/Right (Roll), Forward/Back (Pitch)",
        ]

        for i, line in enumerate(instructions):
            text = self.font.render(line, True, self.text_color)
            self.screen.blit(text, (panel_rect.x + 20, panel_rect.y + 40 + i * 25))

        # Draw current speed setting
        speed_text = self.font.render(
            f"Speed: {self.flight_controller.get_speed_multiplier()*100:.0f}%",
            True,
            self.text_color,
        )
        self.screen.blit(speed_text, (panel_rect.x + 20, panel_rect.y + 250))

        # Draw joystick visualization if controller connected
        if self.controller and self.controller.is_connected():
            filtered_values = self.flight_controller.get_filtered_values()

            # Left joystick (yaw and throttle)
            left_center_x = panel_rect.x + 100
            left_center_y = panel_rect.y + 320

            pygame.draw.circle(
                self.screen, (70, 70, 80), (left_center_x, left_center_y), 50
            )
            pygame.draw.circle(
                self.screen,
                (0, 255, 0),
                (
                    int(left_center_x + filtered_values[3] * 40),  # Left X = yaw
                    int(left_center_y + filtered_values[2] * 40),
                ),  # Left Y = throttle
                10,
            )

            # Right joystick (roll and pitch)
            right_center_x = panel_rect.x + 300
            right_center_y = panel_rect.y + 320

            pygame.draw.circle(
                self.screen, (70, 70, 80), (right_center_x, right_center_y), 50
            )
            pygame.draw.circle(
                self.screen,
                (0, 255, 0),
                (
                    int(right_center_x + filtered_values[0] * 40),  # Right X = roll
                    int(right_center_y + filtered_values[1] * 40),
                ),  # Right Y = pitch
                10,
            )


# Run the application
if __name__ == "__main__":
    app = DroneSimulatorApp()
    app.run()
