"""
This generates a Yin Yang.
"""

import gizeh as gz
from math import pi

L = 200 # <- dimensions of the final picture
surface = gz.Surface(L, L, bg_color=(0 ,.3, .6)) # blue background
r = 70 # radius of the whole yin yang

yin_yang = gz.Group([
     gz.arc(r, pi/2, 3*pi/2, fill = (1,1,1)), # white half
     gz.arc(r, -pi/2, pi/2, fill = (0,0,0)), # black half

     gz.arc(r/2, -pi/2, pi/2, fill = (1,1,1), xy = [0,-r/2]), # white semihalf
     gz.arc(r/2, pi/2, 3*pi/2, fill = (0,0,0), xy = [0, r/2]),  # black semihalf

     gz.circle(r/8, xy = [0,  +r/2], fill = (1,1,1)), # white dot
     gz.circle(r/8, xy = [0,  -r/2], fill = (0,0,0)) ]) # black dot

yin_yang.translate([L/2,L/2]).draw(surface)

surface.write_to_png("yin_yang.png")