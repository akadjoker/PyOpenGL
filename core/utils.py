import glm
import glfw
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

    def __str__(self):
        return f"Rectangle(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def contains(self, x, y):
        return x >= self.x and x < self.x + self.width and y >= self.y and y < self.y + self.height
    
    def intersects(self, other):
        return not (self.x > other.x + other.width or self.x + self.width < other.x or self.y > other.y + other.height or self.y + self.height < other.y)





class Plane3D:
    def __init__(self, normal, distance=0):
        self.normal = normal
        self.distance = distance

    def normalize(self):
        mag = glm.length(self.normal)
        if mag > 0:
            self.normal /= mag
            self.distance /= mag
        return self

    @staticmethod
    def from_points(v0, v1, v2):
        edge1 = v1 - v0
        edge2 = v2 - v0

        normal = glm.cross(edge1, edge2)
        normal = glm.normalize(normal)
        d = -glm.dot(v0, v0)
        return Plane3D(normal, d)



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

class Quad:
    def __init__(self, x, y, t, v):
        self.x = x
        self.y = y
        self.tx = t
        self.ty = v

class Timer:
    def __init__(self):
        self.start_time = glfw.get_time()  
        self.paused_time = 0.0             
        self.pause_start = 0.0             
        self.is_paused = False              
        self.last_time = self.start_time  

    def reset(self):
        self.start_time = glfw.get_time()
        self.paused_time = 0.0
        self.pause_start = 0.0
        self.is_paused = False
        self.last_time = self.start_time

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = glfw.get_time()

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self.paused_time += glfw.get_time() - self.pause_start

    def get_time(self):
        if self.is_paused:
            return self.pause_start - self.start_time - self.paused_time
        else:
            return glfw.get_time() - self.start_time - self.paused_time

    def get_delta_time(self):
        current_time = self.get_time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        return delta_time


class FPSCounter:
    def __init__(self):
        self.timer = Timer()   
        self.frame_count = 0   
        self.fps = 0.0         
        self.elapsed_time = 0.0

    def update(self):
        delta_time = self.timer.get_delta_time()
        self.elapsed_time += delta_time
        self.frame_count += 1
        if self.elapsed_time >= 1.0:
            self.fps = self.frame_count / self.elapsed_time 
            self.frame_count = 0
            self.elapsed_time = 0.0

    def get_fps(self):
        return self.fps









def rotate_point(px, py, cx, cy, angle):
    cos_theta = math.cos(math.radians(angle))
    sin_theta = math.sin(math.radians(angle))
    dx = px - cx
    dy = py - cy
    return (cx + cos_theta * dx - sin_theta * dy, cy + sin_theta * dx + cos_theta * dy)



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


def create_rectangle_atlas( width, height, count_x, count_y):
    w = width / count_x
    h = height / count_y
    bounds = []
    for y in range(count_y):
        for x in range(count_x):
            bounds.append(Rectangle(x * w, y * h, w, h))
    return bounds

def get_matrix_2d(position_x, position_y, scale_x, scale_y, angle, pivot_x, pivot_y):
    m_origin = glm.translate(glm.mat4(1.0), glm.vec3(-position_x, -position_y, 0.0))
    m_rotation = glm.rotate(glm.mat4(1.0), glm.radians(angle), glm.vec3(0.0, 0.0, 1.0))
    m_scale = glm.scale(glm.mat4(1.0), glm.vec3(scale_x, scale_y, 1.0))
    m_translation = glm.translate(glm.mat4(1.0), glm.vec3(pivot_x, pivot_y, 0.0))
    return m_translation * m_rotation * m_scale * m_origin


