"""
This generates a picture with 100 squares of random size, angle,
color and position.
"""

import gizeh as gz
import numpy as np 

L = 200 # <- dimensions of the final picture
surface = gz.Surface(L, L, bg_color=(1,1,1))

# We generate 1000 random values of size, angle, color, position.
# 'rand' is a function that generates numbers between 0 and 1
n_squares = 1000 # number of squares
angles = 2*np.pi* np.random.rand(n_squares) # n_squares angles between 0 and 2pi
sizes = 20 + 20 * np.random.rand(n_squares) # all sizes between 20 and 40
positions = L * np.random.rand(n_squares, 2) # [ [x1, y1] [x2 y2] [x3 y3]]...
colors = np.random.rand(n_squares, 3)


for angle, size, position, color in zip(angles, sizes, positions, colors):
    square = gz.square(size, xy=position, angle=angle, fill=color,
                       stroke_width=size/20) # stroke is black by default.
    square.draw(surface)

surface.write_to_png("random_squares.png")
