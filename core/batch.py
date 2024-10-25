from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core import *
from .texture import Texture

import math

import ctypes

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


INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000
class Batch:
    def __init__(self, maxVertex):
        self.maxVertex = maxVertex
        self.stride = 7  # 3 para posição, 4 para cor
        self.vertices = [0.0] * (maxVertex * self.stride)
        self.totalAlloc =  len(self.vertices) // 7
        self.vertexCount = 0
        self.count = 0
        self.color_r = 1.0
        self.color_g = 1.0
        self.color_b = 1.0
        self.color_a = 1.0
        self.depth = 0.05
        self.clip_enabled = False
        self.clip_rect = [0, 0, 0, 0]
        self.shader = Render.get_shader("solid")
        self.init()

    def init(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * 4, None, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.stride * 4, None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.stride * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

    def _flush(self):
        self.count = 0
        self.vertexCount = 0


    def render(self):
        if self.vertexCount == 0:
            return

        self._flush()




    def vertex3f(self, x, y, z):
        if self.count >= self.totalAlloc:
            self._flush()
        self.vertices[self.count] = x
        self.vertices[self.count + 1] = y
        self.vertices[self.count + 2] = z
        self.vertices[self.count + 3] = self.color_r
        self.vertices[self.count + 4] = self.color_g
        self.vertices[self.count + 5] = self.color_b
        self.vertices[self.count + 6] = self.color_a

        self.count += self.stride
        self.vertexCount += 1

    def color4f(self, r, g, b, a=1.0):
        self.color_r = r
        self.color_g = g
        self.color_b = b
        self.color_a = a

    def color3f(self, r, g, b):
        self.color_r = r
        self.color_g = g
        self.color_b = b



    def line3d(self, x1, y1, z1, x2, y2, z2):
        self.vertex3f(x1, y1, z1)
        self.vertex3f(x2, y2, z2)
        
    
    def line3dv(self, v0, v1):
        self.line3d(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z)



    def set_clip(self, x, y, width, height):
        self.clip_enabled = True
        self.clip_rect = [x, y, x + width, y + height]

    def enable_clip(self,value):
        self.clip_enabled = value
    
    def set_rgb(self, r, g, b):
        self.color_r = r
        self.color_g = g
        self.color_b = b
    def set_alpha(self, a):
        self.color_a = a
    def set_color(self, color):
        self.color_r = color.data[0]
        self.color_g = color.data[1]
        self.color_b = color.data[2]
        self.color_a = color.data[3]


class LinesBatch(Batch):
    def __init__(self, maxVertex):
        super().__init__(maxVertex)


    def triangle2d(self, x0, y0, x1, y1, x2, y2):
        self.line2d(x0, y0, x1, y1)
        self.line2d(x1, y1, x2, y2)
        self.line2d(x2, y2, x0, y0)

    def rectangle(self, x, y, width, height):
        self.triangle2d(x + width, y + height, x + width, y, x, y)
        self.triangle2d(x, y, x, y + height, x + width, y + height)

    def circle(self, x, y, radius, segments=36):
        angle_increment = 2 * math.pi / segments
        prev_x = x + radius
        prev_y = y
        for i in range(1, segments + 1):
            angle = i * angle_increment
            new_x = x + radius * math.cos(angle)
            new_y = y + radius * math.sin(angle)
            self.line2d(prev_x, prev_y, new_x, new_y)
            prev_x, prev_y = new_x, new_y

    
    def grid(self, slices, spacing, axes=False):
        if axes:
            self.set_color(RED)
            self.line3d(0,0.5,0,1,0.5,0)
            self.set_color(BLUE)
            self.line3d(0,0.5,0,0,1.5,0)
            self.set_color(GREEN)
            self.line3d(0,0.5,0,0,0.5,1)
        half = slices // 2
        for i in range(-half, half + 1):
            if i==0:
                self.set_rgb(0.5, 0.5, 0.4)
            else:
                self.set_rgb(0.75, 0.75, 0.75)
            self.line3d(i * spacing, 0, -half * spacing, i * spacing, 0, half * spacing)
            self.line3d(-half * spacing, 0, i * spacing, half * spacing, 0, i * spacing)
    def cube(self,x, y, z, size):
        
        self.line3d(x, y, z, x + size, y, z)
        self.line3d(x, y, z, x, y + size, z)
        self.line3d(x, y, z, x, y, z + size)
        self.line3d(x + size, y, z, x + size, y + size, z)
        self.line3d(x + size, y, z, x + size, y, z + size)
        self.line3d(x, y + size, z, x + size, y + size, z)
        self.line3d(x, y + size, z, x, y + size, z + size)
        self.line3d(x, y, z + size, x + size, y, z + size)
        self.line3d(x, y, z + size, x, y + size, z + size)
        self.line3d(x + size, y + size, z, x + size, y + size, z + size)
        self.line3d(x + size, y + size, z, x, y + size, z + size)
        self.line3d(x + size, y + size, z + size, x, y + size, z + size)
        self.line3d(x + size, y + size, z + size, x + size, y, z + size)
    
    def sphere(self,x, y, z, radius, num_lines=12):
            segments = num_lines // 2
            step = math.pi / segments

            # Linhas longitudinais
            for lat in range(-segments, segments + 1):
                lat_angle = lat * step
                for lon in range(0, num_lines + 1):
                    lon_angle = lon * step
                    x1 = x + radius * math.cos(lat_angle) * math.cos(lon_angle)
                    y1 = y + radius * math.cos(lat_angle) * math.sin(lon_angle)
                    z1 = z + radius * math.sin(lat_angle)

                    lon_angle_next = (lon + 1) * step
                    x2 = x + radius * math.cos(lat_angle) * math.cos(lon_angle_next)
                    y2 = y + radius * math.cos(lat_angle) * math.sin(lon_angle_next)
                    z2 = z + radius * math.sin(lat_angle)

                    self.line3d(x1, y1, z1, x2, y2, z2)

            # Linhas latitudinais
            for lon in range(0, num_lines + 1):
                lon_angle = lon * step
                for lat in range(-segments, segments + 1):
                    lat_angle = lat * step
                    x1 = x + radius * math.cos(lat_angle) * math.cos(lon_angle)
                    y1 = y + radius * math.cos(lat_angle) * math.sin(lon_angle)
                    z1 = z + radius * math.sin(lat_angle)

                    lat_angle_next = (lat + 1) * step
                    x2 = x + radius * math.cos(lat_angle_next) * math.cos(lon_angle)
                    y2 = y + radius * math.cos(lat_angle_next) * math.sin(lon_angle)
                    z2 = z + radius * math.sin(lat_angle_next)

                    self.line3d(x1, y1, z1, x2, y2, z2)



    def ellipse(self, x, y, radius_x, radius_y, segments=36):
        angle_increment = 2 * math.pi / segments
        prev_x = x + radius_x
        prev_y = y
        for i in range(1, segments + 1):
            angle = i * angle_increment
            new_x = x + radius_x * math.cos(angle)
            new_y = y + radius_y * math.sin(angle)
            self.line2d(prev_x, prev_y, new_x, new_y)
            prev_x, prev_y = new_x, new_y

    def arc(self, x, y, radius, start_angle, end_angle, segments=36):
        angle_increment = (end_angle - start_angle) / segments
        prev_x = x + radius * math.cos(start_angle)
        prev_y = y + radius * math.sin(start_angle)
        for i in range(1, segments + 1):
            angle = start_angle + i * angle_increment
            new_x = x + radius * math.cos(angle)
            new_y = y + radius * math.sin(angle)
            self.line2d(prev_x, prev_y, new_x, new_y)
            prev_x, prev_y = new_x, new_y

    def ring(self, x, y, innerRadius, outerRadius, startAngle, endAngle, segments=36):
        angle_increment = (endAngle - startAngle) / segments
        prev_inner_x = x + innerRadius * math.cos(startAngle)
        prev_inner_y = y + innerRadius * math.sin(startAngle)
        prev_outer_x = x + outerRadius * math.cos(startAngle)
        prev_outer_y = y + outerRadius * math.sin(startAngle)

        for i in range(1, segments + 1):
            angle = startAngle + i * angle_increment
            new_inner_x = x + innerRadius * math.cos(angle)
            new_inner_y = y + innerRadius * math.sin(angle)
            new_outer_x = x + outerRadius * math.cos(angle)
            new_outer_y = y + outerRadius * math.sin(angle)
            self.line2d(prev_inner_x, prev_inner_y, new_inner_x, new_inner_y)
            self.line2d(prev_outer_x, prev_outer_y, new_outer_x, new_outer_y)
            self.line2d(prev_inner_x, prev_inner_y, prev_outer_x, prev_outer_y)
            prev_inner_x, prev_inner_y = new_inner_x, new_inner_y
            prev_outer_x, prev_outer_y = new_outer_x, new_outer_y

    def draw_bounding_box(self,box,color):
        self.set_color(color)
        self.vertex3f(box.min.x, box.min.y, box.min.z)
        self.vertex3f(box.max.x, box.min.y, box.min.z)
        
    
        self.vertex3f(box.max.x, box.min.y, box.min.z)
        self.vertex3f(box.max.x, box.max.y, box.min.z)
    
        self.vertex3f(box.max.x, box.max.y, box.min.z)
        self.vertex3f(box.min.x, box.max.y, box.min.z)
    
        self.vertex3f(box.min.x, box.max.y, box.min.z)
        self.vertex3f(box.min.x, box.min.y, box.min.z)
    
        self.vertex3f(box.min.x, box.min.y, box.max.z)
        self.vertex3f(box.max.x, box.min.y, box.max.z)
    
        self.vertex3f(box.max.x, box.min.y, box.max.z)
        self.vertex3f(box.max.x, box.max.y, box.max.z)
    
        self.vertex3f(box.max.x, box.max.y, box.max.z)
        self.vertex3f(box.min.x, box.max.y, box.max.z)
    
        self.vertex3f(box.min.x, box.max.y, box.max.z)
        self.vertex3f(box.min.x, box.min.y, box.max.z)
    
        self.vertex3f(box.min.x, box.min.y, box.min.z)
        self.vertex3f(box.min.x, box.min.y, box.max.z)
    
        self.vertex3f(box.max.x, box.min.y, box.min.z)
        self.vertex3f(box.max.x, box.min.y, box.max.z)
    
        self.vertex3f(box.max.x, box.max.y, box.min.z)
        self.vertex3f(box.max.x, box.max.y, box.max.z)
    
        self.vertex3f(box.min.x, box.max.y, box.min.z)
        self.vertex3f(box.min.x, box.max.y, box.max.z)

    def triangle3d (self, v1, v2, v3):
        self.line3d(v1.x, v1.y, v1.z, v2.x, v2.y, v2.z)
        self.line3d(v2.x, v2.y, v2.z, v3.x, v3.y, v3.z)
        self.line3d(v3.x, v3.y, v3.z, v1.x, v1.y, v1.z)
    
    def draw_transform_bounding_box(self,box,color,mat):
        self.set_color(color)
        edges = box.get_edges()
        
        for c in range(0, 8):
            edges[c] = mat * edges[c]
        self.line3d(edges[5].x, edges[5].y, edges[5].z, edges[1].x, edges[1].y, edges[1].z)
        self.line3d(edges[1].x, edges[1].y, edges[1].z, edges[3].x, edges[3].y, edges[3].z)
        self.line3d(edges[3].x, edges[3].y, edges[3].z, edges[7].x, edges[7].y, edges[7].z)
        self.line3d(edges[7].x, edges[7].y, edges[7].z, edges[5].x, edges[5].y, edges[5].z)

        self.line3d(edges[0].x, edges[0].y, edges[0].z, edges[2].x, edges[2].y, edges[2].z)
        self.line3d(edges[2].x, edges[2].y, edges[2].z, edges[6].x, edges[6].y, edges[6].z)
        self.line3d(edges[6].x, edges[6].y, edges[6].z, edges[4].x, edges[4].y, edges[4].z)
        self.line3d(edges[4].x, edges[4].y, edges[4].z, edges[0].x, edges[0].y, edges[0].z)

        self.line3d(edges[1].x, edges[1].y, edges[1].z, edges[0].x, edges[0].y, edges[0].z)
        self.line3d(edges[3].x, edges[3].y, edges[3].z, edges[2].x, edges[2].y, edges[2].z)
        self.line3d(edges[7].x, edges[7].y, edges[7].z, edges[6].x, edges[6].y, edges[6].z)
        self.line3d(edges[5].x, edges[5].y, edges[5].z, edges[4].x, edges[4].y, edges[4].z)

    def _flush(self):
            if self.vertexCount == 0:
                return
            Render.set_shader(self.shader)
            self.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
            self.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
            self.shader.set_matrix4fv("uModel", glm.value_ptr(Render.matrix[MODEL_MATRIX]))
            
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.count * 4 , np.array(self.vertices, dtype=np.float32))
            glBindVertexArray(self.vao)
            glDrawArrays(GL_LINES, 0, self.vertexCount)
            self.count = 0
            self.vertexCount = 0
            



    def compute_outcode(self, x, y):
        x_min, y_min, x_max, y_max = self.clip_rect
        code = INSIDE
        if x < x_min: 
            code |= LEFT
        elif x > x_max: 
            code |= RIGHT
        if y < y_min: 
            code |= BOTTOM
        elif y > y_max: 
            code |= TOP
        return code
    
    def cohen_sutherland_clip(self, x0, y0, x1, y1):
        x_min, y_min, x_max, y_max = self.clip_rect

        outcode0 = self.compute_outcode(x0, y0)
        outcode1 = self.compute_outcode(x1, y1)
        accept = False

        while True:
            if not (outcode0 | outcode1): 
                accept = True
                break
            elif outcode0 & outcode1: 
                break
            else:
                outcode_out = outcode0 if outcode0 else outcode1

                if outcode_out & TOP:  
                    x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
                    y = y_max
                elif outcode_out & BOTTOM: 
                    x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
                    y = y_min
                elif outcode_out & RIGHT:
                    y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
                    x = x_max
                elif outcode_out & LEFT: 
                    y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
                    x = x_min

                if outcode_out == outcode0:
                    x0, y0 = x, y
                    outcode0 = self.compute_outcode(x0, y0)
                else:
                    x1, y1 = x, y
                    outcode1 = self.compute_outcode(x1, y1)

        if accept:
            self.vertex3f(x0, y0, self.depth)
            self.vertex3f(x1, y1, self.depth)

    def line2d(self, x1, y1, x2, y2):
        if self.clip_enabled:
            self.cohen_sutherland_clip(x1, y1, x2, y2)
        else:
            self.vertex3f(x1, y1, self.depth)
            self.vertex3f(x2, y2, self.depth)        



