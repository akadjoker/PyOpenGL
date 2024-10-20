from enum import Enum
import glfw
import glm
import math
from OpenGL.GL import *
from .color import *
from .utils import Rectangle,Ray3D,Frustum
from .texture import *
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
    vertices = 0
    textures = 0
    programs = 0
    frustum = Frustum()
    clear_flag = GL_COLOR_BUFFER_BIT
    clear_color = BLACK
    layers = [0] * 6
    texture_assets = {}


    stack = []


    defaultTexture = None
    defaultFont = None
    cursor_hand = None
    cursor_arrow = None
    cursor_beam = None
    cursor_cross = None
    current_cursor = None
    window = None
    shaders = {}

    @staticmethod
    def reset():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertices = 0
        Render.layers = [0] * 6

            
    @staticmethod
    def init():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertices = 0
        Render.layers = [0] * 6
        Render.matrix.append(glm.mat4(1.0))
        Render.matrix.append(glm.mat4(1.0))
        Render.matrix.append(glm.mat4(1.0))
        Render.defaultTexture = Texture2D()
        Render.defaultTexture.create(1, 1, ColorFormat.RGBA, [255, 255, 255, 255])
        Render.cursor_hand= glfw.create_standard_cursor(glfw.POINTING_HAND_CURSOR)
        Render.cursor_arrow = glfw.create_standard_cursor(glfw.ARROW_CURSOR)
        Render.cursor_beam = glfw.create_standard_cursor(glfw.IBEAM_CURSOR)
        Render.cursor_cross = glfw.create_standard_cursor(glfw.CROSSHAIR_CURSOR)
        Render.current_cursor = None
        

    
    
    @staticmethod
    def get_shader(name):
        material = Render.shaders.get(name)
        if material == None:
            print(f"Shader {name} not found")
            exit(1)
        return material
    

    @staticmethod
    def set_cursor(cursor):
        if Render.current_cursor == cursor:
            return
        if cursor == None:
            glfw.set_cursor(Render.window, Render.cursor_arrow)
            return 
        
        
        Render.current_cursor = cursor
        if cursor == "hand":
            glfw.set_cursor(Render.window, Render.cursor_hand)
        elif cursor == "beam":
            glfw.set_cursor(Render.window, Render.cursor_beam)
        elif cursor == "cross":
            glfw.set_cursor(Render.window, Render.cursor_cross)
        else:
            glfw.set_cursor(Render.window, cursor)

        
    @staticmethod
    def load_texture(file_path,id):
        if id in Render.texture_assets:
            print(f"Texture {id} already loaded")
            return Render.texture_assets[id]
        texture = Texture2D()
        texture.load(file_path)
        Render.texture_assets[id] = texture
        return texture

    @staticmethod
    def load_shader(vert_name, frag_name):
        shader = Shader()
        shader.load_shader(vert_name, frag_name)
        return shader

    @staticmethod
    def create_shader(vert_string, frag_string):
        shader = Shader()
        shader.create_shader(vert_string, frag_string)
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
        #if Render.layers[layer] == texture:
        #    return
        
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
        Render.material.apply()



    

    @staticmethod
    def render_mesh(mesh, material):
        if mesh.tris == 0 or mesh.vrtx == 0:
            return
        Render.set_material(material)
        glBindVertexArray(mesh.vao)
        glDrawElements(mesh.mode, mesh.tris, GL_UNSIGNED_INT, None)
        Render.triangles += mesh.tris // 3
        Render.vertices += mesh.vrtx

    @staticmethod
    def render_mesh_no_material(mesh):
        if mesh.tris == 0 or mesh.vrtx == 0:
            return
        glBindVertexArray(mesh.vao)
        glDrawElements(mesh.mode, mesh.tris, GL_UNSIGNED_INT, None)
        Render.triangles += mesh.tris // 3
        Render.vertices += mesh.vrtx

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
        Render.width = width
        Render.height = height

    @staticmethod
    def set_viewport(x, y, width, height):
        Render.width  = width
        Render.height = height

        if (Render.view_port.x == x and Render.view_port.y == y and
            Render.view_port.width == width and Render.view_port.height == height):
            return
        Render.view_port.x = x
        Render.view_port.y = y
        Render.view_port.width = width
        Render.view_port.height = height
        glViewport(x, y, width, height)


    @staticmethod
    def is_point_in_frustum(x, y, z):
        return Render.frustum.is_point_in_frustum(x, y, z)
    

    @staticmethod
    def is_min_max_in_frustum(min_point, max_point):
        return Render.frustum.is_box_in_frustum(min_point, max_point)
    

    @staticmethod
    def is_box_in_frustum(box):
        return Render.frustum.is_box_in_frustum(box.min, box.max)
    

    @staticmethod
    def is_sphere_in_frustum(center, radius):
        return Render.frustum.is_sphere_in_frustum(center, radius)
    
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
    def get_view_port():
        return Render.view_port

    @staticmethod
    def get_scissor_box():
        return Render.scissor_box

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