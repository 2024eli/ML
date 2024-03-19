from sys import argv
import cv2
from math import sin, cos, tan, atan
from numpy import array, cross
from numpy.linalg import solve, norm

#GLOBALS
FOV = (0.9, 1.255) #(0.9, 1.255) for portrait --> (1.255, 0.9) for landscape
DISPLACEMENT = [0, 2, 0]
file1, file2 = argv[1:3]
points = []

def spherical_to_cartesian(rho, phi, theta): #(rho, phi, theta) --> (x,y,z)
    return (rho * cos(phi) * cos(theta), rho * cos(phi) * sin(theta), rho * sin(phi))

def intersection(v1, v2):
    X, Y = x,y # of the image
    T, P = FOV # (theta, phi) in the spherical plane
    A = X / 2 / tan(T / 2) # accounting for the distortion from FOV
    B = Y / 2 / tan(P / 2) # accounting for the distortion from FOV

    x1, y1 = v1 # point 1
    x2, y2 = v2 # point 2

    # accounting for image size
    x1 = x1 - X/2
    y1 = -y1 + Y/2
    x2 = x2 - X/2
    y2 = -y2 + Y/2

    #theta and phi accordingly using coordinates and FOV adjustments
    t1 = -atan(x1 / A)
    p1 = atan(y1 / B)
    t2 = -atan(x2 / A)
    p2 = atan(y2 / B)

    # define lines A and B by two points
    XB0 = (XA0:=array([0, 0, 0])) + + array(DISPLACEMENT) 

    UA = array(spherical_to_cartesian(1, p1, t1))
    UB = array(spherical_to_cartesian(1, p2, t2))
    UC = (c:=cross(UB, UA))/norm(c)

    RHS = array(DISPLACEMENT) 
    LHS = array([UA, -UB, UC]).T
    t1, t2, _ = solve(LHS, RHS)

    return (XA0 + t1 * UA + XB0 + t2 * UB) / 2

#to find the lights
def findCenters(filename):
    img = cv2.imread(filename)

    #preprocessing
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = int(cv2.minMaxLoc(grey)[1] * 0.7)  # in pix value to be extracted
    _, thresh = cv2.threshold(grey, thresh, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) #finding contours

    regions = [cv2.boundingRect(c) for c in contours] # getting measurements
    centers = [[x + (w / 2), y + (h / 2)] for x,y,w,h in regions] #calculating centers

    return centers, (img.shape[0], img.shape[1])

#main
centers1, (x,y) = findCenters(file1) #list of centers, (dimension, dimension)
centers2, (x,y) = findCenters(file2)

# sort based on first value
centers1.sort(key = lambda v : v[0])
centers2.sort(key = lambda v : v[0])

#organizing the pairs so it's readable for the intersection function
pairs = [pair for rightGroup, leftGroup in zip([centers1],[centers2]) for pair in zip(rightGroup, leftGroup)]

intersections_forward = [intersection(*p) for p in pairs]
print("\nIntersections for this ONE light ------")
for i, ch in enumerate(["+x (forward)", "+y (left)", "+z (up)"]):
    print(f"{ch}: {intersections_forward[0][i]}")
print(f'\nNumber of lights: 1')