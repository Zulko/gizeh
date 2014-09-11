from copy import deepcopy
from base64 import b64encode
import numpy as np
import cairo
from decorator import decorator
from .geometry import (rotation_matrix,
                       translation_matrix,
                       scaling_matrix,
                       polar2cart)


class Element:
    
    def __init__(self, draw_method):
        self.draw_method = draw_method
        self.matrix = 1.0*np.eye(3)

    def transform_ctx(self, ctx):
        m = self.matrix
        ctx.set_matrix(cairo.Matrix(m[0,0],m[1,0], 
                                   m[0,1],m[1,1],
                                   m[0,2], m[1,2]))
    
    def draw(self, surface):
        ctx = surface.new_context()
        self.transform_ctx(ctx)
        self.draw_method(ctx)
    
    def set_matrix(self, new_mat):
        new = deepcopy(self)
        new.matrix = new_mat
        return new

    def rotate(self, angle, center=[0,0]):
        center=np.array(center)
        mat = (translation_matrix(center)
               .dot(rotation_matrix(angle))
               .dot(translation_matrix(-center)))
        
        return self.set_matrix(mat.dot(self.matrix))
        
    
    def translate(self, xy):
        return self.set_matrix(translation_matrix(xy).dot(self.matrix))

    def scale(self, rx, ry=None, center=[0,0]):
        ry = rx if (ry is None) else ry
        center=np.array(center)
        mat = (translation_matrix(center)
               .dot(scaling_matrix(rx,ry))
               .dot(translation_matrix(-center)))
        return self.set_matrix(mat.dot(self.matrix))


class Group(Element):

    def __init__(self, elements):

        self.elements=elements
        self.matrix = 1.0*np.eye(3)

    def draw(self,surface):

        for e in self.elements:
            m = self.matrix
            mi = np.linalg.inv(m)
            new_matrix = m.dot(e.matrix)
            e.set_matrix(new_matrix).draw(surface)


class Surface:

    def __init__(self, width,height):
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)

    def new_context(self):
        return cairo.Context(self.surface)

    def write_to_png(self, filename, y_origin="up"):

        if y_origin == "bottom":
            W,H = self.width, self.height
            new_surface = Surface(W,H)
            rect = rectangle(2*W,2*H, fill=self).scale(1,-1).translate([0,H])
            rect.draw(new_surface)
            new_surface.write_to_png(filename, y_origin="up")
        else:
            self.surface.write_to_png(filename)

    def get_npimage(self, transparent=False, y_origin="up"):
        im = 0+np.frombuffer(self.surface.get_data(), np.uint8)
        im.shape = (self.height, self.width, 4)
        if y_origin== "bottom":
            im = im[::-1]
        return im if transparent else im[:,:, :3]

    def get_html_embed_code(self, y_origin="up"):
        self.write_to_png("__temp__.png", y_origin=y_origin)
        with open("__temp__.png", "rb") as f:
            data= b64encode(f.read())
        return "<center><img  src='data:image/png;base64,%s'></center>"%(data)

    def ipython_display(self, y_origin="up"):
        from IPython.display import HTML
        return HTML(self.get_html_embed_code(y_origin=y_origin))



class ColorGradient:
    def __init__(self, type, stops_colors, xy1, xy2, xy3=None):
        self.xy1 = xy1
        self.xy2 = xy2
        self.xy3= xy3
        self.stops_colors = stops_colors
        if type not in ["radial", "linear"]:
            raise ValueError("unkown gradient type")
        self.type = type



def set_source(ctx, src):
    if isinstance(src, ColorGradient):
        if src.type == "linear":
            (x1, y1), (x2, y2) = src.xy1, src.xy2
            pat = cairo.LinearGradient(x1, y1, x2, y2)
        elif src.type == "radial":
            (x1, y1), (x2, y2), (x2,y3) = src.xy1, src.xy2, src.xy3
            pat = cairo.RadialGradient(x1, y1, x2, y2, x3, y3)
        for stop, color in src.stops_colors:
            if len(color)==4:
                pat.add_color_stop_rgba(stop, *color)
            else:
                pat.add_color_stop_rgb(stop, *color)
        ctx.set_source(pat)
    elif isinstance(src, Surface):
        pat = cairo.SurfacePattern(src.surface)
        ctx.set_source(pat)
    elif isinstance(src, np.ndarray):
        string = src.to_string()
        surface = cairo.ImageSurface.create_for_data(string)
        set_source(ctx, surface)
    elif len(src)==4: # RGBA
        ctx.set_source_rgba(*src)
    else: # RGB
        ctx.set_source_rgb(*src)


def shape_element(draw, xy=(0,0), angle=0, fill=None,
             stroke=(0,0,0), stroke_width=0):
    
    def new_draw(ctx):
        if fill is not None:
                draw(ctx)
                ctx.move_to(*xy)
                set_source(ctx, fill)
                ctx.fill()
        if stroke_width > 0:
                draw(ctx)
                ctx.move_to(*xy)
                ctx.set_line_width(stroke_width)
                set_source(ctx, stroke)
                ctx.stroke()

    return Element(new_draw).rotate(angle).translate(xy)


def rectangle(lx, ly, **kw):
    return shape_element(lambda c:c.rectangle(-lx/2, -ly/2, lx, ly), **kw)

def square(l, **kw):
    return rectangle(l,l, **kw)

def arc(r, a1, a2, **kw):
    return shape_element(lambda c:c.arc(0,0, r, a1, a2), **kw)

def circle(r,**kw):
    return arc(r, 0, 2*np.pi, **kw)

def text(r,**kw):
    return arc(r, 0, 2*np.pi, **kw)

def polyline(points, **kw):
    def draw(ctx):
        ctx.move_to(*points[0])
        for p in points[1:]:
            ctx.line_to(*p)
    return shape_element(draw, **kw)

def polygon(r,n, **kw):
    points = [polar2cart(r, a) for a in np.linspace(0,2*np.pi,n+1)]
    return polyline(points, **kw)

def bezier(points, **kw):
    return shape_element(lambda c:c.arc(0,0, r, a1, a2), **kw)


def text(txt, fontfamily, fontsize, fill=(0,0,0),
         h_align = "center", v_align = "center",
         stroke=(0,0,0), stroke_width=0,
         fontweight="normal", fontslant="normal",
         angle=0, xy=[0,0], y_origin="up"):
    """
    fontweight
      "normal" "bold"
    
    fontslant
      "normal" "oblique" "italic"
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
        xshift = {"left":0, "center":-w/2, "right":-w}[h_align] - xbear
        yshift = {"bottom":0, "center":-h/2, "top":-h}[v_align] - ybear
        new_xy = np.array(xy) + np.array([xshift, yshift])
        ctx.move_to(*new_xy)
        ctx.text_path(txt)
        set_source(ctx, fill)
        ctx.fill() 
        if stroke_width > 0:
            ctx.move_to(*new_xy)
            ctx.text_path(txt)
            set_source(ctx, stroke)
            ctx.set_line_width(stroke_width)
            ctx.stroke()
    return (Element(draw).scale(1,1 if (y_origin=="up") else -1)
            .rotate(angle))