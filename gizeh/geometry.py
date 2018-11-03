import numpy as np


def rotation_matrix(a):
    """Return a 3x3 2D geometric rotation matrix"""
    return np.array([[np.cos(a),  -np.sin(a), 0],
                     [np.sin(a),  np.cos(a), 0],
                     [0, 0, 1.0]])


def translation_matrix(xy):
    """Return a 3x3 2D geometric translation matrix"""
    return np.array([[1.0, 0, xy[0]],
                     [0, 1, xy[1]],
                     [0, 0, 1]])


def scaling_matrix(sx, sy):
    """Return a 3x3 geometric scaling matrix"""
    return np.array([[sx, 0, 0],
                     [0, sy, 0],
                     [0, 0, 1]])


def polar_polygon(nfaces, radius, npoints):
    """ Returns the (x,y) coordinates of n points regularly spaced
    along a regular polygon of `nfaces` faces and given radius.
    """
    theta = np.linspace(0, 2 * np.pi, npoints)[:-1]
    cos, pi, n = np.cos, np.pi, nfaces
    r = cos(pi / n) / cos((theta % (2 * pi / n)) - pi / n)
    d = np.cumsum(np.sqrt(((r[1:] - r[:-1])**2)))
    d = [0] + list(d / d.max())
    return zip(radius * r, theta, d)


def polar2cart(r, theta):
    """ Transforms polar coodinates into cartesian coordinates (x,y).
    If r or theta or both are vectors, returns a np. array of the list
    [(x1,y1),(x2,y2),etc...]
    """

    res = r * np.array([np.cos(theta), np.sin(theta)])
    return res if len(res.shape) == 1 else res.T
