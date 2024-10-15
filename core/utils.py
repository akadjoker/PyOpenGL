import glm
import math  

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def set(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x, y):
        return x >= self.x and x < self.x + self.width and y >= self.y and y < self.y + self.height
    
    def intersects(self, other):
        return not (self.x > other.x + other.width or self.x + self.width < other.x or self.y > other.y + other.height or self.y + self.height < other.y)

class BoundingBox:
    def __init__(self):
        self.min =glm.vec3(0,0,0)
        self.max =glm.vec3(0,0,0)
    
    def add_point(self, point):
        if self.min.x > point.x:
            self.min.x = point.x
        if self.min.y > point.y:
            self.min.y = point.y
        if self.min.z > point.z:
            self.min.z = point.z
        if self.max.x < point.x:
            self.max.x = point.x
        if self.max.y < point.y:
            self.max.y = point.y
        if self.max.z < point.z:
            self.max.z = point.z