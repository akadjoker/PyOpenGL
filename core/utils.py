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
        self.min = glm.vec3(float('inf'), float('inf'), float('inf'))
        self.max = glm.vec3(float('-inf'), float('-inf'), float('-inf'))



    def reset(self):
        self.min = glm.vec3(float('inf'), float('inf'), float('inf'))
        self.max = glm.vec3(float('-inf'), float('-inf'), float('-inf'))
    
    def add_point(self, x,y,z):
        if self.min.x > x:
            self.min.x = x
        if self.min.y > y:
            self.min.y = y
        if self.min.z > z:
            self.min.z = z
        if self.max.x < x:
            self.max.x = x
        if self.max.y < y:
            self.max.y = y
        if self.max.z < z:
            self.max.z = z