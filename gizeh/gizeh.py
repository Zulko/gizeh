from copy import copy, deepcopy
from base64 import b64encode
import numpy as np
import cairocffi as cairo
from .geometry import (rotation_matrix,
                       translation_matrix,
                       scaling_matrix,
                       polar2cart)
from itertools import chain
from math import sqrt

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        # Python 3 compatibility
        from io import BytesIO as StringIO


class Surface:
    """
    A Surface is an object on which Elements are drawn, and which can be
    exported as PNG images, numpy arrays, or be displayed into an IPython
    Notebook.

    Note that this class is simply a thin wrapper around Cairo's Surface class.
    """

    def __init__(self, width, height, bg_color=None):
        """"Initialize."""
        self.width = width
        self.height = height
        self._cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                 width, height)
        if bg_color:
            rectangle(2 * width, 2 * height, fill=bg_color).draw(self)

    @staticmethod
    def from_image(image):
        """Initialize the surface from an np array of an image."""
        h, w, d = image.shape
        if d == 4:
            image = image[:, :, [2, 1, 0, 3]]
        if d == 1:
            image = np.array(3 * [image])
        elif d == 3:
            image = image[:, :, [2, 1, 0]]
            image = np.dstack([image, 255 * np.ones((h, w))])
        sf = Surface(w, h)
        arr = np.frombuffer(sf._cairo_surface.get_data(), np.uint8)
        arr += image.flatten()
        sf._cairo_surface.mark_dirty()
        return sf

    def get_new_context(self):
        """Return a new context for drawing on the surface."""
        return cairo.Context(self._cairo_surface)

    def write_to_png(self, filename, y_origin="top"):
        """Write the image to a PNG.

        Parameter y_origin ("top" or "bottom") decides whether point (0,0)
        lies in the top-left or bottom-left corner of the screen.
        """

        if y_origin == "bottom":
            W, H = self.width, self.height
            new_surface = Surface(W, H)
            rect = (rectangle(2 * W, 2 * H, fill=ImagePattern(self))
                    .scale(1, -1).translate([0, H]))
            rect.draw(new_surface)
            new_surface.write_to_png(filename, y_origin="top")
        else:
            self._cairo_surface.write_to_png(filename)

    def get_npimage(self, transparent=False, y_origin="top"):
        """ Returns a WxHx[3-4] numpy array representing the RGB picture.

        If `transparent` is True the image is WxHx4 and represents a RGBA
        picture, i.e. array[i,j] is the [r,g,b,a] value of the pixel at
        position [i,j]. If `transparent` is false, a RGB array is returned.

        Parameter y_origin ("top" or "bottom") decides whether point (0,0)
        lies in the top-left or bottom-left corner of the screen.
        """

        im = 0 + np.frombuffer(self._cairo_surface.get_data(), np.uint8)
        im.shape = (self.height, self.width, 4)
        im = im[:, :, [2, 1, 0, 3]]  # put RGB back in order
        if y_origin == "bottom":
            im = im[::-1]
        return im if transparent else im[:, :, :3]

    def get_html_embed_code(self, y_origin="top"):
        """Return an html code containing all the PNG data of the surface. """
        png_data = self._repr_png_()
        data = b64encode(png_data).decode('utf-8')
        return """<img  src="data:image/png;base64,%s">""" % (data)

    def ipython_display(self, y_origin="top"):
        """Display the surface in the IPython notebook.

        Will only work if surface.ipython_display() is written at the end of
        one of the notebook's cells.
        """

        from IPython.display import HTML
        return HTML(self.get_html_embed_code(y_origin=y_origin))

    def _repr_html_(self):
        return self.get_html_embed_code()

    def _repr_png_(self):
        """Return the raw PNG data to be displayed in the IPython notebook."""
        data = StringIO()
        self.write_to_png(data)
        return data.getvalue()


