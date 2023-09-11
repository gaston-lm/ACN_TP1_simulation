import pygame
import numpy as np
import sys
import random

def run_animation(car_positions, scale=1.0, min_visible_x=0, max_visible_x=15500, fps=8):
    pygame.init()

    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    CAR_WIDTH = 7
    CAR_HEIGHT = 4
    ROAD_COLOR = (100, 100, 100)
    CAR_COLOR = (0, 0, 0)
    FPS = fps
    Y_POSITION = (SCREEN_HEIGHT - CAR_HEIGHT) // 2

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Car Simulation")

    # Load a font for displaying the time step
    font = pygame.font.Font(None, 36)

    def draw_cars(x_coordinates):
        for x in x_coordinates:
            if 0.5 + min_visible_x <= x <= max_visible_x:
                # Adjust the x-coordinate for scale and visibility
                adjusted_x = int((x - min_visible_x) * scale)
                pygame.draw.rect(screen, CAR_COLOR, (adjusted_x, Y_POSITION, CAR_WIDTH, CAR_HEIGHT))

    clock = pygame.time.Clock()
    running = True
    time_step = 0

    num_cars = len(car_positions)  # Get the number of cars
    # Generate a list of random colors for each car
    car_colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(num_cars)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(ROAD_COLOR)

        # Get the car positions for the current time step
        current_positions = car_positions[:, time_step]

        # Convert float positions to integers
        current_positions = current_positions.astype(float)

        # # Draw the cars with their respective random colors
        draw_cars(current_positions)

        # Display the current time step as text
        time_text = font.render(f"Time: {time_step}", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))  # Position of the text

        # Increment time step
        time_step = (time_step + 1) % car_positions.shape[1]

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

car_positions = np.load("pos_choques.npy")  # Load your numpy array
# Correr toda la Av. Gral Paz entre Liniers y Lugones
run_animation(car_positions, fps=30)

# Correr zoomeado en un lugar:
# run_animation(car_positions, scale=2.0, min_visible_x=0, max_visible_x=5000, fps=15)