class FillBatch(Batch):
    def __init__(self, maxVertex):
        super().__init__(maxVertex)
   


    def clip_triangle(self, x0, y0, x1, y1, x2, y2):
        xmin, ymin, xmax, ymax = self.clip_rect


        if (x0 < xmin and x1 < xmin and x2 < xmin) or \
           (x0 > xmax and x1 > xmax and x2 > xmax) or \
           (y0 < ymin and y1 < ymin and y2 < ymin) or \
           (y0 > ymax and y1 > ymax and y2 > ymax):
            return  


        x0 = max(xmin, min(x0, xmax))
        y0 = max(ymin, min(y0, ymax))
        x1 = max(xmin, min(x1, xmax))
        y1 = max(ymin, min(y1, ymax))
        x2 = max(xmin, min(x2, xmax))
        y2 = max(ymin, min(y2, ymax))


        self.vertex3f(x0, y0, self.depth)
        self.vertex3f(x1, y1, self.depth)
        self.vertex3f(x2, y2, self.depth)

    def triangle2d(self, x0, y0, x1, y1, x2, y2):
        if self.clip_enabled:
            self.clip_triangle(x0, y0, x1, y1, x2, y2)
        else:
            self.vertex3f(x0, y0, self.depth)
            self.vertex3f(x1, y1, self.depth)
            self.vertex3f(x2, y2, self.depth)

    def triangle3d (self, v1, v2, v3):
        self.vertex3f(v1.x, v1.y, v1.z)
        self.vertex3f(v2.x, v2.y, v2.z)
        self.vertex3f(v3.x, v3.y, v3.z)

    def rectangle(self, x, y, width, height):
        self.triangle2d(x + width, y + height, x + width, y, x, y)
        self.triangle2d(x, y, x, y + height, x + width, y + height)

    def ellipse(self, x, y, radius_x, radius_y, segments=36):
        angle_increment = 2 * math.pi / segments
        for i in range(segments):
            angle1 = i * angle_increment
            angle2 = (i + 1) * angle_increment
            x1 = x + radius_x * math.cos(angle1)
            y1 = y + radius_y * math.sin(angle1)
            x2 = x + radius_x * math.cos(angle2)
            y2 = y + radius_y * math.sin(angle2)
            self.triangle2d(x, y, x1, y1, x2, y2)

    def circle(self, x, y, radius, segments=36):
        self.ellipse(x, y, radius, radius, segments)  

    def arc(self, x, y, radius, start_angle, end_angle, segments=36):
        angle_increment = (end_angle - start_angle) / segments
        for i in range(segments):
            angle1 = start_angle + i * angle_increment
            angle2 = start_angle + (i + 1) * angle_increment
            x1 = x + radius * math.cos(angle1)
            y1 = y + radius * math.sin(angle1)
            x2 = x + radius * math.cos(angle2)
            y2 = y + radius * math.sin(angle2)
            self.triangle2d(x, y, x1, y1, x2, y2)

    def ring(self, x, y, innerRadius, outerRadius, startAngle, endAngle, segments=36):
        angle_increment = (endAngle - startAngle) / segments
        for i in range(segments):
            angle1 = startAngle + i * angle_increment
            angle2 = startAngle + (i + 1) * angle_increment
            inner_x1 = x + innerRadius * math.cos(angle1)
            inner_y1 = y + innerRadius * math.sin(angle1)
            inner_x2 = x + innerRadius * math.cos(angle2)
            inner_y2 = y + innerRadius * math.sin(angle2)
            outer_x1 = x + outerRadius * math.cos(angle1)
            outer_y1 = y + outerRadius * math.sin(angle1)
            outer_x2 = x + outerRadius * math.cos(angle2)
            outer_y2 = y + outerRadius * math.sin(angle2)
            self.triangle2d(inner_x1, inner_y1, outer_x1, outer_y1, outer_x2, outer_y2)
            self.triangle2d(inner_x1, inner_y1, outer_x2, outer_y2, inner_x2, inner_y2)






    def _flush(self):
        if self.vertexCount == 0:
            return
        Render.set_shader(self.shader)
        self.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
        self.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
        self.shader.set_matrix4fv("uModel", glm.value_ptr(Render.matrix[MODEL_MATRIX]))
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.count * 4, np.array(self.vertices, dtype=np.float32))
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
        self.count = 0
        self.vertexCount = 0
