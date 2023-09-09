import pygame
import numpy as np
import sys
import random

def run_animation(car_positions, scale=1.0, min_visible_x=0, max_visible_x=None, fps=8):
    pygame.init()

    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    CAR_WIDTH = 15
    CAR_HEIGHT = 10
    ROAD_COLOR = (100, 100, 100)
    FPS = fps
    Y_POSITION = (SCREEN_HEIGHT - CAR_HEIGHT) // 2

    if max_visible_x is None:
        max_visible_x = len(car_positions[0])

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Car Simulation")

    def draw_cars(x_coordinates, colors):
        for x, color in zip(x_coordinates, colors):
            if 0.5 + min_visible_x <= x <= max_visible_x:
                # Adjust the x-coordinate for scale and visibility
                adjusted_x = int((x - min_visible_x) * scale)
                pygame.draw.rect(screen, color, (adjusted_x, Y_POSITION, CAR_WIDTH, CAR_HEIGHT))

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

        # Draw the cars with their respective random colors
        draw_cars(current_positions, car_colors)

        # Increment time step
        time_step = (time_step + 1) % car_positions.shape[1]

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

car_positions = np.load("test_con_choques.npy")  # Load your numpy array
# Correr toda la Av. Gral Paz entre Liniers y Lugones
# run_animation(car_positions)

# Correr zoomeado en un lugar:
run_animation(car_positions, scale=2.0, min_visible_x=0, max_visible_x=1500, fps=5)