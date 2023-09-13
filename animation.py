import pygame
import numpy as np
import os
import sys

class Video:

    def __init__(self,size):
        self.path = "D:\\Facultad\\Tercer Año\\Segundo Cuatrimestre\\ACN_TP1_simulation\slides\\animation"
        self.name = "capture"
        self.cnt = 0

        # Ensure we have somewhere for the frames
        try:
            os.makedirs(self.path)
        except OSError:
            pass
    
    def make_png(self,screen):
        self.cnt+=1
        fullpath = self.path + "\\"+self.name + "%08d.png"%self.cnt
        pygame.image.save(screen,fullpath)

    #https://stackoverflow.com/questions/44947505/how-to-make-a-movie-out-of-images-in-python
    #https://stackoverflow.com/questions/3561715/using-ffmpeg-to-encode-a-high-quality-video
    def make_mp4(self):
        os.system("ffmpeg -r 60 -i D:\Facultad\\animation\\capture%08d.png -vcodec mpeg4 -q:v 0 -y movie.mp4")


# Initialize Pygame
pygame.init()

# Define constants for the screen dimensions and colors
WIDTH, HEIGHT = 1600, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define the road length in meters
ROAD_LENGTH_METERS = 15500

# Create a Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Animation")

# Function to draw the road and position labels
def draw_road():
    # Draw the road as two horizontal lines
    # pygame.draw.line(screen, BLACK, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 5)

    # Draw position labels above the road (rounded to kilometers)
    label_interval = ROAD_LENGTH_METERS / 10
    for i in range(11):
        position_km = int(i * label_interval / 1000)  # Convert to rounded kilometers
        label = f"{position_km} km"
        font = pygame.font.Font(None, 24)  # Smaller font size
        text = font.render(label, True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (i * WIDTH // 10, HEIGHT // 4 - 20)  # Adjusted position
        if i == 0:
            text_rect.left = 10  # Adjust for 0 km label
        elif i == 10:
            text_rect.right = WIDTH - 10  # Adjust for 15 km label
        screen.blit(text, text_rect)

# Function to draw cars at their respective positions
def draw_cars(positions, time_step):
    # Clear the screen
    screen.fill(WHITE)

    # Draw the road and position labels
    draw_road()

    # Draw cars as rectangles
    num_cars = positions.shape[0]
    car_width = 3
    car_height = 3
    for i in range(num_cars):
        car_x_percent = positions[i, time_step] / ROAD_LENGTH_METERS
        car_x = car_x_percent * WIDTH
        car_y = HEIGHT // 2 - car_height // 2
        pygame.draw.rect(screen, BLACK, (car_x, car_y, car_width, car_height))

    # Display the current time
    font = pygame.font.Font(None, 36)
    time_label = f"Time: {time_step}"
    text = font.render(time_label, True, BLACK)
    screen.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()

def main(positions, fps):
    num_time_steps = positions.shape[1]
    running = True
    time_step = 0

    # Create a Pygame clock to control the frame rate
    clock = pygame.time.Clock()
    video = Video((1280,720))
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        video.make_png(screen)

        draw_cars(positions, time_step)
        time_step = (time_step + 1) % num_time_steps

        # Control the frame rate
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    # Create or load your numpy array here
    # For example, you can create a random array with:
    # num_cars = 5
    # num_time_steps = 100
    positions = np.load("npys/results_noche_pasada/pos0.npy")

    # Set the desired FPS for animation
    animation_fps = 60

    # main(positions, animation_fps)

    video = Video((1280,720))
    video.make_mp4()
