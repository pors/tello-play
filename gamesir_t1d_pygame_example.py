import pygame
from gamesir_t1d_pygame import GameSirT1dPygame  # Save the wrapper code as this file


def main(controller_name):
    # Initialize pygame for window and graphics
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("GameSir T1d Test")
    clock = pygame.time.Clock()

    # Initialize our custom controller
    controller = GameSirT1dPygame(controller_name)
    print("Connecting to controller...")
    if not controller.init():
        print("Failed to connect to controller")
        return

    running = True
    while running:
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read joystick values
        left_x = controller.get_axis(0)
        left_y = controller.get_axis(1)
        right_x = controller.get_axis(2)
        right_y = controller.get_axis(3)

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw joystick positions
        pygame.draw.circle(
            screen, (50, 50, 50), (160, 240), 100
        )  # Left stick background
        pygame.draw.circle(
            screen, (0, 255, 0), (160 + int(left_x * 80), 240 + int(left_y * 80)), 20
        )  # Left stick position

        pygame.draw.circle(
            screen, (50, 50, 50), (480, 240), 100
        )  # Right stick background
        pygame.draw.circle(
            screen, (0, 255, 0), (480 + int(right_x * 80), 240 + int(right_y * 80)), 20
        )  # Right stick position

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(60)

    # Clean up
    controller.quit()
    pygame.quit()

if __name__ == "__main__":
    main("Gamesir-T1d-39BD")
