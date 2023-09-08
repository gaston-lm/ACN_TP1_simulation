import pygame
import sys
import numpy as np
from road import *

simulation = RoadSimulation(3000, 2.0, 4.0, 4, 2, 4.3)

car_positions = simulation.pos
car_speeds = simulation.spd

# Initialize PyGame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Car dimensions
CAR_WIDTH = 20
CAR_HEIGHT = 40

# Lane width and position
LANE_WIDTH = 80
LANE_CENTER = SCREEN_HEIGHT // 2

# Load your NumPy arrays for car positions and car speeds
car_positions = simulation.pos
car_speeds = simulation.spd

# Create the PyGame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Animation")


# Main game loop
if __name__ == "__main__":
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill(WHITE)

        # Draw the highway lane
        pygame.draw.rect(screen, WHITE, (0, LANE_CENTER - LANE_WIDTH // 2, SCREEN_WIDTH, LANE_WIDTH))

        # Draw the cars
        for i in range(car_positions.shape[0]):
            for j in range(car_positions.shape[1]):
                x = car_positions[i, j]
                y = LANE_CENTER - CAR_HEIGHT // 2  # Place cars in the middle of the lane
                pygame.draw.rect(screen, RED, (x, y, CAR_WIDTH, CAR_HEIGHT))

        pygame.display.flip()  # Update the display
