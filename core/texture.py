from enum import Enum
import numpy as np
from OpenGL.GL import *
from PIL import Image

class ColorFormat(Enum):
    GRAYSCALE  = 1,       # 8 bit per pixel (no alpha)
    GRAY_ALPHA = 2,        # 8*2 bpp (2 channels)
    RGB     = 3,          # 24 bpp
    RGBA   = 4          # 32 bpp


class Texture:
    def __init__(self):
        self.id = 0
        self.format = ColorFormat.RGB
        self.width = 0
        self.height = 0
    



        


class Texture2D(Texture):
    def __init__(self):
        super().__init__()


    def create(self,width,height,format,bytes):
        self.width = width
        self.height = height
        self.format = format
        
        glFormat = 0
        if self.format == ColorFormat.GRAYSCALE:
            glFormat = GL_LUMINANCE
        elif self.format == ColorFormat.GRAY_ALPHA:
            glFormat = GL_LUMINANCE_ALPHA
        elif self.format == ColorFormat.RGB:
            glFormat = GL_RGB
        elif self.format == ColorFormat.RGBA:
            glFormat = GL_RGBA

        img_data = np.array(bytes, dtype=np.uint8)
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, glFormat, width, height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def load(self, file_path):
        image = Image.open(file_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)  

        img_data = np.array(image, dtype=np.uint8)
        width, height = image.size

        img_mode = image.mode
        glFormat = 0
        
        if img_mode == "L": 
            self.format = ColorFormat.GRAYSCALE
            glFormat = GL_LUMINANCE
        elif img_mode == "LA":  
            self.format = ColorFormat.GRAY_ALPHA
            glFormat = GL_LUMINANCE_ALPHA
        elif img_mode == "RGB": 
            glFormat = GL_RGB
            self.format = ColorFormat.RGB
        elif img_mode == "RGBA": 
            self.format = ColorFormat.RGBA
            glFormat = GL_RGBA

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

  
        glTexImage2D(GL_TEXTURE_2D, 0,  glFormat, width, height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture  {file_path} {self.id} {self.format} {width}x{height} loaded" )
                