Gizeh - Cairo for tourists
===========================

Python has a fast and powerful vector graphics library called PyCairo, but its is difficult to learn and use. Gizeh implements a few classes on top of Cairo that make it more intuitive:
::

    # Let's draw a red circle !
    import gizeh
    surface = gizeh.Surface(width=320, height=260) # in pixels
    circle = gizeh.circle(r=30, xy= [40,40], fill_color=(1,0,0))
    circle.draw(surface)
    surface.write_to_png("circle.png") # And voila !

Gizeh is an open-source software written by Zulko and released under the MIT licence. Everyone is welcome to contribute !


Installation
--------------

gizeh can be installed by unzipping the source code in one directory and using this command:
::

    (sudo) python setup.py install

You can also install it directly from the Python Package Index with this command:
::

    (sudo) pip install gizeh


Gizeh depends on the Python packages PyCairo and Numpy. They will both be automatically installed (if they aren't already) during the installation of Gizeh.

User Guide
-------------

This guide, along with the examples in the `gizeh/examples` folder, should give you everything you need to get started. To go further, read the function docstrings.

Surfaces
~~~~~~~~

A Surface is a rectangle of fixed dimensions (in pixels), on which you will draw elements, and that you can save or export as an image:
::

    import gizeh
    
    # initialize surface
    surface = gizeh.Surface(width=320, height=260) # in pixels

    # Now make a shape and draw it on the surface
    circle = gizeh.circle(r=30, xy= [40,40], fill_color=(1,1,1))
    circle.draw(surface)

    # Now export the surface
    surface.get_npimage() # returns a (width x height x 3) numpy array
    surface.scipy_imsave("circle.png") # requires scipy.
    surface.write_to_png("circle.png") # doesn't require scipy, but image is flipped
    


Elements
~~~~~~~~~

Basic elements are circles, rectangles, lines, texts, etc., that you can draw on a surface using `my_element.draw(surface)`. You can specify the properties and coordinates of these elements at creation time:

- `xy` : coordinates of the center of the object. (0,0), which is the defaut, corresponds to the bottom left corner of the final picture.
- `angle` : angle (in radians) of the rotation of the element around its center `xy`.
- `fill` : what will fill the element (default is no fill). Can be a color (R,G,B), a color gradient, an image, etc. See section below.
- `stroke` : What will fill the element's contour. Same rules as for `fill`.
- `stroke_width` : the width (in pixels) of the element's contour. Default is 0 (no stroke).

Examples of elements:
::

    Pi = 3.14
    circ = gizeh.circle(r=30, xy=30, fill_color=(1,1,1))
    rect = gizeh.rectangle(lx=60.3, ly=45, xy=30, fill_color=(0,1,0), angle=Pi/8)
    sqr = gizeh.square(l=20, stroke_color=(1,1,1), stroke_width= 1.5)
    arc = gizeh.arc(r=20, a1=Pi/4, a2=3*Pi/4, fill_color=(1,1,1))
    text = gizeh.text("Hello world", fontfamily="Impact",  fontsize=40,
                      fontcolor=(1,1,1), xy=(100,100), angle=Pi/12)
    polygon = gizeh.polygon(r=40, n=5, angle=np.pi/4, xy=[40,50], fill=(1,0,1))
    line = gizeh.polyline(points=[(0,0), (20,30), (40,40), (0,10)], stroke_width=3,
                         stroke_color=(1,0,0), fill_color=(0,1,0))

Fill and stroke
----------------

When you make a shape, the `fill` and `stroke` parameters can be one of the following:

- A RGB color of the form (r,g,b) where each element is comprised between 0 and 1 (1 is 100%).
- A RGBA colot of the form (r,g,b,a), where `a` is comprised between 0 (totally transparent) and 1 (totally opaque)
- A color gradient (see section below)
- A surface: the object will display the content of this surface. In this case the `xy` attribute of the shape really matters, as the element will be filled with the content of the surface in the area on which it stands.
- A numpy array representing a RGB or RGBA image (not implemented yet)
- A PNG image file (not implemented yet)

Examples:
::
    

Color gradients
----------------



Transformations
~~~~~~~~~~~~~~~~

Any element can be tranformed (translated, rotated or scaled). All transformations are *outplace*: they do not modify the original element, they create a modified version of it.

Examples:
::

    square_1 = gizeh.square(l=20, xy = [30,35], fill_color=(1,0,0))
    square_2 = square_1.rotate(Pi/8) # rotation around [0,0] by default
    square_3 = square_2.rotate(Pi/4, center=[10,15]) # rotation around a center
    square_4 = square_1.scale(2) # two times bigger
    square_5 = square1.scale(sx=2, sy=3) # width times 2, height times 3
    square_6 = square_1.scale(2, center=[30,30]) # zoom: scales around a center
    square_7 = square_1.translate(xy=[5,15]) # translation


Groups
~~~~~~~

A Group is a collection of elements which will be transformed and drawn together. The elements can be a basic element (square, circle...) or even groups.

Examples:
::

    square = gizeh.square(l=20, fill_color=(1,0,0), xy=(40,40))
    circle = gizeh.circle(r=20, fill_color=(1,2,0), xy=(50,30))
    group_1 = gizeh.Group([square, circle])
    group_2 = group.translate(xy=[30,30]).rotate(Pi/4)
    group_3 = gizeh.Group([circle, group_1])
    
    surface = gizeh.ImageSurface(width=300,height=200)
    group.draw(surface)
    group_1.draw(surface)
    group_2.draw(surface)
    group_3.draw(surface)
    surface.write_to_png("my_masterwork.png")


That's all folks !
~~~~~~~~~~~~~~~~~~~

To go further, see the examples in the `examples` folder or (wishful thinking) on the Web.