class PDFSurface(object):
    """Simple class to allow Gizeh to create PDF figures."""

    def __init__(self, name, width, height, bg_color=None):
        self.width = width
        self.height = height
        self._cairo_surface = cairo.PDFSurface(name, width, height)

    def get_new_context(self):
        """Return a new context for drawing on the surface."""
        return cairo.Context(self._cairo_surface)

    def flush(self):
        """Write the file"""
        self._cairo_surface.flush()

    def finish(self):
        """Close the surface"""
        self._cairo_surface.finish()


class Element:
    """Base class for objects that can be transformed (rotated, translated,
    scaled) and drawn to a Surface.

    Parameter `draw_method` is a function which takes a cairo.Surface.Context()
    as argument and draws on this context. All Elements are draw on a different
    context.
    """

    def __init__(self, draw_method):
        """Initialize."""
        self.draw_method = draw_method
        self.matrix = 1.0 * np.eye(3)

    def _cairo_matrix(self):
        """Return the element's matrix in cairo form """
        m = self.matrix
        return cairo.Matrix(m[0, 0], m[1, 0],
                            m[0, 1], m[1, 1],
                            m[0, 2], m[1, 2])

    def _transform_ctx(self, ctx):
        """Tranform the context before drawing.
        It applies all the rotation, translation, etc. to the context.
        In short, it sets the context's matrix to the element's matrix.
        """
        ctx.set_matrix(self._cairo_matrix())

    def draw(self, surface):
        """Draw the Element on a new context of the given Surface """
        ctx = surface.get_new_context()
        self._transform_ctx(ctx)
        self.draw_method(ctx)

    def set_matrix(self, new_mat):
        """Return a copy of the element, with a new transformation matrix """
        new = deepcopy(self)
        new.matrix = new_mat
        return new

    def rotate(self, angle, center=[0, 0]):
        """Rotate the element.

        Returns a new element obtained by rotating the current element
        by the given `angle` (unit: rad) around the `center`.
        """

        center = np.array(center)
        mat = (translation_matrix(center)
               .dot(rotation_matrix(angle))
               .dot(translation_matrix(-center)))

        return self.set_matrix(mat.dot(self.matrix))

    def translate(self, xy):
        """Translate the element.

        Returns a new element obtained by translating the current element
        by a vector xy
        """
        return self.set_matrix(translation_matrix(xy).dot(self.matrix))

    def scale(self, rx, ry=None, center=[0, 0]):
        """Scale the element.

        Returns a new element obtained by scaling the current element
        by a factor rx horizontally and ry vertically, with fix point `center`.
        If ry is not provided it is assumed that rx=ry.
        """

        ry = rx if (ry is None) else ry
        center = np.array(center)
        mat = (translation_matrix(center)
               .dot(scaling_matrix(rx, ry))
               .dot(translation_matrix(-center)))
        return self.set_matrix(mat.dot(self.matrix))


class Group(Element):
    """
    Class for special Elements made out of a group of other elements which
    will be translated, scaled, rotated, and drawn together.
    These elements can be base elements (circles, squares) or even groups.
    """

    def __init__(self, elements):
        """Initialize."""

        self.elements = elements
        self.matrix = 1.0 * np.eye(3)

    def draw(self, surface):
        """Draw the group to a new context of the given Surface """

        for e in self.elements:
            m = self.matrix
            mi = np.linalg.inv(m)
            new_matrix = m.dot(e.matrix)
            e.set_matrix(new_matrix).draw(surface)


