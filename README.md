<p align="center">
  <img src="https://raw.githubusercontent.com/Zulko/gizeh/master/logo.jpeg" alt="[logo]" />
</p>

# Gizeh — Cairo for tourists

Gizeh is a Python library for vector graphics, built on top of [`cairocffi`](https://cairocffi.readthedocs.io/) (Cairo bindings for Python). Cairo is powerful but low-level; Gizeh adds a small set of intuitive primitives to make drawing easier.

```python
# Let's draw a red circle!
import gizeh

surface = gizeh.Surface(width=320, height=260)  # pixels
circle = gizeh.circle(r=30, xy=[40, 40], fill=(1, 0, 0))
circle.draw(surface)  # draw the circle on the surface
surface.write_to_png("circle.png")  # export as PNG
```

See Gizeh in action (combined with MoviePy for animations) in
[this blog post](http://zulko.github.io/blog/2014/09/20/vector-animations-with-python/).

Gizeh supports Python 3.7+.

## Installation

Gizeh requires the Cairo graphics library to be installed on your system.

- macOS (Homebrew):
  - `brew install cairo pkg-config`
- Debian/Ubuntu:
  - `sudo apt-get install -y libcairo2-dev pkg-config`

Then install the Python package:

```bash
pip install gizeh
```

Alternatively, from source (editable/development install):

```bash
pip install -e .
```

## User Guide

This guide, along with the examples in `gizeh/examples`, should give you everything you need to get started. Check docstrings for details.

### Surfaces

A Surface is a rectangle of fixed dimensions (in pixels) on which you draw elements, and which you can save/export as an image:

```python
import gizeh

# initialize surface
surface = gizeh.Surface(width=320, height=260)  # in pixels

# make a shape and draw it on the surface
circle = gizeh.circle(r=30, xy=[40, 40], fill=(1, 1, 1))
circle.draw(surface)

# export the surface
surface.get_npimage()           # returns a (width x height x 3) numpy array
surface.write_to_png("circle.png")
```

### Elements

Basic elements are circles, rectangles, lines, text, etc., that you draw on a surface using `my_element.draw(surface)`. Common parameters:

- `xy`: center coordinates of the object. At render time (`surface.write_to_png`) you can set `y_origin` to `"top"` (default) or `"bottom"`. With `"top"`, `(0, 0)` is the upper-left of the final image; the bottom-right is `(width, height)`. With `"bottom"`, `(0, 0)` is the bottom-left (like plots), and `(width, height)` is the top-right.
- `angle`: rotation (radians) around `xy`.
- `fill`: interior fill (default: none). Can be a color `(R, G, B)`, gradient, image pattern, etc.
- `stroke`: contour fill; same rules as `fill`.
- `stroke_width`: contour width (pixels). Default is `0` (no stroke).

Examples:

```python
import numpy as np
Pi = np.pi

circ = gizeh.circle(r=30, xy=(50, 50), fill=(1, 1, 1))
rect = gizeh.rectangle(lx=60.3, ly=45, xy=(60, 70), fill=(0, 1, 0), angle=Pi/8)
sqr  = gizeh.square(l=20, stroke=(1, 1, 1), stroke_width=1.5)
arc  = gizeh.arc(r=20, a1=Pi/4, a2=3*Pi/4, fill=(1, 1, 1))
text = gizeh.text("Hello world", fontfamily="Impact", fontsize=40,
                  fill=(1, 1, 1), xy=(100, 100), angle=Pi/12)
poly = gizeh.regular_polygon(r=40, n=5, angle=np.pi/4, xy=[40, 50], fill=(1, 0, 1))
line = gizeh.polyline(points=[(0, 0), (20, 30), (40, 40), (0, 10)],
                      stroke_width=3, stroke=(1, 0, 0), fill=(0, 1, 0))
```

### Fill and stroke

`fill` and `stroke` can be:

- RGB `(r, g, b)` with values in `[0, 1]`
- RGBA `(r, g, b, a)` with `a` in `[0, 1]`
- `gizeh.ColorGradient`
- `gizeh.ImagePattern` (an image)
- A NumPy RGB/RGBA image array (where implemented)

### Transformations

Elements can be transformed (translated, rotated, scaled). All transformations are out-of-place: they return a modified copy.

```python
square_1 = gizeh.square(l=20, xy=[30, 35], fill=(1, 0, 0))
square_2 = square_1.rotate(np.pi/8)                    # rotation around [0, 0] by default
square_3 = square_2.rotate(np.pi/4, center=[10, 15])   # rotation around a center
square_4 = square_1.scale(2)                           # two times bigger
square_5 = square_1.scale(sx=2, sy=3)                  # width x2, height x3
square_6 = square_1.scale(2, center=[30, 30])          # zoom around a center
square_7 = square_1.translate(xy=[5, 15])              # translation
```

### Groups

A `Group` is a collection of elements (including nested groups) transformed and drawn together:

```python
square = gizeh.square(l=20, fill=(1, 0, 0), xy=(40, 40))
circle = gizeh.circle(r=20, fill=(1, 1, 0), xy=(50, 30))
group_1 = gizeh.Group([square, circle])
group_2 = group_1.translate(xy=[30, 30]).rotate(np.pi/4)
group_3 = gizeh.Group([circle, group_1])

surface = gizeh.Surface(width=300, height=200)
group_1.draw(surface)
group_2.draw(surface)
group_3.draw(surface)
surface.write_to_png("my_masterwork.png")
```

## Troubleshooting installation

If pip installation fails, ensure you have the system Cairo development packages and `pkg-config` installed (see “Installation” above).

- macOS (Homebrew): `brew install cairo pkg-config`
- Debian/Ubuntu: `sudo apt-get install -y libcairo2-dev pkg-config`

## Developers

Development uses [`uv`](https://github.com/astral-sh/uv) for fast Python packaging and workflows.

Prerequisites:

- Install system packages
  - macOS: `brew install uv cairo pkg-config`
  - Debian/Ubuntu: `sudo apt-get install -y libcairo2-dev pkg-config` and install `uv` from its docs

Setup and install deps:

```bash
uv python install 3.12
uv venv --python 3.12
uv sync --group dev
```

Run tests:

```bash
uv run pytest -q
```

Run a specific test:

```bash
uv run pytest -q tests/test_samples.py::test_random_squares
```

Quick import check:

```bash
uv run python -c "import gizeh, numpy, cairocffi; print('ok')"
```

## Contributing

Gizeh is open-source (MIT) by [Zulko](https://github.com/Zulko). Contributions are welcome—issues and pull requests on
[GitHub](https://github.com/Zulko/gizeh).


