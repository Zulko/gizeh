import numpy as np



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

def polar_polygon(nfaces,radius, npoints):
    theta=np.linspace(0,2*np.pi,npoints)[:-1]
    cos, pi, n = np.cos, np.pi, nfaces
    r= cos( pi/n )/cos((theta%(2*pi/n))-pi/n)
    d = np.cumsum(np.sqrt(((r[1:]-r[:-1])**2)))
    d = [0]+list(d/d.max())
    return zip(radius*r, theta, d)

def polar2cart(r,theta):
    return r*np.array([np.cos(theta), np.sin(theta)])