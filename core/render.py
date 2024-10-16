from enum import Enum
import glfw
import glm
from OpenGL.GL import *
from .color import *
from .utils import Rectangle
from.texture import *
from .shader import Shader
from .material import SolidMaterial

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


PROJECTION_MATRIX = 0x0000
MODEL_MATRIX      = 0x0001
VIEW_MATRIX       = 0x0002

TRIANGLES = 0
TRIANGLE_STRIP = 1
TRIANGLE_FAN = 2
LINES     = 3
LINE_STRIP= 4
LINE_LOOP = 5
POINTS    = 6



class Render:
    program = -1
    width = 0
    height = 0
    view_port = Rectangle(0, 0, 1, 1)
    blend = False
    blend_mode = BlendMode.NONE
    set_cull_mode = CullMode.NONE
    matrix=[]
    cull = False
    material = None
    depth_test = False
    scissor_test = False
    scissor_box = Rectangle(0, 0, 1, 1)
    triangles = 0
    vertexes = 0
    textures = 0
    programs = 0
    view_matrix = None
    projection_matrix = None
    clear_flag = GL_COLOR_BUFFER_BIT
    clear_color = BLACK
    layers = [0] * 6
    texture_assets = {}
    shaders_assets = {}
    use_transform = False
    stack = []
    material2D = None
    defaultTexture = None


    @staticmethod
    def reset():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertexes = 0
        Render.layers = [0] * 6

            
    @staticmethod
    def init():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertexes = 0
        Render.layers = [0] * 6
        Render.matrix.append(glm.mat4(1.0))
        Render.matrix.append(glm.mat4(1.0))
        Render.matrix.append(glm.mat4(1.0))
        Render.defaultTexture = Texture2D()
        Render.defaultTexture.create(1, 1, ColorFormat.RGBA, [255, 255, 255, 255])
        

        
    @staticmethod
    def load_texture(file_path):
        name = file_path.split("/")[-1].split(".")[0]
        if name in Render.texture_assets:
            print(f"Texture {name} already loaded")
            return Render.texture_assets[name]
        texture = Texture2D()
        texture.load(file_path)
        Render.texture_assets[name] = texture
        return texture

    @staticmethod
    def load_shader(vert_name, frag_name, name):
        if name in Render.shaders_assets:
            print(f"Shader {name} already loaded")
            return Render.shaders_assets[name]
        shader = Shader()
        shader.load_shader(vert_name, frag_name)
        Render.shaders_assets[name] = shader
        return shader

    @staticmethod
    def create_shader(vert_string, frag_string, name):
        if name in Render.shaders_assets:
            print(f"Shader {name} already loaded")
            return Render.shaders_assets[name]
        shader = Shader()
        shader.create_shader(vert_string, frag_string)
        Render.shaders_assets[name] = shader
        return shader

    @staticmethod
    def create_texture(width, height, format, bytes):
        texture = Texture2D()
        texture.create(width, height, format, bytes)
        return texture

    @staticmethod
    def get_texture(name):
        return Render.texture_assets.get(name)

    @staticmethod
    def set_texture(texture, layer):
        if Render.layers[layer] == texture:
            return
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_2D, texture)
        Render.textures += 1

    @staticmethod
    def set_depth_test(enable):
        if Render.depth_test == enable:
            return
        Render.depth_test = enable
        if enable:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)




    @staticmethod
    def set_material(material):
        Render.material = material
        Render.set_program(material.shader.program)
        Render.material.apply(Render)
        for layer in range(len(material.textures)):
            Render.set_texture(material.textures[layer].id, layer)

    @staticmethod
    def render_mesh(mesh):
        if mesh.tris == 0 or mesh.vrtx == 0:
            return
        Render.set_material(mesh.material)
        Render.material.shader.set_matrix4fv("uModel", glm.value_ptr(Render.matrix[MODEL_MATRIX]))
        Render.material.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
        Render.material.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
        glBindVertexArray(mesh.vao)
        glDrawElements(mesh.mode, mesh.tris, GL_UNSIGNED_INT, None)
        Render.triangles += mesh.tris // 3
        Render.vertexes += mesh.vrtx

    @staticmethod
    def set_blend(enable):
        if Render.blend == enable:
            return
        Render.blend = enable
        if enable:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
    
    @staticmethod
    def set_scissor_test(enable):
        if Render.scissor_test == enable:
            return
        Render.scissor_test = enable
        if enable:
            glEnable(GL_SCISSOR_TEST)
        else:
            glDisable(GL_SCISSOR_TEST)

    @staticmethod
    def set_cull(enable):
        if Render.cull == enable:
            return
        Render.cull = enable
        if enable:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)

    @staticmethod
    def set_cull_mode(mode):
        if Render.set_cull_mode == mode:
            return
        Render.set_cull_mode = mode
        if mode == CullMode.Back:
            glCullFace(GL_BACK)
        elif mode == CullMode.Front:
            glCullFace(GL_FRONT)

    @staticmethod
    def set_clear_color(r, g, b):
        if (Render.clear_color.data[0] == r and
            Render.clear_color.data[1] == g and
            Render.clear_color.data[2] == b):
            return
        Render.clear_color.data[0] = r
        Render.clear_color.data[1] = g
        Render.clear_color.data[2] = b
        glClearColor(r, g, b, 1.0)

    @staticmethod
    def set_clear_mode(depth=False, stencil=False):
        flags = GL_COLOR_BUFFER_BIT
        if depth:
            flags |= GL_DEPTH_BUFFER_BIT
        if stencil:
            flags |= GL_STENCIL_BUFFER_BIT
        Render.clear_flag = flags

    @staticmethod
    def set_blend_mode(mode):
        if Render.blend_mode == mode or Render.blend == False:
            return
        Render.blend_mode = mode
        if mode == BlendMode.Normal:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        elif mode == BlendMode.Additive:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        elif mode == BlendMode.Multiply:
            glBlendFunc(GL_DST_COLOR, GL_ONE_MINUS_SRC_ALPHA)
        elif mode == BlendMode.One:
            glBlendFunc(GL_ONE, GL_ONE)

    @staticmethod
    def set_size(width, height):
        if Render.width == width and Render.height == height:
            return
        Render.width = width
        Render.height = height

    @staticmethod
    def set_viewport(x, y, width, height):
        if (Render.view_port.x == x and Render.view_port.y == y and
            Render.view_port.width == width and Render.view_port.height == height):
            return
        Render.view_port.x = x
        Render.view_port.y = y
        Render.view_port.width = width
        Render.view_port.height = height
        Render.width = width
        Render.height = height
        glViewport(x, y, width, height)
    
    @staticmethod
    def set_scissor(x, y, width, height):
        if (Render.scissor_box.x == x and Render.scissor_box.y == y and
            Render.scissor_box.width == width and Render.scissor_box.height == height):
            return
        Render.scissor_box.x = x
        Render.scissor_box.y = y
        Render.scissor_box.width = width
        Render.scissor_box.height = height
        inverted_y = Render.height - (y + height)
        glScissor(x, inverted_y, width, height)

    @staticmethod
    def set_matrix(mode,matrix):
        Render.matrix[mode] = matrix

   

    @staticmethod
    def set_program(program):
        if Render.program != program:
            Render.program = program
            glUseProgram(program)
            Render.programs += 1

    @staticmethod
    def set_shader(shader):
        Render.set_program(shader.program)

    @staticmethod
    def clear():
        glClear(Render.clear_flag)




    @staticmethod
    def push_matrix():
        Render.use_transform = True
        Render.stack.append(glm.mat4(Render.matrix[MODEL_MATRIX]))  

    @staticmethod
    def pop_matrix():
        if len(Render.stack) > 0:
            Render.use_transform = False
            Render.matrix[MODEL_MATRIX] = Render.stack.pop()  

    @staticmethod
    def identity():
        if len(Render.stack) > 0:
            Render.stack[-1] = glm.mat4(1.0)  
            Render.matrix[MODEL_MATRIX] = glm.mat4(Render.stack[-1])

    @staticmethod
    def scale(x, y, z):
        if len(Render.stack) > 0:
            Render.stack[-1] = glm.scale(Render.stack[-1], glm.vec3(x, y, z)) 
            Render.matrix[MODEL_MATRIX] = glm.mat4(Render.stack[-1])  

    @staticmethod
    def translate(x, y, z):
        if len(Render.stack) > 0:
            Render.stack[-1] = glm.translate(Render.stack[-1], glm.vec3(x, y, z))  
            Render.matrix[MODEL_MATRIX] = glm.mat4(Render.stack[-1])

    @staticmethod
    def rotate(angle, x, y, z):
        if len(Render.stack) > 0:
            Render.stack[-1] = glm.rotate(Render.stack[-1], glm.radians(angle), glm.vec3(x, y, z)) 
            Render.matrix[MODEL_MATRIX] = glm.mat4(Render.stack[-1])

    @staticmethod
    def rotation(x, y, z, w):
        if len(Render.stack) > 0:
            rotation_quat = glm.quat(w, x, y, z)  
            Render.stack[-1] = Render.stack[-1] * glm.mat4_cast(rotation_quat)  
            Render.matrix[MODEL_MATRIX] = glm.mat4(Render.stack[-1])