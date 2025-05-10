import pygame
import time
import sys
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

        # Set up a minimal display (can be expanded later)
        self.screen_width, self.screen_height = 640, 480
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tello Drone Controller")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

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

                # Draw a simple display
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
        """Draw basic telemetry display."""
        self.screen.fill((20, 20, 30))

        # Get drone data
        pos = self.drone.get_position()
        rot = self.drone.get_rotation()
        bat = self.drone.get_battery()
                    
        # Debug the state check
        flying = self.drone.get_is_flying()
        #print(f"Display state check - get_is_flying()={flying}, tello.is_flying={self.drone.tello.is_flying}")
        
        # Use the CORRECT state
        state = "Flying" if self.drone.get_is_flying() else "Landed"
        
        # Draw telemetry text
        lines = [
            f"Status: {state}",
            f"Battery: {bat}%",
            f"Position (est): X={pos[0]:.2f}m, Y={pos[1]:.2f}m, Z={pos[2]:.2f}m",
            f"Rotation: {rot:.1f}°",
        ]

        # Add controller status
        if self.controller:
            lines.append(f"Controller: {self.controller.get_connection_state()}")

        # Draw each line
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (20, 20 + i * 30))

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

    app = TelloControllerApp(controller_name=args.controller, host=args.host, use_simulator=args.sim)
    app.run()
