import cv2
import pygame
import time
import sys
import numpy as np
from flight_controller import FlightController
from tello_drone import TelloDrone
from gamesir_t1d import GameSirT1dPygame
from tello_simulator import TelloSimulator


class TelloControllerApp:
    """Application for controlling a real Tello drone with GameSir controller."""

    def __init__(self, controller_name, host=None, use_simulator=False):
        # Add initialization status flag
        self.initialized = False

        # Initialize pygame
        pygame.init()

        # Set up a display that can accommodate video
        self.screen_width, self.screen_height = 960, 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tello Drone Controller")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

        # Create a rect for where the video will be displayed
        self.video_rect = pygame.Rect(20, 150, 640, 480)

        # Initialize controller
        print("Initializing GameSir T1d controller...")
        try:
            self.controller = GameSirT1dPygame(controller_name)
            if not self.controller.init():
                print("Failed to initialize controller.")
                self.controller = None
                return
        except Exception as e:
            print(f"Failed to initialize controller: {e}")
            self.controller = None
            return

        # Initialize drone (real or simulator)
        if use_simulator:
            self.drone = TelloSimulator()
        else:
            self.drone = TelloDrone(host)

        connected = self.drone.connect()

        if not connected:
            print("Failed to connect to the drone.")
            return

        # Initialize flight controller
        self.flight_controller = FlightController(self.drone)

        # Frame counter for monitoring video stream
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps_stats = []

        # Mark initialization as successful
        self.initialized = True

    def run(self):
        """Main application loop."""
        # Check if properly initialized before running
        if not self.initialized:
            print("Cannot run: Application not properly initialized.")
            return

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

                # Update drone state
                self.drone.update(dt)

                # Draw the telemetry and video display
                self.draw_telemetry()

                # Cap at 60 FPS
                self.clock.tick(60)

        except KeyboardInterrupt:
            print("Program stopped by user")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Ensure the drone lands safely on exit
            if self.drone.get_is_flying():
                print("Emergency landing on program exit")
                self.drone.land()

            # Wait a moment for landing to complete
            time.sleep(2)

            # Clean up
            if self.controller:
                self.controller.quit()
            pygame.quit()
            sys.exit()

    def draw_telemetry(self):
        """Draw telemetry and video display."""
        self.screen.fill((20, 20, 30))

        # Get drone data
        bat = self.drone.get_battery()
        state = "Flying" if self.drone.get_is_flying() else "Landed"

        # Draw telemetry text
        lines = [
            f"Status: {state}",
            f"Battery: {bat}%",
        ]

        # Add controller status
        if self.controller:
            lines.append(f"Controller: {self.controller.get_connection_state()}")

        # Draw each line
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (20, 20 + i * 30))

        # Display video frame if available
        frame = self.drone.get_video_frame()
        if frame is not None:
            # Track FPS
            self.frame_count += 1
            now = time.time()
            if now - self.last_frame_time >= 1.0:  # Calculate FPS every second
                fps = self.frame_count / (now - self.last_frame_time)
                self.fps_stats.append(fps)
                if len(self.fps_stats) > 10:
                    self.fps_stats.pop(0)
                self.frame_count = 0
                self.last_frame_time = now

            # Convert numpy array to pygame surface
            try:
                # Ensure frame has the right format for pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Create a PyGame surface
                h, w = frame.shape[:2]
                pygame_frame = pygame.Surface((w, h))
                pygame.surfarray.blit_array(pygame_frame, np.swapaxes(frame, 0, 1))

                # Scale if needed
                if pygame_frame.get_size() != (
                    self.video_rect.width,
                    self.video_rect.height,
                ):
                    pygame_frame = pygame.transform.scale(
                        pygame_frame, (self.video_rect.width, self.video_rect.height)
                    )

                self.screen.blit(pygame_frame, self.video_rect)
            except Exception as e:
                print(f"Error displaying frame: {e}")
                # Draw a red border to indicate error
                pygame.draw.rect(self.screen, (255, 0, 0), self.video_rect, 2)
        else:
            # Draw a placeholder for video
            pygame.draw.rect(self.screen, (40, 40, 60), self.video_rect)
            no_video = self.font.render("No Video Feed", True, (150, 150, 150))
            text_rect = no_video.get_rect(center=self.video_rect.center)
            self.screen.blit(no_video, text_rect)

        # Update display
        pygame.display.flip()


# Run the application
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--controller",
        type=str,
        help="Controller name (of the format: Gamesir-T1d-XXXX)",
    )
    parser.add_argument(
        "--sim", action="store_true", help="Use simulator instead of real drone"
    )
    parser.add_argument(
        "--host", type=str, default=None, help="Tello drone IP address (optional)"
    )
    args = parser.parse_args()

    app = TelloControllerApp(
        controller_name=args.controller, host=args.host, use_simulator=args.sim
    )
    app.run()
