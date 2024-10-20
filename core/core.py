from enum import Enum
import glfw
from OpenGL.GL import *

import base64
from .shader import Shader
from .texture import Texture
from .color import *
from .material import *
from .utils import Rectangle,Timer
from .input import Input
from .render import *
from .font import Font
from .data import defaultFontData,defaultFontImage

class Core:
    def __init__(self, width=800, height=600, title="OpenGL"):

        if not glfw.init():
            print("Fail to initialize GLFW")
            exit(1)
        
        self.width = width
        self.height = height
        self.title = title
        self.OnResize = None
        Render.width = width
        Render.height = height
        self.time = Timer()
        self.frame_count = 0   
        self.fps = 0.0         
        self.elapsed_time = 0.0

        



        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            print("Fail to create GLFW window")
            exit(1)

        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self._resize_callback)
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_callback)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        Render.init()
        Render.set_size(width, height)
        Render.set_viewport(0, 0, width, height)
        Render.window = self.window
        Render.shaders["default"] = DefaultShader()
        Render.shaders["solid"]   = SolidShader()
        Render.shaders["texture"] = TextureShader()
        Render.shaders["point"]   = PointShader()
        Render.defaultFont = Font(1024*8)
        Render.set_matrix(VIEW_MATRIX, glm.mat4(1.0))
        Render.set_matrix(PROJECTION_MATRIX, glm.mat4(1.0))
        Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
        
        
        fontData = base64.b64decode(defaultFontData).decode('utf-8')
        texture = Texture2D()
        texture.decode(defaultFontImage)
        Render.defaultFont.create(fontData, texture)

        
        
    def _key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, 1)
        down = action != glfw.RELEASE
        chars = glfw.get_key_name(key, scancode)
        if not chars: chars = ""
        Input.set_key_state(key, down, chars)

    def _cursor_callback(self, window, xpos, ypos):
        Input.set_mouse_cursor(xpos, ypos,self.width,self.height)

    def _mouse_callback(self, window, button, action, mods):
        donw = action != glfw.RELEASE
        Input.set_mouse_state(button, donw)
    
    def _resize_callback(self,window,w,h):
        self.width  = w
        self.height = h
        Render.set_size(w, h)
    

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_time(self):
        return self.time.get_time()
    
    def get_delta_time(self):
        return self.time.get_delta_time()
    def get_fps(self):
        return int(self.fps)

    def run(self):
        Render.reset()
        Input.update()
        delta_time = self.time.get_delta_time()
        self.elapsed_time += delta_time
        self.frame_count += 1

        if self.elapsed_time >= 1.0:
            self.fps = self.frame_count / self.elapsed_time  
            self.frame_count = 0
            self.elapsed_time = 0.0
        state = glfw.window_should_close(self.window)
        glfw.poll_events()
        return not state
    
    def flip(self):
        glfw.swap_buffers(self.window)
   

    def close(self):
        glfw.terminate()
