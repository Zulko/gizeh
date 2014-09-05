import numpy as np


def polar_polygon(nfaces,radius, npoints):
    theta=np.linspace(0,2*np.pi,npoints)[:-1]
    cos, pi, n = np.cos, np.pi, nfaces
    r= cos( pi/n )/cos((theta%(2*pi/n))-pi/n)
    d = np.cumsum(np.sqrt(((r[1:]-r[:-1])**2)))
    d = [0]+list(d/d.max())
    return zip(radius*r, theta, d)

def polar2cart(r,theta):
    return r*np.array([np.cos(theta), np.sin(theta)])