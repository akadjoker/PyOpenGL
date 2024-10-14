from enum import Enum


import glfw
from OpenGL.GL import *
import numpy as np
from PIL import Image

class ColorFormat(Enum):
    GRAYSCALE  = 1,       # 8 bit per pixel (no alpha)
    GRAY_ALPHA = 2,        # 8*2 bpp (2 channels)
    R8G8B8     = 3,          # 24 bpp
    R8G8B8A8   = 4          # 32 bpp



class BlendMode(Enum):
    NONE=0,
    Normal= 1,
    Additive= 2,
    Multiply= 3,
    One = 4,


class CullMode(Enum): 
    Front= 1,
    Back=2,
    FrontAndBack= 3,


class DepthMode(Enum):
    NONE= 0,
    LESS= 1,
    LESSOREQUAL= 2,
    GREATER= 3,
    GREATEROREQUAL= 4,
    EQUAL= 5,
    NOT_EQUAL= 6,
    ALWAYS= 7,
    NEVER= 8


class FaceMode(Enum): 
    CW = 0,
    CCW= 1


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



class Shader:
    def __init__(self):
        self.program = glCreateProgram()
        self.uniforms = {}

    def use(self):
        glUseProgram(self.program)


    def createShader(self, vertString, fragString):
        vert = self.loadShaderFromString(vertString, GL_VERTEX_SHADER)
        frag = self.loadShaderFromString(fragString, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, vert)
        glAttachShader(self.program, frag)
        glLinkProgram(self.program)
        result = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not result:
            log = glGetProgramInfoLog(self.program)
            print(f"Erro na compilação do shader: {log.decode()}")
            return
        glDeleteShader(vert)
        glDeleteShader(frag)
        glUseProgram(self.program)
        self.load_uniforms()

    def loadShader(self, vertName, fragName):
        vert = self.loadShaderFromFile(vertName, GL_VERTEX_SHADER)
        frag = self.loadShaderFromFile(fragName, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, vert)
        glAttachShader(self.program, frag)
        glLinkProgram(self.program)
        result = glGetProgramiv(self.program, GL_LINK_STATUS) 
        if not result:
            log = glGetProgramInfoLog(self.program)
            print(f"Erro na compilação do shader: {log.decode()}")
            return

        glDeleteShader(vert)
        glDeleteShader(frag)

        glUseProgram(self.program)
        self.load_uniforms()



    def loadShaderFromString(self, source, shaderType):
        shader = glCreateShader(shaderType)
        glShaderSource(shader, source)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not result:
            log = glGetShaderInfoLog(shader)
            print(f"Erro na compilação do shader: {log.decode()}")
            return None
        return shader

    def loadShaderFromFile(self, fileName, shaderType):
        with open(fileName, 'r') as file:
            source = file.read()
        shader = glCreateShader(shaderType)
        glShaderSource(shader, source)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not result:
            log = glGetShaderInfoLog(shader)
            print(f"Erro na compilação do shader: {log.decode()}")
            return None
        return shader

    def load_uniforms(self):
            program = self.program
            num_uniforms = glGetProgramiv(program, GL_ACTIVE_UNIFORMS)
            for i in range(num_uniforms):
                uniform_name, uniform_type = glGetActiveUniform(program, i)[:2]
                name = uniform_name.decode()
                uniform_location = glGetUniformLocation(program, uniform_name)
                self.uniforms[name] = uniform_location
            print(self.uniforms)

    def set_matrix4fv(self, name, matrix):
        location = self.uniforms.get(name)
        if location is not None:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)
        else:
            print(f"Uniform '{name}' not found.")

    def set_float(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform1f(location, value)
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_int(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform1i(location, value)
        else:
            print(f"Uniform '{name}' not found.")


    def set_vector2f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform2f(location, value[0], value[1])
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_vector3f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform3f(location, value[0], value[1], value[2])
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_vector4f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform4f(location, value[0], value[1], value[2], value[3])
        else:
            print(f"Uniform '{name}' not found.")



class Texture:
    def __init__(self):
        self.id = glGenTextures(1)
        self.format = ColorFormat.R8G8B8
        self.width = 0
        self.height = 0
    
    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def create(self,width,height,format,bytes):
        self.width = width
        self.height = height
        self.format = format
        
        glFormat = 0
        if self.format == ColorFormat.GRAYSCALE:
            glFormat = GL_LUMINANCE
        elif self.format == ColorFormat.GRAY_ALPHA:
            glFormat = GL_LUMINANCE_ALPHA
        elif self.format == ColorFormat.R8G8B8:
            glFormat = GL_RGB
        elif self.format == ColorFormat.R8G8B8A8:
            glFormat = GL_RGBA

        img_data = np.array(bytes, dtype=np.uint8)

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
            self.format = ColorFormat.R8G8B8
        elif img_mode == "RGBA": 
            self.format = ColorFormat.R8G8B8A8
            glFormat = GL_RGBA


        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

  
        glTexImage2D(GL_TEXTURE_2D, 0,  glFormat, width, height, 0,  glFormat, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Texture  {file_path} {self.id} {self.format} {width}x{height} loaded" )
        
class Render:
    def __init__(self):
        self.program = -1
        self.width = 0
        self.height = 0
        self.viewPort = Rectangle(0,0,1,1)
        self.blend = False
        self.blendMode = BlendMode.NONE
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)



    def set_blend(self, enable):
        if self.blend == enable:
            return
        self.blend = enable
        if enable:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)

    def set_blend_mode(self, mode):
        if self.blendMode == mode or self.blend == False:
            return
        self.blendMode = mode
        if mode == BlendMode.Normal:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        elif mode == BlendMode.Additive:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        elif mode == BlendMode.Multiply:
            glBlendFunc(GL_DST_COLOR, GL_ONE_MINUS_SRC_ALPHA)
        elif mode == BlendMode.One:
            glBlendFunc(GL_ONE, GL_ONE)

    def set_size(self, width, height):
        if self.width == width and self.height == height:
            return
        self.width = width
        self.height = height
        

    def set_viewport(self, x, y, width, height):
        if self.viewPort.x == x and self.viewPort.y == y and self.viewPort.width == width and self.viewPort.height == height:
            return
        self.viewPort.x = x
        self.viewPort.y = y
        self.viewPort.width = width
        self.viewPort.height = height
        glViewport(x, y, width, height)


    def create_shader(self, vertString, fragString):
        shader = Shader()
        shader.createShader(vertString, fragString)
        return shader
    
    def load_shader(self, vertName, fragName):
        shader = Shader()
        shader.loadShader(vertName, fragName)
        return shader
    
    

    def set_program(self, program):
        if self.program != program:
            self.program = program
            glUseProgram(program)

    def set_shader(self, shader):
        self.set_program(shader.program)   

    def clear(self,r,g,b):
        glClearColor(r, g, b, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class Core:
    def __init__(self, width=800, height=600, title="OpenGL Demo"):
        self.width = width
        self.height = height
        self.render = Render()
        self.render.width = width
        self.render.height = height

        self.OnResize = None
        self.OnKeyPress = None
        self.OnMouseMove = None
        self.OnMouseClick = None




        if not glfw.init():
            raise Exception("Fail to initialize GLFW")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception(" Fail to create GLFW window")

        self.render.set_viewport(0, 0, width, height)
        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self.resize_callback)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_callback)

        
        
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, 1)
        if self.OnKeyPress is not None:
            self.OnKeyPress(key, scancode, action, mods)

    def cursor_callback(self, window, xpos, ypos):
        if self.OnMouseMove is not None:
            self.OnMouseMove(xpos, ypos)

    def mouse_callback(self, window, button, action, mods):
        if self.OnMouseClick is not None:
            self.OnMouseClick(button, action, mods)
    
    def resize_callback(self,window,w,h):
        self.width  = w
        self.height = h
        self.render.set_size(w, h)
        if self.OnResize is not None:
            self.OnResize(w, h)
        



    def GetWidth(self):
        return self.width

    def GetHeight(self):
        return self.height

    def GetTime(self):
        return glfw.get_time()




    def run(self):
        state = glfw.window_should_close(self.window)
        glfw.poll_events()
        return not state
    
    def flip(self):
        glfw.swap_buffers(self.window)


    def close(self):
        glfw.terminate()
