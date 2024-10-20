from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core import *
from .utils import Quad, rotate_point
from .texture import Texture

import math
import ctypes

class SpriteBatch:
    def __init__(self, maxVertex):
        self.maxVertex = maxVertex
        self.stride = 9  # 3 para posição, 2 para textura, 4 para cor
        self.vertices = [0.0] * (maxVertex * self.stride)
        self.indices = []
        self.vertexCount = 0
        self.maxElemnts = maxVertex * 4 * 6
        self.totalAlloc = math.floor((self.maxVertex * 4 * self.stride * 4) / 9)
        
        self.defaultTexture = Texture2D()
        self.pixels = np.zeros((64, 64, 3), dtype=np.uint8)
        for w in range(64):
            for h in range(64):
                self.pixels[w, h] = [255, 0, 255]  
        self.defaultTexture.create(64, 64, ColorFormat.RGB, self.pixels)
        self.currentBaseTexture = self.defaultTexture

        self.count = 0
        self.color_r = 1.0
        self.color_g = 1.0
        self.color_b = 1.0
        self.color_a = 1.0
        self.tu = 0
        self.tv = 0
        self.flip_x = False
        self.flip_y = False
        self.depth = 0.0
        self.invTexWidth = 1.0
        self.invTexHeight = 1.0
        self.stretching_texels=True

        k = 0
        for i in range(0, self.maxElemnts // 6):
            self.indices.append(4 * k + 0)
            self.indices.append(4 * k + 1)
            self.indices.append(4 * k + 2)
            self.indices.append(4 * k + 0)
            self.indices.append(4 * k + 2)
            self.indices.append(4 * k + 3)
            k += 1

        self.shader = Render.get_shader("default")
        self.init()

    def init(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)


        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(self.indices, dtype=np.uint32), GL_STATIC_DRAW)


        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * 4, None, GL_DYNAMIC_DRAW)


        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.stride * 4, None)
        glEnableVertexAttribArray(0)


        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.stride * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, self.stride * 4, ctypes.c_void_p(20))
        glEnableVertexAttribArray(2)

    def vertex2f(self, x, y):
        self.vertex3f(x, y, self.depth)

    def _switch_texture(self, texture):
        self.defaultTexture = texture
        self.invTexWidth =  1.0 / texture.width
        self.invTexHeight = 1.0 / texture.height

    def vertex3f(self, x, y, z):
        self.vertices[self.count] = x
        self.vertices[self.count + 1] = y
        self.vertices[self.count + 2] = z
        self.vertices[self.count + 3] = self.tu
        self.vertices[self.count + 4] = self.tv
        self.vertices[self.count + 5] = self.color_r
        self.vertices[self.count + 6] = self.color_g
        self.vertices[self.count + 7] = self.color_b
        self.vertices[self.count + 8] = self.color_a
        self.count += self.stride
        self.vertexCount += 1

    def textCoords(self, x, y):
        self.tu = x
        self.tv = y

    def render(self):
        if self.vertexCount == 0:
            return
        self._flush()

    def _flush(self):
        if self.vertexCount == 0:
            return

        glBindVertexArray(self.vao)
        
        Render.set_shader(self.shader)
        Render.set_texture(self.defaultTexture.id, 0)
        self.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
        self.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
        self.shader.set_matrix4fv("uModel", glm.value_ptr(Render.matrix[MODEL_MATRIX]))
  
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.count * 4, np.array(self.vertices, dtype=np.float32))

        glDrawElements(GL_TRIANGLES,  (self.vertexCount // 4) * 6, GL_UNSIGNED_INT, None)

        self.count = 0
        self.vertexCount = 0



    def draw(self, texture, x, y, width, height):
        if (texture.id != self.defaultTexture.id):
            self._switch_texture(texture)


        width_tex  = texture.width
        height_tex = texture.height



  
        left = 0.0
        right = 1.0
        top = 0.0
        bottom = 1.0

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top





        x1 =x 
        y1 =y

        x2 = x 
        y2 = y + height

        x3=  x + width
        y3 = y + height

        x4 = x + width
        y4 = y 




        self.textCoords( left, top)
        self.vertex2f( x1, y1)

        self.textCoords( left, bottom)
        self.vertex2f( x2, y2)

        self.textCoords( right, bottom)
        self.vertex2f( x3, y3)

        self.textCoords( right, top)
        self.vertex2f( x4, y4)         


    def draw_clip(self, texture, x, y, width, height, src_x, src_y, src_width, src_height):
        if (texture.id != self.defaultTexture.id):
            self._switch_texture(texture)


        width_tex  = texture.width
        height_tex = texture.height



        if self.stretching_texels:
            left = (2 * src_x + 1) / (2 * width_tex)
            right = left + (src_width * 2 - 2) / (2 * width_tex)
            top = (2 * src_y + 1) / (2 * height_tex)
            bottom = top + (src_height * 2 - 2) / (2 * height_tex)
        else:
            left = src_x / width_tex
            right = (src_x + src_width) / width_tex
            top = src_y / height_tex
            bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top





        x1 =x 
        y1 =y

        x2 = x 
        y2 = y + height

        x3=  x + width
        y3 = y + height

        x4 = x + width
        y4 = y 




        self.textCoords( left, top)
        self.vertex2f( x1, y1)

        self.textCoords( left, bottom)
        self.vertex2f( x2, y2)

        self.textCoords( right, bottom)
        self.vertex2f( x3, y3)

        self.textCoords( right, top)
        self.vertex2f( x4, y4)  


    def draw_rotate(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, angle):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)

        width_tex = texture.width
        height_tex = texture.height

        if self.stretching_texels:
            left = (2 * src_x + 1) / (2 * width_tex)
            right = left + (src_width * 2 - 2) / (2 * width_tex)
            top = (2 * src_y + 1) / (2 * height_tex)
            bottom = top + (src_height * 2 - 2) / (2 * height_tex)
        else:
            left = src_x / width_tex
            right = (src_x + src_width) / width_tex
            top = src_y / height_tex
            bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top


        x1, y1 = x, y
        x2, y2 = x, y + height
        x3, y3 = x + width, y + height
        x4, y4 = x + width, y


        center_x = x + width / 2
        center_y = y + height / 2


        
        x1, y1 = rotate_point(x1, y1, center_x, center_y, angle)
        x2, y2 = rotate_point(x2, y2, center_x, center_y, angle)
        x3, y3 = rotate_point(x3, y3, center_x, center_y, angle)
        x4, y4 = rotate_point(x4, y4, center_x, center_y, angle)

        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)

    def draw_rotate_pivot(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, pivot_x,pivot_y,angle):
            if texture.id != self.defaultTexture.id:
                self._switch_texture(texture)

            width_tex = texture.width
            height_tex = texture.height

            if self.stretching_texels:
                left = (2 * src_x + 1) / (2 * width_tex)
                right = left + (src_width * 2 - 2) / (2 * width_tex)
                top = (2 * src_y + 1) / (2 * height_tex)
                bottom = top + (src_height * 2 - 2) / (2 * height_tex)
            else:
                left = src_x / width_tex
                right = (src_x + src_width) / width_tex
                top = src_y / height_tex
                bottom = (src_y + src_height) / height_tex

            if self.flip_x:
                left, right = right, left

            if self.flip_y:
                top, bottom = bottom, top


            x1, y1 = x, y
            x2, y2 = x, y + height
            x3, y3 = x + width, y + height
            x4, y4 = x + width, y

            # Calcular o ponto central da rotação
            center_x = pivot_x
            center_y = pivot_y




            
            x1, y1 = rotate_point(x1, y1, center_x, center_y, angle)
            x2, y2 = rotate_point(x2, y2, center_x, center_y, angle)
            x3, y3 = rotate_point(x3, y3, center_x, center_y, angle)
            x4, y4 = rotate_point(x4, y4, center_x, center_y, angle)

            self.textCoords(left, top)
            self.vertex2f(x1, y1)

            self.textCoords(left, bottom)
            self.vertex2f(x2, y2)

            self.textCoords(right, bottom)
            self.vertex2f(x3, y3)

            self.textCoords(right, top)
            self.vertex2f(x4, y4)        

    def draw_scale(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, scale_x=1.0, scale_y=1.0):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)

        width_tex = texture.width
        height_tex = texture.height

        if self.stretching_texels:
            left = (2 * src_x + 1) / (2 * width_tex)
            right = left + (src_width * 2 - 2) / (2 * width_tex)
            top = (2 * src_y + 1) / (2 * height_tex)
            bottom = top + (src_height * 2 - 2) / (2 * height_tex)
        else:
            left = src_x / width_tex
            right = (src_x + src_width) / width_tex
            top = src_y / height_tex
            bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top


        scaled_width = width * scale_x
        scaled_height = height * scale_y

        x1, y1 = x, y
        x2, y2 = x, y + scaled_height
        x3, y3 = x + scaled_width, y + scaled_height
        x4, y4 = x + scaled_width, y


        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)


    def draw_rotate_scale(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, angle, scale_x=1.0, scale_y=1.0):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)

        width_tex = texture.width
        height_tex = texture.height

        if self.stretching_texels:
            left = (2 * src_x + 1) / (2 * width_tex)
            right = left + (src_width * 2 - 2) / (2 * width_tex)
            top = (2 * src_y + 1) / (2 * height_tex)
            bottom = top + (src_height * 2 - 2) / (2 * height_tex)
        else:
            left = src_x / width_tex
            right = (src_x + src_width) / width_tex
            top = src_y / height_tex
            bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top

        scaled_width = width * scale_x
        scaled_height = height * scale_y


        x1, y1 = x, y
        x2, y2 = x, y + scaled_height
        x3, y3 = x + scaled_width, y + scaled_height
        x4, y4 = x + scaled_width, y


        center_x = x + scaled_width / 2
        center_y = y + scaled_height / 2


        x1, y1 = rotate_point(x1, y1, center_x, center_y, angle)
        x2, y2 = rotate_point(x2, y2, center_x, center_y, angle)
        x3, y3 = rotate_point(x3, y3, center_x, center_y, angle)
        x4, y4 = rotate_point(x4, y4, center_x, center_y, angle)


        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)


    def draw_rotate_scale_pivot(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, angle, scale_x=1.0, scale_y=1.0, pivot_x=0.5, pivot_y=0.5):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)

        width_tex = texture.width
        height_tex = texture.height

        if self.stretching_texels:
            left = (2 * src_x + 1) / (2 * width_tex)
            right = left + (src_width * 2 - 2) / (2 * width_tex)
            top = (2 * src_y + 1) / (2 * height_tex)
            bottom = top + (src_height * 2 - 2) / (2 * height_tex)
        else:
            left = src_x / width_tex
            right = (src_x + src_width) / width_tex
            top = src_y / height_tex
            bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top


        scaled_width = width * scale_x
        scaled_height = height * scale_y


        x1, y1 = x, y
        x2, y2 = x, y + scaled_height
        x3, y3 = x + scaled_width, y + scaled_height
        x4, y4 = x + scaled_width, y


        pivot_point_x = x + scaled_width * pivot_x
        pivot_point_y = y + scaled_height * pivot_y

        x1, y1 = rotate_point(x1, y1, pivot_point_x, pivot_point_y, angle)
        x2, y2 = rotate_point(x2, y2, pivot_point_x, pivot_point_y, angle)
        x3, y3 = rotate_point(x3, y3, pivot_point_x, pivot_point_y, angle)
        x4, y4 = rotate_point(x4, y4, pivot_point_x, pivot_point_y, angle)


        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)        


    def draw_wave(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, wave_amplitude=5.0, wave_frequency=0.1):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)

        width_tex = texture.width
        height_tex = texture.height

        left = src_x / width_tex
        right = (src_x + src_width) / width_tex
        top = src_y / height_tex
        bottom = (src_y + src_height) / height_tex

        if self.flip_x:
            left, right = right, left
        

        if self.flip_y:
            top, bottom = bottom, top


        x1, y1 = x, y + math.sin(x * wave_frequency) * wave_amplitude
        x2, y2 = x, y + height + math.sin(x * wave_frequency + 1) * wave_amplitude
        x3, y3 = x + width, y + height + math.sin((x + width) * wave_frequency + 1) * wave_amplitude
        x4, y4 = x + width, y + math.sin((x + width) * wave_frequency) * wave_amplitude

        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)        

    def draw_parallax(self, texture, x, y, width, height, src_x, src_y, src_width, src_height, parallax_factor_x=1.0, parallax_factor_y=1.0):
        if texture.id != self.defaultTexture.id:
            self._switch_texture(texture)


        width_tex = texture.width
        height_tex = texture.height

        left = (src_x / width_tex) * parallax_factor_x
        right = ((src_x + src_width) / width_tex) * parallax_factor_x
        top = (src_y / height_tex) * parallax_factor_y
        bottom = ((src_y + src_height) / height_tex) * parallax_factor_y

        if self.flip_x:
            left, right = right, left

        if self.flip_y:
            top, bottom = bottom, top


        x1, y1 = x, y
        x2, y2 = x, y + height
        x3, y3 = x + width, y + height
        x4, y4 = x + width, y

        self.textCoords(left, top)
        self.vertex2f(x1, y1)

        self.textCoords(left, bottom)
        self.vertex2f(x2, y2)

        self.textCoords(right, bottom)
        self.vertex2f(x3, y3)

        self.textCoords(right, top)
        self.vertex2f(x4, y4)

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
    
    def set_alpha(self, alpha):
        self.color_a = alpha

    def set_depth(self, depth):
        self.depth = depth

    def set_flip_x(self, flip):
        self.flip_x = flip

    def set_flip_y(self, flip):
        self.flip_y = flip