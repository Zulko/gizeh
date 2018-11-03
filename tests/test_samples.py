import os
import numpy as np
from PIL import Image
import gizeh as gz

samples_dir = os.path.join("tests", "samples")
samples = {
    f[:-4]: np.array(Image.open(os.path.join(samples_dir, f)))
    for f in os.listdir(samples_dir)
}


def is_like_sample(surface, sample_name):
    return (surface.get_npimage() == samples[sample_name]).all()


def test_random_squares():
    np.random.seed(123)
    L = 200
    surface = gz.Surface(L, L, bg_color=(1, 1, 1))
    n_squares = 1000
    angles = 2 * np.pi * np.random.rand(n_squares)
    sizes = 20 + 20 * np.random.rand(n_squares)
    positions = L * np.random.rand(n_squares, 2)
    colors = np.random.rand(n_squares, 3)

    for angle, size, position, color in zip(angles, sizes, positions, colors):
        square = gz.square(size, xy=position, angle=angle, fill=color,
                           stroke_width=size / 20)
        square.draw(surface)

    assert is_like_sample(surface, 'random_squares')


def test_star():
    surface = gz.Surface(200, 200, bg_color=(1, 0.9, 0.6))

    star1 = gz.star(radius=70, ratio=.4, fill=(1, 1, 1), angle=-np.pi / 2,
                    stroke_width=2, stroke=(1, 0, 0))
    star2 = gz.star(radius=55, ratio=.4, fill=(1, 0, 0), angle=-np.pi / 2)
    stars = gz.Group([star1, star2]).translate([100, 100])
    stars.draw(surface)

    assert is_like_sample(surface, 'star')


def test_yin_yang():
    L = 200  # <- dimensions of the final picture
    surface = gz.Surface(L, L, bg_color=(0, .3, .6))  # blue background
    r = 70  # radius of the whole yin yang

    yin_yang = gz.Group([
        gz.arc(r, np.pi / 2, 3 * np.pi / 2, fill=(1, 1, 1)),  # white half
        gz.arc(r, -np.pi / 2, np.pi / 2, fill=(0, 0, 0)),  # black half

        gz.arc(r / 2, -np.pi / 2, np.pi / 2, fill=(1, 1, 1), xy=[0, -r / 2]),
        gz.arc(r / 2, np.pi / 2, 3 * np.pi / 2, fill=(0, 0, 0), xy=[0, r / 2]),

        gz.circle(r / 8, xy=[0,  +r / 2], fill=(1, 1, 1)),  # white dot
        gz.circle(r / 8, xy=[0,  -r / 2], fill=(0, 0, 0))])  # black dot

    yin_yang.translate([L / 2, L / 2]).draw(surface)

    assert is_like_sample(surface, 'yin_yang')

def test_transparent_colors():
    L = 200  # <- dimensions of the final picture
    surface = gz.Surface(L, L, bg_color=(1, 1, 1))  # <- white background
    radius = 50
    centers = [gz.polar2cart(40, angle)
               for angle in [0, 2 * np.pi / 3, 4 * np.pi / 3]]
    colors = [(1, 0, 0, .4),  # <- Semi-tranparent red (R,G,B, transparency)
              (0, 1, 0, .4),  # <- Semi-tranparent green
              (0, 0, 1, .4)]  # <- Semi-tranparent blue
    circles = gz.Group([gz.circle(radius, xy=center, fill=color,
                                  stroke_width=3, stroke=(0, 0, 0))
                        for center, color in zip(centers, colors)])
    circles.translate([L / 2, L / 2]).draw(surface)

    assert is_like_sample(surface, 'transparent_colors')
