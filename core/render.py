from enum import Enum
import glfw
import glm
from OpenGL.GL import *
from .color import *
from .utils import Rectangle
from.texture import Texture
from .shader import Shader

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
    program = -1
    width = 0
    height = 0
    view_port = Rectangle(0, 0, 1, 1)
    blend = False
    blend_mode = BlendMode.NONE
    set_cull_mode = CullMode.NONE
    cull = False
    material = None
    depth_test = False
    triangles = 0
    vertexes = 0
    textures = 0
    programs = 0
    view_matrix = None
    projection_matrix = None
    model_matrix = None
    clear_flag = GL_COLOR_BUFFER_BIT
    clear_color = BLACK
    layers = [0] * 6
    texture_assets = {}
    shaders_assets = {}

    @staticmethod
    def reset():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertexes = 0
        Render.layers = [0] * 6

    @staticmethod
    def load_texture(file_path):
        name = file_path.split("/")[-1].split(".")[0]
        if name in Render.texture_assets:
            print(f"Texture {name} already loaded")
            return Render.texture_assets[name]
        texture = Texture()
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
        texture = Texture()
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
        if Render.model_matrix is not None:
            Render.material.shader.set_matrix4fv("uModel", glm.value_ptr(Render.model_matrix))
        if Render.view_matrix is not None:
            Render.material.shader.set_matrix4fv("uView", glm.value_ptr(Render.view_matrix))
        if Render.projection_matrix is not None:
            Render.material.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.projection_matrix))
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
        glViewport(x, y, width, height)

    @staticmethod
    def set_view_matrix(matrix):
        Render.view_matrix = matrix

    @staticmethod
    def set_projection_matrix(matrix):
        Render.projection_matrix = matrix

    @staticmethod
    def set_model_matrix(matrix):
        Render.model_matrix = matrix

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
