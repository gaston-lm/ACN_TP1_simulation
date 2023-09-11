import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Replace this with your actual data
car_positions_matrix = np.array([
    [0, 10, 20, 30, 40],
    [5, 15, 25, 35, 45],
    [10, 20, 30, 40, 50],
    [15, 25, 35, 45, 55]
])

# Initialize the figure and axis
fig, ax = plt.subplots()

# Set the axis limits based on your simulation
ax.set_xlim(0, car_positions_matrix.max())
ax.set_ylim(0, 1)  # Adjust the y-axis limits as needed

# Create a road background
road = plt.Rectangle((-5, 0), car_positions_matrix.max() + 10, 1, color='gray')
ax.add_patch(road)

# Create lane markings
for i in range(1, 4):
    if i != 2:
        ax.axhline(y=i / 4, color='white', linewidth=2, linestyle='--')
    else:
        ax.axhline(y=i / 4, color='yellow', linewidth=2, linestyle='--')

# Initialize cars with the same color
car_color = 'blue'
cars = [ax.plot([], [], 'o', markersize=10, color=car_color)[0] for _ in range(car_positions_matrix.shape[1])]

# Define an initialization function for the animation
def init():
    for car in cars:
        car.set_data([], [])
    return cars

# Define an update function to animate the car positions
def update(frame):
    for i, car in enumerate(cars):
        car_positions = car_positions_matrix[frame]
        car.set_data(car_positions[i], 0.5)
    return cars

# Create the animation
num_frames = car_positions_matrix.shape[0]
animation = FuncAnimation(fig, update, frames=num_frames, init_func=init, blit=True)

# Show the animation (if you want to display it)
plt.show()
