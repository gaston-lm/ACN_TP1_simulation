import pygame
import numpy as np
import sys

car_positions = np.load("test.npy")  # Load your numpy array

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
CAR_WIDTH = 15
CAR_HEIGHT = 10
ROAD_COLOR = (100, 100, 100)
CAR_COLOR = (0, 0, 0)
FPS = 10
Y_POSITION = (SCREEN_HEIGHT - CAR_HEIGHT) // 2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Simulation")

def draw_cars(x_coordinates):
    for x in x_coordinates:
        if x != 0 and x < 15500:
            pygame.draw.rect(screen, CAR_COLOR, (x, Y_POSITION, CAR_WIDTH, CAR_HEIGHT))

clock = pygame.time.Clock()
running = True
time_step = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(ROAD_COLOR)

     # Get the car positions for the current time step
    current_positions = car_positions[:, time_step]

    # Convert float positions to integers
    current_positions = current_positions.astype(float)

    # Draw the cars
    draw_cars(current_positions)

    # Increment time step
    time_step = (time_step + 1) % car_positions.shape[1]

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()