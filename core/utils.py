import glm
import glfw
import math


class UtilMath:
    @staticmethod
    def clamp(x, min, max):
        return min if x < min else max if x > max else x

    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def smoothstep(x, min, max):
        t = UtilMath.clamp((x - min) / (max - min), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @staticmethod
    def angle_between_vectors(vec1, vec2):
        dotProduct = glm.dot(vec1, vec2)
        mag = glm.length(vec1) * glm.length(vec2)
        if mag == 0:
            return 0
        angle = math.acos(dotProduct / mag)
        
        return angle
    @staticmethod
    def angle_between_camera_and_point(camera_position, camera_rotation_quat, point_position):
        forward_vector = camera_rotation_quat * glm.vec3(0, 0, -1)
        forward_vector = glm.normalize(forward_vector)  
        direction_to_point = glm.normalize(point_position - camera_position)

        cos_angle = glm.dot(forward_vector, direction_to_point)
        angle_rad = glm.acos(cos_angle)  # O ângulo em radianos entre 0 e π (0° a 180°)
        angle_deg = glm.degrees(angle_rad)  # Converter para graus
        

        return angle_deg

    @staticmethod
    def get_angle_weight(v1, v2, v3):
        a = glm.distance2(v2, v3)
        asqrt = math.sqrt(a)
        b = glm.distance2(v1, v3)
        bsqrt = math.sqrt(b)
        c = glm.distance2(v1, v2)
        csqrt = math.sqrt(c)
        if bsqrt * csqrt == 0 or asqrt * csqrt == 0 or bsqrt * asqrt == 0:
            return glm.vec3(1.0, 1.0, 1.0)

        angle1 = math.acos((b + c - a) / (2 * bsqrt * csqrt))
        angle2 = math.acos((-b + c + a) / (2 * asqrt * csqrt))
        angle3 = math.acos((b - c + a) / (2 * bsqrt * asqrt))

        return glm.vec3(angle1, angle2, angle3)


    @staticmethod
    def ray_from_mouse(mouse_x, mouse_y, viewport_width, viewport_height, view_matrix, projection_matrix):
        # Convertendo coordenadas de tela para NDC (Normalized Device Coordinates)
        x = (2.0 * mouse_x) / viewport_width - 1.0
        y = 1.0 - (2.0 * mouse_y) / viewport_height
        
        near_point = glm.vec4(x, y, -1.0, 1.0)
        far_point = glm.vec4(x, y, 1.0, 1.0)
        

        inv_projection = glm.inverse(projection_matrix)
        inv_view = glm.inverse(view_matrix)
        
        near_world = inv_view * inv_projection * near_point
        far_world = inv_view * inv_projection * far_point
        

        if near_world.w != 0:
            near_world /= near_world.w
        if far_world.w != 0:
            far_world /= far_world.w
        

        ray_direction = glm.normalize(glm.vec3(far_world - near_world))
        
        return ray_direction
    
    @staticmethod
    def ray_intersect_triangle(ray_origin, ray_direction, v0, v1, v2):
        epsilon = 1e-8
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = glm.cross(ray_direction, edge2)
        a = glm.dot(edge1, h)
        
        if -epsilon < a < epsilon:
            return False, 0.0    
        
        f = 1.0 / a
        s = ray_origin - v0
        u = f * glm.dot(s, h)
        
        if u < 0.0 or u > 1.0:
            return False, 0.0 
        
        q = glm.cross(s, edge1)
        v = f * glm.dot(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return False, 0.0 
        
        t = f * glm.dot(edge2, q)
        
        if t > epsilon:
            return True, t   
            
        return False, 0.0   

    @staticmethod
    def project_to_infinity(vertex, light_position, infinity):
        direction = glm.normalize(vertex - light_position)
        return vertex + direction * infinity
    
    @staticmethod
    def are_equal(v1, v2, epsilon=1e-5):
        return glm.all(glm.epsilonEqual(v1, v2, epsilon))
    
    @staticmethod
    def is_front_facing(v0, v1, v2, light_direction):
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = glm.normalize(glm.cross(edge1, edge2))
        dot_product = glm.dot(normal, glm.normalize(light_direction))
        return dot_product > 0.0
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
    


class Frustum:
    def __init__(self):
        self.planes = [Plane3D(glm.vec3(0)) for _ in range(6)]  # 6 planos: Left, Right, Bottom, Top, Near, Far

    def update(self, proj_view_matrix):
        self.planes[0] = self.extract_plane(proj_view_matrix, 0, 3, -1)  # Left
        self.planes[1] = self.extract_plane(proj_view_matrix, 0, 3, 1)   # Right
        self.planes[2] = self.extract_plane(proj_view_matrix, 1, 3, -1)  # Bottom
        self.planes[3] = self.extract_plane(proj_view_matrix, 1, 3, 1)   # Top
        self.planes[4] = self.extract_plane(proj_view_matrix, 2, 3, -1)  # Near
        self.planes[5] = self.extract_plane(proj_view_matrix, 2, 3, 1)   # Far

        for plane in self.planes:
            plane.normalize()

    def get_left(self):
        return self.planes[0]

    def get_right(self):
        return self.planes[1]

    def get_bottom(self):
        return self.planes[2]

    def get_top(self):
        return self.planes[3]

    def get_near(self):
        return self.planes[4]

    def get_far(self):
        return self.planes[5]

    @staticmethod
    def extract_plane(matrix, row, column, sign):
        plane = Plane3D(glm.vec3(0))
        
        plane.normal.x = matrix[0][3] + sign * matrix[0][row]
        plane.normal.y = matrix[1][3] + sign * matrix[1][row]
        plane.normal.z = matrix[2][3] + sign * matrix[2][row]
        plane.distance = matrix[3][3] + sign * matrix[3][row]

        return plane

    def is_point_in_frustum(self, point):
        for plane in self.planes:
            if glm.dot(plane.normal, point) + plane.distance < 0:
                return False
        return True

    def is_sphere_in_frustum(self, center, radius):
        for plane in self.planes:
            distance = glm.dot(plane.normal, center) + plane.distance
            if distance < -radius:
                return False
            elif distance < radius:
                return True  # Intersecting
        return True  # Fully inside

    def is_box_in_frustum(self, min_point, max_point):
        for plane in self.planes:
            p = glm.vec3(
                max_point.x if plane.normal.x >= 0 else min_point.x,
                max_point.y if plane.normal.y >= 0 else min_point.y,
                max_point.z if plane.normal.z >= 0 else min_point.z
            )
            n = glm.vec3(
                min_point.x if plane.normal.x >= 0 else max_point.x,
                min_point.y if plane.normal.y >= 0 else max_point.y,
                min_point.z if plane.normal.z >= 0 else max_point.z
            )
            
            if glm.dot(plane.normal, p) + plane.distance < 0:
                return False
            elif glm.dot(plane.normal, n) + plane.distance < 0:
                return True  # Intersecting
        return True  # Fully inside


class Ray3D:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
    
    def set(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def __str__(self):
        return f"Ray3D(origin={self.origin}, direction={self.direction})"
    
    def intersects_min_max(self, minimum, maximum):
        d = 0.0
        max_value = float('inf')
        
        # Verifica o eixo X
        if abs(self.direction.x) < 1e-7:
            if self.origin.x < minimum.x or self.origin.x > maximum.x:
                return False
        else:
            inv = 1.0 / self.direction.x
            min_val = (minimum.x - self.origin.x) * inv
            max_val = (maximum.x - self.origin.x) * inv
            
            if max_val == float('-inf'):
                max_val = float('inf')
            
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            
            d = max(min_val, d)
            max_value = min(max_val, max_value)
            
            if d > max_value:
                return False
        
        # Verifica o eixo Y
        if abs(self.direction.y) < 1e-7:
            if self.origin.y < minimum.y or self.origin.y > maximum.y:
                return False
        else:
            inv = 1.0 / self.direction.y
            min_val = (minimum.y - self.origin.y) * inv
            max_val = (maximum.y - self.origin.y) * inv
            
            if max_val == float('-inf'):
                max_val = float('inf')
            
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            
            d = max(min_val, d)
            max_value = min(max_val, max_value)
            
            if d > max_value:
                return False
        
        # Verifica o eixo Z
        if abs(self.direction.z) < 1e-7:
            if self.origin.z < minimum.z or self.origin.z > maximum.z:
                return False
        else:
            inv = 1.0 / self.direction.z
            min_val = (minimum.z - self.origin.z) * inv
            max_val = (maximum.z - self.origin.z) * inv
            
            if max_val == float('-inf'):
                max_val = float('inf')
            
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            
            d = max(min_val, d)
            max_value = min(max_val, max_value)
            
            if d > max_value:
                return False
        
        return True

    def intersects_box(self, box):
        return self.intersects_min_max(box.min, box.max)
    
    @staticmethod
    def create_from_2d(mouse_x, mouse_y, width, height,  view_matrix, projection_matrix):
        screen_x = mouse_x
        screen_y = height - mouse_y
        start = glm.unProject(glm.vec3(screen_x, screen_y, 0.0),  view_matrix, projection_matrix, glm.vec4(0,0, width, height))
        end   = glm.unProject(glm.vec3(screen_x, screen_y, 1.0),  view_matrix, projection_matrix, glm.vec4(0,0, width, height))
        direction = glm.normalize(end - start)
        return Ray3D(start, direction)



class BoundingBox:
    def __init__(self):
        self.min = glm.vec3(float('inf'), float('inf'), float('inf'))
        self.max = glm.vec3(float('-inf'), float('-inf'), float('-inf'))

    def get_center(self):
        return (self.min + self.max) * 0.5
    
    def get_edges(self):
        middle = self.get_center()
        diag = glm.vec3(self.max.x - middle.x, self.max.y - middle.y, self.max.z - middle.z)
        edges = []
        edges.append( glm.vec3(middle.x + diag.x, middle.y + diag.y, middle.z + diag.z))
        edges.append( glm.vec3(middle.x + diag.x, middle.y - diag.y, middle.z + diag.z))
        edges.append( glm.vec3(middle.x + diag.x, middle.y + diag.y, middle.z - diag.z))
        edges.append( glm.vec3(middle.x + diag.x, middle.y - diag.y, middle.z - diag.z))
        edges.append( glm.vec3(middle.x - diag.x, middle.y + diag.y, middle.z + diag.z))
        edges.append( glm.vec3(middle.x - diag.x, middle.y - diag.y, middle.z + diag.z))
        edges.append( glm.vec3(middle.x - diag.x, middle.y + diag.y, middle.z - diag.z))
        edges.append( glm.vec3(middle.x - diag.x, middle.y - diag.y, middle.z - diag.z))
        return edges
        
    def transform(self, matrix):
        box = BoundingBox()
        corners = self.get_edges()
        #box.clear(corners[0])
        for c in corners:
            point = matrix * c
            box.add_point(point.x,point.y,point.z)
        return box

    def clear(self,point):
        self.min = point
        self.max = point
        
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

    def add(self,box):
        if box.min.x<self.min.x: 
            self.min.x = box.min.x
        if box.min.y<self.min.y: 
            self.min.y = box.min.y
        if box.min.z<self.min.z: 
            self.min.z = box.min.z
        if box.max.x>self.max.x: 
            self.max.x = box.max.x
        if box.max.y>self.max.y: 
            self.max.y = box.max.y
        if box.max.z>self.max.z: 
            self.max.z = box.max.z
    
    def merge(self,box):
        self.add(box)

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


