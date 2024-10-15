from enum import Enum
import glfw
from OpenGL.GL import *

from .shader import Shader
from .texture import Texture
from .color import *
from .material import *
from .utils import Rectangle

class BlendMode(Enum):
    NONE=0,
    Normal= 1,
    Additive= 2,
    Multiply= 3,
    One = 4,


class CullMode(Enum): 
    NONE = 0,
    Front= 1,
    Back=2


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





        


class Render:
    def __init__(self):
        self.program = -1
        self.width = 0
        self.height = 0
        self.viewPort = Rectangle(0,0,1,1)
        self.blend = False
        self.blendMode = BlendMode.NONE
        self.setCullMode = CullMode.NONE
        self.cull = False
        self.material=None
        self.depthTest = False
        self.triangles =0
        self.vertexes =0
        self.textures =0
        self.programs=0
        self.view_matrix = None
        self.projection_matrix = None
        self.model_matrix = None
        self.clearFlag = GL_COLOR_BUFFER_BIT
        self.clearColor = BLACK
        self.layers=[0,0,0,0,0,0]
        self.textureAssets={}
        self.shadersAssets={}
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    def reset(self):
        self.program = -1
        self.textures = 0
        self.triangles = 0
        self.programs = 0
        self.vertexes = 0
        self.layers = [0,0,0,0,0,0]

    def load_texture(self, file_path):
        name = file_path.split("/")[-1].split(".")[0]
        if name in self.textureAssets:
            print(f"Texture {name} already loaded")
            return self.textureAssets[name]
        texture = Texture()
        texture.load(file_path)
        self.textureAssets[name] = texture
        return texture
    
    def load_shader(self, vertName, fragName, name):
        if name in self.shadersAssets:
            print(f"Shader {name} already loaded")
            return self.shadersAssets[name]
        shader = Shader()
        shader.load_shader(vertName, fragName)
        self.shadersAssets[name] = shader
        return shader
    
    def create_shader(self, vertString, fragString, name):
        if name in self.shadersAssets:
            print(f"Shader {name} already loaded")
            return self.shadersAssets[name]
        shader = Shader()
        shader.create_shader(vertString, fragString)
        self.shadersAssets[name] = shader
        return shader
    
    def create_texture(self,width,height,format,bytes):
        texture = Texture()
        texture.create(width,height,format,bytes)
        return texture
    
    def get_texture(self, name):
        if name in self.textureAssets:
            return self.textureAssets[name]
        return None

    def set_texture(self, texture,layer):
        if self.layers[layer] == texture:
            return
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_2D, texture)
        self.textures += 1

    def set_depth_test(self, enable):
        if self.depthTest == enable:
            return
        self.depthTest = enable
        if enable:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

    def set_material(self, material):
        #if self.material == material:
        #    return
        self.material = material
        self.set_program(material.shader.program)

        self.material.apply(self)
        for layer in range(len(material.textures)):
            self.set_texture(material.textures[layer].id,layer)
    
    def render_mesh(self, mesh):
        if (mesh.tris == 0 or mesh.vrtx == 0):
            return
        self.set_material(mesh.material)
        if self.model_matrix is not None:
                self.material.shader.set_matrix4fv("uModel",glm.value_ptr(self.model_matrix))
        if self.view_matrix is not None:
                self.material.shader.set_matrix4fv("uView",glm.value_ptr(self.view_matrix))
        if self.projection_matrix is not None:
                self.material.shader.set_matrix4fv("uProjection",glm.value_ptr(self.projection_matrix))
        glBindVertexArray(mesh.vao)
        glDrawElements(mesh.mode, mesh.tris, GL_UNSIGNED_INT, None)
        self.triangles += mesh.tris // 3
        self.vertexes += mesh.vrtx

    def set_blend(self, enable):
        if self.blend == enable:
            return
        self.blend = enable
        if enable:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
        
    def set_cull(self, enable):
        if self.cull == enable:
            return
        self.cull = enable
        if enable:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)
    def set_cull_mode(self, mode):
        if self.setCullMode == mode:
            return
        self.setCullMode = mode
        if mode == CullMode.Back:
            glCullFace(GL_BACK)
        elif mode == CullMode.Front:
            glCullFace(GL_FRONT)

    def set_clear_color(self, r,g,b):
        if self.clearColor.data[0] == r and self.clearColor.data[1] == g and self.clearColor.data[2] == b:
            return
        self.clearColor.data[0] = r
        self.clearColor.data[1] = g
        self.clearColor.data[2] = b
        glClearColor(r, g, b, 1.0)
    
    def set_clear_mode(self,  depth=False, stencil=False):
        flags = GL_COLOR_BUFFER_BIT
        if depth:
            flags |= GL_DEPTH_BUFFER_BIT
        if stencil:
            flags |= GL_STENCIL_BUFFER_BIT
        self.clearFlag = flags


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



    def set_view_matrix(self, matrix):
        self.view_matrix = matrix

    def set_projection_matrix(self, matrix):
        self.projection_matrix = matrix  

    def set_model_matrix(self, matrix):
        self.model_matrix = matrix  

    def set_program(self, program):
        if self.program != program:
            self.program = program
            glUseProgram(program)
            self.programs += 1

    def set_shader(self, shader):
        self.set_program(shader.program)   

    def clear(self):
        glClear(self.clearFlag)


class Core:
    def __init__(self, width=800, height=600, title="OpenGL"):
        self.width = width
        self.height = height
        self.title = title
        self.render = Render()
        self.render.width = width
        self.render.height = height
        self.last_frame = 0.0
        self.delta_time = 0.0
        self.OnResize = None
        self.OnKeyPress = None
        self.OnMouseMove = None
        self.OnMouseClick = None
        self.key_pressed =[False] * 256
        self.mouse_pressed = [False] * 8
        self.mouse_x = 0
        self.mouse_y = 0
        




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
        glfw.set_window_size_callback(self.window, self._resize_callback)
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_callback)

        
        
    def _key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, 1)
        self.key_pressed[key] = action != glfw.RELEASE

    def _cursor_callback(self, window, xpos, ypos):
        self.mouse_x = xpos
        self.mouse_y = ypos

    def _mouse_callback(self, window, button, action, mods):
        self.mouse_pressed[button] = action != glfw.RELEASE
    
    def _resize_callback(self,window,w,h):
        self.width  = w
        self.height = h
        self.render.set_size(w, h)

        

    def mouse_down(self, button):
        return self.mouse_pressed[button]

    def mouse_pos(self):
        return glm.vec2(self.mouse_x, self.mouse_y)
    
    def key_down(self, key):
        return self.key_pressed[key]


    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_time(self):
        return glfw.get_time()
    
    def get_delta_time(self):
        return self.delta_time

    def run(self):
        self.render.reset()
        for key in range(256):
            self.key_pressed[key] = False
        state = glfw.window_should_close(self.window)
        current_frame = glfw.get_time()
        self.delta_time = current_frame - self.last_frame
        self.last_frame = current_frame
        glfw.poll_events()
        return not state
    
    def flip(self):
        glfw.swap_buffers(self.window)
        glfw.set_window_title(self.window,f" {self.title} [triangles {self.render.triangles} vertex {self.render.vertexes}]")


    def close(self):
        glfw.terminate()
