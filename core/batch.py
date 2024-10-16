from enum import Enum
import numpy as np
from OpenGL.GL import *
import math

PI = 3.14159265
PI2 = 2*3.14159265
PI_2 = 3.14159265/2
PI_3 = 3.14159265/3
PI_4 = 3.14159265/4
HALF_PI = PI / 2
DEG2RAD = PI / 180.0
RAD2DEG = 180.0 / PI

def RAD(d):
      return -d*PI/180.0
def DEG(r):
     return -r*180.0/PI

def toRadians(degrees):
    return degrees * PI / 180.0


def toDegrees(radians):
	return radians * 180.0 / PI


def constrain(value, min_value, max_value):
    return min(max(value, min_value), max_value)

def point_in_circle(x, y, cx, cy, r):
    return (x - cx) * (x - cx) + (y - cy) * (y - cy) < r * r

def point_in_rect(x, y, rx, ry, rw, rh):
    return x >= rx and x <= rx + rw and y >= ry and y <= ry + rh

def rect_in_rect(x, y, w, h, rx, ry, rw, rh):
    return x + w >= rx and x <= rx + rw and y + h >= ry and y <= ry + rh

def circle_in_circle(x1, y1, r1, x2, y2, r2):
    return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) < (r1 + r2) * (r1 + r2)

def circle_in_rect(x, y, r, rx, ry, rw, rh):
    test_x = x
    test_y = y
    if x < rx:
        test_x = rx
    elif x > rx + rw:
        test_x = rx + rw
    if y < ry:
        test_y = ry
    elif y > ry + rh:
        test_y = ry + rh
    return distance(x, y, test_x, test_y) < r

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