class ColorGradient:
    """ This class is more like a structure to store the data for color gradients

    These gradients are used as sources for filling elements or their borders (see
    parameters `fill` and `stroke` in `shape_elements`).

    Parameters
    ------------
    type
      Type of gradient: "linear" or "radial"

    xy1, xy2, xy3

    stops_colors
      For instance, if you want a blue color then a red color then a green color
      you will write stops_colors=[(0,(1,0,0)), (0.5,(0,1,0)) , (1,(0,0,1))].

    """

    def __init__(self, type, stops_colors, xy1, xy2, xy3=None):
        """Initialize/"""
        self.xy1 = xy1
        self.xy2 = xy2
        self.xy3 = xy3
        self.stops_colors = stops_colors
        if type not in ["radial", "linear"]:
            raise ValueError("unkown gradient type")
        self.type = type

    def set_source(self, ctx):
        """Create a pattern and set it as source for the given context."""
        if self.type == "linear":
            (x1, y1), (x2, y2) = self.xy1, self.xy2
            pat = cairo.LinearGradient(x1, y1, x2, y2)
        elif self.type == "radial":
            (x1, y1), (x2, y2), (x3, y3) = self.xy1, self.xy2, self.xy3
            pat = cairo.RadialGradient(x1, y1, x2, y2, x3, y3)
        for stop, color in self.stops_colors:
            if len(color) == 4:
                pat.add_color_stop_rgba(stop, *color)
            else:
                pat.add_color_stop_rgb(stop, *color)
        ctx.set_source(pat)


class ImagePattern(Element):
    """ Class for images that will be used to fill an element or its contour.

    Parameters
    ------------
    image
      A numpy RGB(A) image.
    pixel_zero
      The coordinates of the pixel of the image that will serve as 0,0 origin
      when filling the element.

    filter
      Determines the method with which the images are resized:
        "best": slow but good quality
        "nearest": takes nearest pixel (can create artifacts)
        "good": Good and faster than "best"
        "bilinear": use linear interpolation
        "fast":fast filter, quality like 'nearest'

    extend
      Determines what happends outside the boundaries of the picture:
      "none", "repeat", "reflect", "pad" (pad= use pixel closest from source)

    """

    def __init__(self, image, pixel_zero=[0, 0], filter="best", extend="none"):
        """Initialize"""
        if isinstance(image, Surface):
            self._cairo_surface = image
        else:
            self._cairo_surface = Surface.from_image(image)._cairo_surface
        self.matrix = translation_matrix(pixel_zero)
        self.filter = filter
        self.extend = extend

    def set_matrix(self, new_mat):
        """ Returns a copy of the element, with a new transformation matrix """
        new = copy(self)
        new.matrix = new_mat
        return new

    def make_cairo_pattern(self):
        pat = cairo.SurfacePattern(self._cairo_surface)
        pat.set_filter({"best": cairo.FILTER_BEST,
                        "nearest": cairo.FILTER_NEAREST,
                        "gaussian": cairo.FILTER_GAUSSIAN,
                        "good": cairo.FILTER_GOOD,
                        "bilinear": cairo.FILTER_BILINEAR,
                        "fast": cairo.FILTER_FAST}[self.filter])

        pat.set_extend({"none": cairo.EXTEND_NONE,
                        "repeat": cairo.EXTEND_REPEAT,
                        "reflect": cairo.EXTEND_REFLECT,
                        "pad": cairo.EXTEND_PAD}[self.extend])

        pat.set_matrix(self._cairo_matrix())

        return pat


for meth in ["scale", "rotate", "translate", "_cairo_matrix"]:
    exec("ImagePattern.%s = Element.%s" % (meth, meth))


def _set_source(ctx, src):
    """ Sets a source before drawing an element.

    The source is what fills an element (or the element's contour).
    If can be of many forms. See the documentation of shape_element for more
    details.

    """
    if isinstance(src, ColorGradient):
        src.set_source(ctx)
    elif isinstance(src, ImagePattern):
        ctx.set_source(src.make_cairo_pattern())
    elif isinstance(src, np.ndarray) and len(src.shape) > 1:
        string = src.to_string()
        surface = cairo.ImageSurface.create_for_data(string)
        set_source(ctx, surface)
    elif len(src) == 4:  # RGBA
        ctx.set_source_rgba(*src)
    else:  # RGB
        ctx.set_source_rgb(*src)


#########################################################################
# BASE ELEMENTS

