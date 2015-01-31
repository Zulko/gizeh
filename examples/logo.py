"""
This example generates the logo of Gizeh, a fractal made of triangles.
"""

import gizeh as gz
import numpy as np

# PARAMETERS

L = 600 # Picture dimension
r = 100  # Size of the triangles
angles = np.arange(3)*2*np.pi/3 # directions 3h00, 7h00, 11h00

# INITIALIZE THE SURFACE

surface = gz.Surface(L,L, bg_color=(1,1,1))

# DRAW THE TEXT

txt = gz.text("Gizeh", fontfamily="Dancing Script",
              fontsize=120, fill=(0,0,0),xy=(L/2,L/9))
txt.draw(surface)

# MAKE THE FIRST TRIANGLE

gradient=gz.ColorGradient('radial', [(0,(.3,.2,.8)),(1,(.4,.6,.8))],
                      xy1=(0,0), xy2=(0,r/3), xy3=(0,r))

triangle = gz.regular_polygon(r, n=3,fill=gradient, stroke=(0,0,0),
                              stroke_width=3, xy = (r,0))

# BUILD THE FRACTAL RECURSIVELY

fractal = gz.Group([triangle.rotate(a) for a in angles])
for i in range(6):
    fractal = gz.Group([fractal.scale(.5).rotate(-np.pi)
                        .translate(gz.polar2cart(3*r/2,np.pi+a))
                        for a in angles]+[fractal])

# PLACE AND DRAW THE FRACTAL (this will take time)

fractal.rotate(-np.pi/2).translate((L/2,1.1*L/2)).draw(surface)

# SAVE
surface.write_to_png("logo.png")