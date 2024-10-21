from enum import Enum
import numpy as np
from OpenGL.GL import *
from PIL import Image
from io import BytesIO
import base64

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
    
    def destroy(self):
        if self.id != 0:
            glDeleteTextures(1, [self.id])
            self.id = 0

class RenderTexture(Texture):
    def __init__(self):
        super().__init__()
        self.frameBuffer = 0
        self.depthBuffer = 0
        self.isBegin = False
        self.format = ColorFormat.RGA

    def create(self, width, height, Linear=True):
        self.width = width
        self.height = height

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        if Linear:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)  

        # Configurar o framebuffer
        self.frameBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.id, 0)

        # Criar e anexar o renderbuffer de profundidade
        self.depthBuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depthBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depthBuffer)


        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer not complete")


        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def begin(self):
        if self.isBegin:
            return
        self.isBegin = True
        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBuffer)
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def end(self):
        if not self.isBegin:
            return
        self.isBegin = False
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def destroy(self):
        super().destroy()
        glDeleteFramebuffers(1, [self.frameBuffer])
        glDeleteRenderbuffers(1, [self.depthBuffer])
        self.frameBuffer = 0
        self.depthBuffer = 0


class Texture2D(Texture):
    def __init__(self):
        super().__init__()


    def create(self,width,height,format,bytes):
        self.width = width
        self.height = height
        self.format = format
        
        glFormat = 0
        if self.format == ColorFormat.GRAYSCALE:
            glFormat = GL_RED 
        elif self.format == ColorFormat.GRAY_ALPHA:
            glFormat = GL_RG
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


    def decode(self, base64_string):
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
    
        
        img_data = np.array(image, dtype=np.uint8)
        self.width, self.height = image.size

        img_mode = image.mode
        glFormat = 0
        if img_mode == "L": 
            self.format = ColorFormat.GRAYSCALE
            glFormat = GL_RED 
        elif img_mode == "LA":  
            self.format = ColorFormat.GRAY_ALPHA
            glFormat = GL_RG 
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

  
        glTexImage2D(GL_TEXTURE_2D, 0,  glFormat, self.width, self.height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture   {self.id} {self.format} {self.width}x{self.height} loaded" )
                

    def load(self, file_path):
        image = Image.open(file_path)
        #image = image.transpose(Image.FLIP_TOP_BOTTOM)  

        img_data = np.array(image, dtype=np.uint8)
        self.width, self.height = image.size

        img_mode = image.mode
        glFormat = 0
        
        if img_mode == "L": 
            self.format = ColorFormat.GRAYSCALE
            glFormat = GL_RED
        elif img_mode == "LA":  
            self.format = ColorFormat.GRAY_ALPHA
            glFormat = GL_RG
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

  
        glTexImage2D(GL_TEXTURE_2D, 0,  glFormat, self.width, self.height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture  {file_path} {self.id} {self.format} {self.width}x{self.height} loaded" )

    def load_from_image(self,image):
        img_data = np.array(image, dtype=np.uint8)
        self.width, self.height = image.size

        img_mode = image.mode
        glFormat = 0
        
        if img_mode == "L": 
            self.format = ColorFormat.GRAYSCALE
            glFormat = GL_RED
        elif img_mode == "LA":  
            self.format = ColorFormat.GRAY_ALPHA
            glFormat = GL_RG
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

  
        glTexImage2D(GL_TEXTURE_2D, 0,  glFormat, self.width, self.height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture  {self.id} {self.format} {self.width}x{self.height} loaded" )                

    def blank(self, width, height):
        self.width = width
        self.height = height
        self.format = ColorFormat.RGBA
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


        bytes = np.zeros((height, width, 4), dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture {self.id} {self.width}x{self.height} created" )


