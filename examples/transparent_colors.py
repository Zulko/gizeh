"""
This generates a picture of 3 semi-transparent circles of different colors
which overlap to some extent.
"""

import gizeh as gz
from numpy import pi # <- 3.14... :)

L = 200 # <- dimensions of the final picture

surface = gz.Surface(L,L, bg_color=(1,1,1)) # <- white background

radius = 50
centers = [ gz.polar2cart(40, angle) for angle in [0, 2*pi/3, 4*pi/3]]
colors = [ (1,0,0,.4), # <- Semi-tranparent red (R,G,B, transparency)
           (0,1,0,.4), # <- Semi-tranparent green
           (0,0,1,.4)] # <- Semi-tranparent blue

circles = gz.Group( [ gz.circle(radius, xy=center, fill=color,
                                stroke_width=3, stroke=(0,0,0)) # black stroke
                      for center, color in zip(centers, colors)] )

circles.translate([L/2,L/2]).draw(surface)

surface.write_to_png("transparent_colors.png")
