from copy import deepcopy
from decorator import decorator
import numpy as np
import cairo

# GEOMETRY

def rotation_matrix(a):
    return np.array([[np.cos(a),  -np.sin(a),0],
                      [np.sin(a),  np.cos(a),0],
                      [0,          0 ,       1.0]])

def translation_matrix(xy):
    return np.array([[1.0,0,xy[0]],
                     [0,1,xy[1]],
                     [0,0,1]])

def scaling_matrix(sx,sy):
    return np.array([[sx,0,0],
                     [0,sy,0],
                     [0,0,1]])

class Element:
    
    def __init__(self, draw_method):
        self.draw_method = draw_method
        self.matrix = np.eye(3)

    def transform_ctx(self, ctx):
        m = self.matrix
        ctx.transform(cairo.Matrix(m[0,0],m[0,1],
                                   m[1,0],m[1,1],
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
            new_matrix = self.matrix.dot(e.matrix)
            e.set_matrix(new_matrix).draw(surface)


class Surface:

    def __init__(self, width,height):
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)

    def new_context(self):
        return cairo.Context(self.surface)

    def get_npimage(self):
        im = 0+np.frombuffer(self.surface.get_data(), np.uint8)
        im.shape = (self.height, self.width, 4)
        return im[:,:,:3]

    def write_to_png(self, filename):
        self.surface.write_to_png(filename)



def shape_element(draw, xy=(0,0), angle=0, fill_color=None,
             stroke_color=(0,0,0), stroke_width=0):
    
    def new_draw(ctx):
        if fill_color is not None:
                draw(ctx)
                ctx.set_source_rgb(*fill_color)
                ctx.fill()
        if stroke_width > 0:
                draw(ctx)
                ctx.set_line_width(stroke_width)
                ctx.set_source_rgb(*stroke_color)
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


def line(points, **kw):
    return shape_element(lambda c:c.arc(0,0, r, a1, a2), **kw)

def bezier(points, **kw):
    return shape_element(lambda c:c.arc(0,0, r, a1, a2), **kw)