def shape_element(draw_contour, xy=(0, 0), angle=0, fill=None, stroke=(0, 0, 0),
                  stroke_width=0, line_cap=None, line_join=None):
    """

    Parameters
    ------------

    xy
      vector [x,y] indicating where the Element should be inserted in the
      drawing. Note that for shapes like circle, square, rectangle,
      regular_polygon, the [x,y] indicates the *center* of the element.
      So these elements are centered around 0 by default.

    angle
      Angle by which to rotate the shape. The rotation uses (0,0) as center
      point. Therefore all circles, rectangles, squares, and regular_polygons
      are rotated around their center.

    fill
      Defines wath will fill the element. Default is None (no fill). `fill` can
      be one of the following:
      - A (r,g,b) color tuple, where 0 =< r,g,b =< 1
      - A (r,g,b, a) color tuple, where 0=< r,g,b,a =< 1 (a defines the
        transparency: 0 is transparent, 1 is opaque)
      - A gizeh.ColorGradient object.
      - A gizeh.Surface
      - A numpy image (not implemented yet)

    stroke
      Decides how the stroke (contour) of the element will be filled.
      Same rules as for argument ``fill``. Default is color black

    stroke_width
      Width of the stroke, in pixels. Default is 0 (no apparent stroke)

    line_cap
      The shape of the ends of the stroke: 'butt' or 'round' or 'square'

    line_join
      The shape of the 'elbows' of the contour: 'square', 'cut' or 'round'

    """

    def new_draw(ctx):
        draw_contour(ctx)
        if fill is not None:
            ctx.move_to(*xy)
            _set_source(ctx, fill)
            ctx.fill_preserve()
        if stroke_width > 0:
            ctx.move_to(*xy)
            ctx.set_line_width(stroke_width)
            if line_cap is not None:
                ctx.set_line_cap({"butt":  cairo.LINE_CAP_BUTT,
                                  "round": cairo.LINE_CAP_ROUND,
                                  "square": cairo.LINE_CAP_SQUARE}[line_cap])
            if line_join is not None:
                ctx.set_line_join({"cut":  cairo.LINE_JOIN_BEVEL,
                                   "square": cairo.LINE_JOIN_MITER,
                                   "round": cairo.LINE_JOIN_ROUND}[line_join])
            _set_source(ctx, stroke)
            ctx.stroke_preserve()

    if (angle == 0) and (tuple(xy) == (0, 0)):
        return Element(new_draw)
    elif angle == 0:
        return Element(new_draw).translate(xy)
    elif tuple(xy) == (0, 0):
        return Element(new_draw).rotate(angle)
    else:
        return Element(new_draw).rotate(angle).translate(xy)


def rectangle(lx, ly, **kw):
    return shape_element(lambda c: c.rectangle(-lx / 2, -ly / 2, lx, ly), **kw)


def square(l, **kw):
    return rectangle(l, l, **kw)


def arc(r, a1, a2, **kw):
    return shape_element(lambda c: c.arc(0, 0, r, a1, a2), **kw)


def circle(r, **kw):
    return arc(r, 0, 2 * np.pi, **kw)


def polyline(points, close_path=False, **kw):
    def draw(ctx):
        ctx.move_to(*points[0])
        for p in points[1:]:
            ctx.line_to(*p)
        if close_path:
            ctx.close_path()
    return shape_element(draw, **kw)


def regular_polygon(r, n, **kw):
    points = [polar2cart(r, a) for a in np.linspace(0, 2 * np.pi, n + 1)[:-1]]
    return polyline(points, close_path=True, **kw)


def bezier_curve(points, **kw):
    '''Create cubic Bezier curve

    points
      List of four (x,y) tuples specifying the points of the curve.
    '''
    def draw(ctx):
        ctx.move_to(*points[0])
        ctx.curve_to(*tuple(chain(*points))[2:])
    return shape_element(draw, **kw)


