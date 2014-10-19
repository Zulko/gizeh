import gizeh as gz
import numpy as np

surface = gz.Surface(200,200, bg_color=(1, 0.9, 0.6))

star1 = gz.star(radius=70, ratio=.4, fill=(1,1,1), angle=-np.pi/2,
             stroke_width=2, stroke=(1,0,0))
star2 = gz.star(radius =55, ratio=.4, fill=(1,0,0), angle=-np.pi/2)
stars = gz.Group([ star1, star2 ]).translate([100,100])
stars.draw(surface)

surface.write_to_png("star.png")