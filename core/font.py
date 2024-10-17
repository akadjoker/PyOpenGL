from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core import *
from .render import Render
from .utils import Quad
from .texture import Texture
from .material import SolidMaterial,SpriteMaterial
import math
import ctypes

class TextAlign(Enum):
    Left = 0
    Right = 1
    Center = 2


class CharacterInfo:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def __str__(self):
        return f"CharacterInfo(x={self.x}, y={self.y}, width={self.width}, height={self.height}, offset_x={self.offset_x}, offset_y={self.offset_y})"


class Font:
    def __init__(self, maxVertex):
        self.maxVertex = maxVertex
        self.stride = 9  # 3 para posição, 2 para textura, 4 para cor
        self.vertices = [0.0] * (maxVertex * self.stride)
        self.indices = []
        self.vertexCount = 0
        self.maxElemnts = maxVertex * 4 * 6
        self.totalAlloc = math.floor((self.maxVertex * 4 * self.stride * 4) / 9)
        self.texture = None
        self.CharInfo=[]
        self.quads=[]
        self.quads.append(Quad(0.0, 0.0, 1.0, 1.0))
        self.quads.append(Quad(0.0, 0.0, 1.0, 1.0))
        self.quads.append(Quad(0.0, 0.0, 1.0, 1.0))
        self.quads.append(Quad(0.0, 0.0, 1.0, 1.0))
        self.invTexWidth  = 0.0
        self.invTexHeight = 0.0
        self.allign = TextAlign.Left
            

        self.maxWidth = 1
        self.maxHeight = 1  

        self.clip_enabled = False
        self.clip = Rectangle(0, 0, 1, 1)
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
        self.size=20
        self.stretching_texel = False

        k = 0
        for i in range(0, self.maxElemnts // 6):
            self.indices.append(4 * k + 0)
            self.indices.append(4 * k + 1)
            self.indices.append(4 * k + 2)
            self.indices.append(4 * k + 0)
            self.indices.append(4 * k + 2)
            self.indices.append(4 * k + 3)
            k += 1

        self.material = SpriteMaterial()
        self.init()
   
    def set_clip(self, x, y, width, height):
        self.clip_enabled = True
        self.clip.set(x, y, width, height)

    def enable_clip(self,value):
        self.clip_enabled = value
        
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


  



    def vertex3f(self, x, y, z):
        self.vertices[self.count]     = x
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

    
    def vertex2f(self, x, y):
        self.vertex3f(x, y, self.depth)

    def textCoords(self, x, y):
        self.tu = x
        self.tv = y

    def render(self):
        if self.vertexCount == 0:
            return

        self._flush()



    def _flush(self):
        if self.vertexCount == 0 or self.texture==None:
            return

        glBindVertexArray(self.vao)
        
        Render.set_material(self.material)
        Render.set_texture(self.texture.id, 0)
        self.material.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
        self.material.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
  
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.count * 4, np.array(self.vertices, dtype=np.float32))

        glDrawElements(GL_TRIANGLES,  (self.vertexCount // 4) * 6, GL_UNSIGNED_INT, None)


        self.count = 0
        self.vertexCount = 0

    def load(self, file_path,texture):
        try: 
            with open(file_path, 'r') as f:
                data = f.read()
                self.create(data,texture)
            return True
        except Exception as e:
            print(f"Fail process font data: {e}")
            return False 


    def create(self, data, texture):
        try:
            self.texture = texture
            
            self.invTexWidth  = 1.0 / texture.width
            self.invTexHeight = 1.0 / texture.height
            lines = data.split('\n')
            for line in lines:
                tokens = line.split(',')
                count = len(tokens)
                index =0
                if count == 8:
                    index = 1
                #print(count ,":",tokens)
                value = tokens[index].strip()
                x = tokens[index+1].strip()
                y = tokens[index+2].strip()
                width = tokens[index+3].strip()
                height = tokens[index+4].strip()
                offsetX = tokens[index+5].strip()
                offsetY = tokens[index+6].strip()
   
                char_info = CharacterInfo()
                char_info.x = int(x)
                char_info.y = int(y)
                char_info.width = int(width)
                char_info.height = int(height)
                if char_info.width > self.maxWidth:
                    self.maxWidth = char_info.width
                if char_info.height > self.maxHeight:
                    self.maxHeight = char_info.height

                char_info.offset_x = int(offsetX)
                char_info.offset_y = int(offsetY)

                self.CharInfo.append(char_info)
           
 

        except Exception as e:
            print(f"Fail process font data: {e} {line}")
            return
        



    def _draw(self, x, y, width, height, src_x, src_y, src_width, src_height):
            if not self.texture or len(self.CharInfo) == 0:
                return

            
            width_tex  = self.texture.width
            height_tex = self.texture.height
            

    
            if self.stretching_texel:
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


            min_x = min(min(x1, x2), min(x3, x4))
            min_y = min(min(y1, y2), min(y3, y4))
            max_x = max(max(x1, x2), max(x3, x4))
            max_y = max(max(y1, y2), max(y3, y4))

            WIDTH  = max_x - min_x
            HEIGHT = max_y - min_y



        

            self.quads[0].x = x1
            self.quads[0].y = y1
            self.quads[1].x = x2
            self.quads[1].y = y2
            self.quads[2].x = x3
            self.quads[2].y = y3
            self.quads[3].x = x4
            self.quads[3].y = y4

            self.quads[0].tx = left 
            self.quads[0].ty = top

            self.quads[1].tx = left
            self.quads[1].ty = bottom

            self.quads[2].tx = right
            self.quads[2].ty = bottom

            self.quads[3].tx = right
            self.quads[3].ty = top
            quadLeft   = min(min(self.quads[0].x, self.quads[1].x), min(self.quads[2].x, self.quads[3].x))
            quadTop    = min(min(self.quads[0].y, self.quads[1].y), min(self.quads[2].y, self.quads[3].y))
            quadRight  = max(max(self.quads[0].x, self.quads[1].x), max(self.quads[2].x, self.quads[3].x))
            quadBottom = max(max(self.quads[0].y, self.quads[1].y), max(self.quads[2].y, self.quads[3].y))

            if self.clip_enabled:
        
                if (quadRight < self.clip.x or quadLeft > self.clip.x + self.clip.width or quadBottom < self.clip.y or quadTop > self.clip.y + self.clip.height):
                    return
                if (x1 < self.clip.x):
                    delta = self.clip.x - x1
                    ratio = delta / WIDTH
                    self.quads[0].x = self.quads[1].x = self.clip.x
                    self.quads[0].tx = self.quads[1].tx = left + (right - left) * ratio

                

                if (x1 + WIDTH > self.clip.x + self.clip.width):
                    delta = (x1 + WIDTH) - (self.clip.x + self.clip.width)
                    ratio = delta / WIDTH
                    self.quads[2].x = self.quads[3].x = self.clip.x + self.clip.width
                    self.quads[2].tx = self.quads[3].tx = right - (right - left) * ratio

                if (y1 < self.clip.y):
                    delta = self.clip.y - y1
                    ratio = delta / HEIGHT
                    self.quads[0].y = self.quads[3].y = self.clip.y
                    self.quads[0].ty = self.quads[3].ty = top + (bottom - top) * ratio
                
                if (y1 + HEIGHT > self.clip.y + self.clip.height):
                    delta = (y1 + HEIGHT) - (self.clip.y + self.clip.height)
                    ratio = delta / HEIGHT
                    self.quads[1].y = self.quads[2].y = self.clip.y + self.clip.height
                    self.quads[1].ty = self.quads[2].ty = bottom - (bottom - top) * ratio




            self.textCoords(self.quads[0].tx, self.quads[0].ty)
            self.vertex2f(self.quads[0].x, self.quads[0].y)

            self.textCoords(self.quads[1].tx, self.quads[1].ty)
            self.vertex2f(self.quads[1].x, self.quads[1].y)

        
            self.textCoords(self.quads[2].tx, self.quads[2].ty)
            self.vertex2f(self.quads[2].x, self.quads[2].y)

            self.textCoords(self.quads[3].tx, self.quads[3].ty)
            self.vertex2f(self.quads[3].x, self.quads[3].y)
        
    def get_text_width(self, text):
        length = len(text)
        scale = self.size / self.maxWidth * 0.5
        offset_x = 0
        for i in range(length):
            c = ord(text[i])
            char_info = self.CharInfo[c - 32]  
            if char_info is None:
                continue
            clip_w = char_info.width
            offset_x += clip_w * scale
        return offset_x
    
    def writef(self, x, y, *args):
        text = " ".join(map(str, args))
        self.write(x, y, text)

    def get_width(self):
        return self.maxWidth * self.size

    def get_height(self):
        return self.maxHeight * self.size

    def write(self, x, y, text):
        scale = self.size / self.maxWidth * 0.5
        offset_x = x
        offset_y = y
        move_y = (self.maxHeight * 0.5) * scale
        length = len(text)

        # Alinhamento
        if self.allign ==  TextAlign.Center:
            offset_x -= self.get_text_width(text) / 2
        elif self.allign ==  TextAlign.Left:
            offset_x = x
        elif self.allign ==  TextAlign.Right:
            offset_x -= self.get_text_width(text)

        for i in range(length):
            c = ord(text[i])
            if c == 10:  # Nova linha
                offset_y -= self.maxHeight * scale
                offset_x = x
                continue

            char_info = self.CharInfo[c - 32]
            if char_info is None:
                continue

            clip_x = char_info.x
            clip_y = char_info.y
            clip_w = char_info.width
            clip_h = char_info.height
            off_x = char_info.offset_x
            off_y = char_info.offset_y + move_y


            self._draw(
                offset_x + off_x * scale,
                offset_y + off_y * scale,
                clip_w * scale, clip_h * scale,
                clip_x, clip_y, clip_w, clip_h
            )
            offset_x += clip_w * scale

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

    def set_allign(self, allign):
        self.allign = allign
    
    def se_alpha(self, alpha):
        self.color_a = alpha

    def set_size(self, size):
        self.size = size
    
    def get_max_width(self):
        return self.maxWidth

    def get_max_height(self):
        return self.maxHeight