def ellipse(w, h, **kw):
    '''Create an ellipse.

    w, h
      These are used to set the control points for the first quarter
      of the ellipse.
    '''

    # Bezier control points for a quarter of an ellipse.
    ctrl_pnts = [((w / 2), 0), ((w / 2), (h / 2) * (4 / 3) * (sqrt(2) - 1)),
                 ((w / 2) * (4 / 3) * (sqrt(2) - 1), (h / 2)), (0, (h / 2))]

    # Create a list, all_points, which will be populated with lists of control
    # points for 4 Bezier curves that will approximate the ellipse.
    all_points = []
    for i in [1, -1]:
        for j in [1, -1]:
            all_points.append([(pnt[0] * i, pnt[1] * (-j))
                               for pnt in ctrl_pnts])
    # Permutes the last three lists to put the curves in correct order
    all_points.append(all_points.pop(1))
    # Correct the order of the two sublists defining their respective quarter
    # pieces of the ellipse so that the whole ellipse is drawn in order
    all_points[1].reverse()
    all_points[3].reverse()

    def draw(ctx):
        ctx.move_to(*ctrl_pnts[0])
        for points in all_points:
            ctx.curve_to(*tuple(chain(*points))[2:])
        ctx.close_path()

    return shape_element(draw, **kw)


def star(nbranches=5, radius=1.0, ratio=0.5, **kwargs):
    """ This function draws a star with the given number of branches,
    radius, and ratio between branches and body. It accepts the usual
    parameters xy, angle, fill, etc. """

    rr = radius * np.array(nbranches * [1.0, ratio])
    aa = np.linspace(0, 2 * np.pi, 2 * nbranches + 1)[:-1]
    points = polar2cart(rr, aa)
    return polyline(points, close_path=True, **kwargs)


def text(txt, fontfamily, fontsize, fill=(0, 0, 0),
         h_align="center", v_align="center",
         stroke=(0, 0, 0), stroke_width=0,
         fontweight="normal", fontslant="normal",
         angle=0, xy=[0, 0], y_origin="top"):
    """Create a text object.

    Parameters
    -----------

    v_align
      vertical alignment of the text: "top", "center", "bottom"

    h_align
      horizontal alignment of the text: "left", "center", "right"

    fontweight
      "normal" "bold"

    fontslant
      "normal" "oblique" "italic"

    y_origin
      Adapts the vertical orientation of the text to the coordinates system:
      if you are going to export the image with y_origin="bottom" (see for
      instance Surface.write_to_png) then set y_origin to "bottom" here too.

    angle, xy, stroke, stroke_width
      see the doc for ``shape_element``
    """

    fontweight = {"normal": cairo.FONT_WEIGHT_NORMAL,
                  "bold":   cairo.FONT_WEIGHT_BOLD}[fontweight]
    fontslant = {"normal":  cairo.FONT_SLANT_NORMAL,
                 "oblique": cairo.FONT_SLANT_OBLIQUE,
                 "italic":  cairo.FONT_SLANT_ITALIC}[fontslant]

    def draw(ctx):

        ctx.select_font_face(fontfamily, fontslant, fontweight)
        ctx.set_font_size(fontsize)
        xbear, ybear, w, h, xadvance, yadvance = ctx.text_extents(txt)
        xshift = {"left": 0, "center": -w / 2, "right": -w}[h_align] - xbear
        yshift = {"bottom": 0, "center": -h / 2, "top": -h}[v_align] - ybear
        new_xy = np.array(xy) + np.array([xshift, yshift])
        ctx.move_to(*new_xy)
        ctx.text_path(txt)
        _set_source(ctx, fill)
        ctx.fill()
        if stroke_width > 0:
            ctx.move_to(*new_xy)
            ctx.text_path(txt)
            _set_source(ctx, stroke)
            ctx.set_line_width(stroke_width)
            ctx.stroke()

    return (Element(draw).scale(1, 1 if (y_origin == "top") else -1)
            .rotate(angle))
