import pygame
import time
import sys
from gamesir_t1d import GameSirT1dPygame

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up display window for feedback
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tello GameSir Controller")
    font = pygame.font.Font(None, 36)
    
    # Initialize controller
    print("Initializing GameSir T1d controller...")
    try:
        # Use the specific controller name you provided
        controller = GameSirT1dPygame("Gamesir-T1d-39BD")
        if not controller.init():
            print("Failed to initialize controller. Exiting.")
            return
        print(f"Controller initialized: {controller.get_name()}")
    except Exception as e:
        print(f"Failed to initialize controller: {e}")
        return
    
    # Main loop - read and display controller values
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Read controller connection state
            conn_state = controller.get_connection_state()
            
            # Clear the screen
            screen.fill((0, 0, 0))
            
            # Display connection status
            status_color = (255, 0, 0)  # Red for disconnected
            if conn_state == "connected":
                status_color = (0, 255, 0)  # Green for connected
            elif conn_state == "connecting":
                status_color = (255, 255, 0)  # Yellow for connecting
                
            status_text = font.render(f"Status: {conn_state}", True, status_color)
            screen.blit(status_text, (50, 50))
            
            # Only read inputs if controller is connected
            if controller.is_connected():
                # Read joystick values
                left_x = controller.get_axis(0)
                left_y = controller.get_axis(1)
                right_x = controller.get_axis(2)
                right_y = controller.get_axis(3)
                
                # Read button states
                button_states = []
                for i in range(controller.get_numbuttons()):
                    button_states.append(controller.get_button(i))
                
                # Read d-pad
                hat_x, hat_y = controller.get_hat(0)
                
                # Display joystick values
                left_text = font.render(f"Left Stick: ({left_x:.2f}, {left_y:.2f})", True, (255, 255, 255))
                right_text = font.render(f"Right Stick: ({right_x:.2f}, {right_y:.2f})", True, (255, 255, 255))
                screen.blit(left_text, (50, 100))
                screen.blit(right_text, (50, 150))
                
                # Display button states
                button_text = font.render(f"Buttons: {button_states}", True, (255, 255, 255))
                screen.blit(button_text, (50, 200))
                
                # Display D-pad values
                dpad_text = font.render(f"D-pad: ({hat_x}, {hat_y})", True, (255, 255, 255))
                screen.blit(dpad_text, (50, 250))
                
                # Visualize joysticks with circles
                # Left joystick
                pygame.draw.circle(screen, (100, 100, 100), (200, 400), 100)  # Background
                pygame.draw.circle(screen, (0, 255, 0), 
                                (int(200 + left_x * 80), int(400 + left_y * 80)), 20)  # Position
                
                # Right joystick
                pygame.draw.circle(screen, (100, 100, 100), (600, 400), 100)  # Background
                pygame.draw.circle(screen, (0, 255, 0), 
                                (int(600 + right_x * 80), int(400 + right_y * 80)), 20)  # Position
            
            # Update the display
            pygame.display.flip()
            
            # Control the loop speed
            clock.tick(60)  # 60 FPS
            
    except KeyboardInterrupt:
        print("Program stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        controller.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
    