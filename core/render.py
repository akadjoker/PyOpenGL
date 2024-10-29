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
    view_port_box = Rectangle(0, 0, 1, 1)
    blend = False
    blend_mode = BlendMode.NONE
    cull_mode = CullMode.NONE
    matrix=[]
    cull = True
    material = None
    depth_test = False
    scissor_test = False
    scissor_box = Rectangle(0, 0, 1, 1)
    triangles = 0
    vertices = 0
    textures = 0
    cubeTexture = -1
    programs = 0
    frustum = Frustum()
    clear_flag = GL_COLOR_BUFFER_BIT
    clear_color = BLACK
    layers = []
    texture_assets = {}
    states = {}
    stack = []
    shadows=[]
    linesBatch=None
    defaultTexture = None
    defaultFont = None
    cursor_hand = None
    cursor_arrow = None
    cursor_beam = None
    cursor_cross = None
    current_cursor = None
    window = None
    StencilValue=0
    shaders = {}

    @staticmethod
    def reset():
        Render.program = -1
        Render.textures = 0
        Render.triangles = 0
        Render.programs = 0
        Render.vertices = 0
        Render.layers[0]= None
        Render.layers[1]= None
        Render.layers[2]= None
        Render.layers[3]= None

            
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
        Render.layers.append(None)
        Render.layers.append(None)
        Render.layers.append(None)
        Render.layers.append(None)
        Render.shadows.append(0)
        Render.shadows.append(0)
        Render.shadows.append(0)
        Render.shadows.append(0)

        

    @staticmethod
    def save():
        Render.states["view_port"] = Render.view_port_box
        Render.states["blend"] = Render.blend
        Render.states["blend_mode"] = Render.blend_mode
        Render.states["cull"] = Render.cull
        Render.states["material"] = Render.material
        Render.states["depth_test"] = Render.depth_test
        Render.states["scissor_test"] = Render.scissor_test
        Render.states["scissor_box"] = Render.scissor_box
        Render.states["clear_flag"] = Render.clear_flag
        Render.states["clear_color_r"] = Render.clear_color.data[0]
        Render.states["clear_color_g"] = Render.clear_color.data[1]
        Render.states["clear_color_b"] = Render.clear_color.data[2]
        
    

    @staticmethod
    def restore():
        Render.view_port_box = Render.states["view_port"]
        Render.blend = Render.states["blend"]
        Render.blend_mode = Render.states["blend_mode"]
        Render.cull = Render.states["cull"]
        Render.material = Render.states["material"]
        Render.depth_test = Render.states["depth_test"]
        Render.scissor_test = Render.states["scissor_test"]
        Render.scissor_box = Render.states["scissor_box"]
        Render.clear_flag = Render.states["clear_flag"]
        r = Render.states["clear_color_r"]
        g = Render.states["clear_color_g"]
        b = Render.states["clear_color_b"]
        Render.set_clear_color(r, g, b)
        Render.set_viewport(Render.view_port_box.x, Render.view_port_box.y, Render.view_port_box.width, Render.view_port_box.height)


    @staticmethod
    def set_shadow_texture(id,layer):
        if layer < 0 or layer > 3:
            print(f"Layer {layer} not found")
            return
        Render.shadows[layer] = id
    
    @staticmethod
    def get_shader(name):
        shader = Render.shaders.get(name)
        if shader == None:
            print(f"Shader {name} not found")
            exit(1)
        return shader
    
    @staticmethod
    def get_cursor():
        return Render.current_cursor
    
    @staticmethod
    def is_cursor(c):
        if Render.current_cursor==None:
            return False
        return Render.current_cursor == Render.cursor_hand
 
        
    


    @staticmethod
    def set_cursor(cursor):
        if Render.current_cursor == cursor:
            return
        if cursor == None:
            glfw.set_cursor(Render.window, Render.cursor_arrow)
            return 
        if  Render.current_cursor == cursor:
            return
        Render.current_cursor = cursor
        glfw.set_cursor(Render.window, cursor)

        
    @staticmethod
    def load_texture(file_path,id):
        if id in Render.texture_assets:
            #print(f"Texture {id} already loaded")
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
        if layer < 0 or layer > 3:
            #print(f"Layer {layer} not found")
            return
        if Render.layers[layer] == texture:
            return
        
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_2D, texture)
        Render.textures += 1
    @staticmethod
    def set_default_texture(layer):
        if layer < 0 or layer > 3:
            #print(f"Layer {layer} not found")
            return
        if Render.layers[layer] == Render.defaultTexture:
            return
        
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_2D, Render.defaultTexture)
        Render.textures += 1
    @staticmethod
    def set_texture_cube(texture, layer=1):
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture)
        Render.textures += 1

    @staticmethod
    def set_texture_cube_face(texture, face):
        glBindTexture(GL_TEXTURE_CUBE_MAP_POSITIVE_X + face, texture); 
    

    @staticmethod
    def set_depth_test(enable):
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
            print("Mesh is empty")
            return
        glBindVertexArray(mesh.vao)
        glDrawElements(mesh.mode, mesh.tris, GL_UNSIGNED_INT, None)
        Render.triangles += mesh.tris // 3
        Render.vertices += mesh.vrtx

    @staticmethod
    def render_mesh_geometry(mesh):
        if mesh.tris == 0 or mesh.vrtx == 0:
            print("Mesh is empty")
            return
        glBindVertexArray(mesh.vao)
        glDrawElements(GL_TRIANGLES_ADJACENCY, mesh.tris, GL_UNSIGNED_INT, None)
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
        Render.cull = enable
        if enable:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)

    @staticmethod
    def set_cull_mode(mode):
        if not Render.cull:
            return
        Render.cull_mode = mode
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

        if (Render.view_port_box.x == x and Render.view_port_box.y == y and
            Render.view_port_box.width == width and Render.view_port_box.height == height):
            return
        Render.view_port_box.x = x
        Render.view_port_box.y = y
        Render.view_port_box.width = width
        Render.view_port_box.height = height
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
        #if Render.program != program:
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



#for screen effect or shadow shader : ScreenShader
class ScreenQuad:
    def __init__(self,size):
        self.vertices = [-size,-size,
                         size,-size,
                         -size,size,
                         size,size]
        self.VBO =0
        self.VAO =0
    
    def init(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * sizeof(self.vertices[0]), self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
    
    def update(self,size):
        self.vertices = [-size,-size,
                         size,-size,
                         -size,size,
                         size,size]
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * sizeof(self.vertices[0]), self.vertices, GL_STATIC_DRAW)

    def render(self):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    
    def destroy(self):
        glDeleteVertexArrays(1, self.VAO)
        glDeleteBuffers(1, self.VBO)

#for screen effect or shadow with more control
class SingleRender:
    def __init__(self):
        self.stride = 2  # Número de componentes por vértice (x, y)
        self.vertices = [0.0] * (4 * self.stride)  # 4 vértices * 2 componentes
        self.count = 0
        self.VAO = 0
        self.VBO = 0
        self.vertex(-1.0, -1.0)
        self.vertex(1.0, -1.0)
        self.vertex(-1.0, 1.0)
        self.vertex(1.0, 1.0)
        self.init()

    def init(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        size_in_bytes = len(self.vertices) * ctypes.sizeof(ctypes.c_float)
        data_array = (ctypes.c_float * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, size_in_bytes, data_array, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        stride = self.stride * ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, self.stride, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.VAO])
        glDeleteBuffers(1, [self.VBO])

    def vertex(self, x, y):
        self.vertices[self.count] = x
        self.vertices[self.count + 1] = y
        self.count += self.stride 

    def render(self, x, y, width, height):
        self.count = 0  
        w = width /2
        h = height /2
        x1 = x - w
        y1 = y - h
        x2 = x + w
        y2 = y + h

        self.vertex(x1, y1)
        self.vertex(x2, y1)
        self.vertex(x1, y2)
        self.vertex(x2, y2)


        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        size_in_bytes = len(self.vertices) * ctypes.sizeof(ctypes.c_float)
        data_array = (ctypes.c_float * len(self.vertices))(*self.vertices)
        glBufferSubData(GL_ARRAY_BUFFER, 0, size_in_bytes, data_array)

        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        

class FullScreenQuad:
    def __init__(self):
        self.vao=0
        self.vbo=0
        self.init()
    
    def init(self):
        # Vértices para quad em NDC (Normalized Device Coordinates) shader em 2D sem matrix
        # vertices = [
        #     -1.0, -1.0,   0.0, 0.0,  
        #      1.0, -1.0,   1.0, 0.0,  
        #     -1.0,  1.0,   1.0, 1.0,  
        #     1.0,   1.0,    0.0, 1.0   
        # ]
        vertices = [
            1.0, 1.0, 
             -1.0, 1.0,    
            -1.0,  -1.0,  
            1.0,   -1.0,    
        ]

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)
         
   
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, None)
        glEnableVertexAttribArray(0)
        # glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        # glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        
    def render(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        
    def release(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])


class DepthTexture(Texture):
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0
        self.frame_buffer = 0
        self.status = 0
        self.isBegin = False
        self.format = ColorFormat.RGB

    def init(self, width, height):
        self.width = width
        self.height = height
        self.frame_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)



        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.id, 0)

         # Não usar buffer de cor  ao debug mostra vermelho
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        
        self.status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if self.status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer is not complete")


        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    
    def begin(self):
        if self.isBegin:
            return
        self.isBegin = True
        Render.save()
        Render.set_viewport(0, 0, self.width, self.height)
        Render.set_clear_color(1.0, 1.0, 1.0)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        glClear(GL_DEPTH_BUFFER_BIT)
        

    def end(self):
        if not self.isBegin:    
            return
        self.isBegin = False
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        Render.restore()
        Render.set_shadow_texture(self.id,0)


    def release(self):
        super().release()
        glDeleteFramebuffers(1, [self.frame_buffer])
   
class DepthCubeTexture(Texture):
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0
        self.frame_buffer = 0
        self.status = 0
        self.isBegin = False
        self.format = ColorFormat.RGB 

    def init(self, width, height):
        self.width = width
        self.height = height
        
        self.frame_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)
        
        for i in range(6):
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)


        
        
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)


        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, self.id, 0)

        # Não usamos buffer de cor para sombras
        #glDrawBuffer(GL_NONE)
        #glReadBuffer(GL_NONE)

        
        self.status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if self.status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer is not complete")
        
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    
    def begin(self):
        if self.isBegin:
            return
        self.isBegin = True
        Render.save()
        Render.set_viewport(0, 0, self.width, self.height)
        Render.set_clear_color(0.0, 0.0, 1.0)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        glClear(GL_DEPTH_BUFFER_BIT)
        
    def render(self, face_index):
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X + face_index, self.id, 0)
        glDrawBuffer(GL_NONE)
        glClear(GL_DEPTH_BUFFER_BIT)

    def end(self):
        if not self.isBegin:
            return
        self.isBegin = False
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        Render.restore()

    def set_texture(self, layer):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)
        #glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X + layer, self.id, 0)


    def release(self):
        super().release()
        glDeleteFramebuffers(1, [self.frame_buffer])
        glDeleteTextures(1, [self.id])




class Stencil:
    @staticmethod
    def front():
        # Configuração Inicial
        midStencilVal = 128  # Valor intermediário no stencil buffer

        # 1. Ativar o teste de stencil e limpar buffers
        glEnable(GL_STENCIL_TEST)
        glClearStencil(midStencilVal)             # Define o valor inicial do stencil buffer
        glClear(GL_STENCIL_BUFFER_BIT)            # Limpa o stencil buffer com o valor inicial
        glDepthMask(GL_FALSE)                     # Desativa escrita no depth buffer
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)  # Desativa escrita no color buffer
        glEnable( GL_CULL_FACE )
        # 2. Renderizar o Volume de Sombra

        # Passo 1: Incrementar para Faces Traseiras (Z-fail)
        glStencilFunc(GL_ALWAYS, midStencilVal, 0xFFFFFFFF) #~0 like 0xFFFFFFFF 
        glStencilOp(GL_KEEP, GL_INCR_WRAP, GL_KEEP)          # Incrementa no depth fail
        glCullFace(GL_BACK)                                  
                               


    @staticmethod
    def back():
        # Passo 2: Decrementar para Faces Frontais (Z-pass)
        glStencilOp(GL_KEEP, GL_DECR_WRAP, GL_KEEP)          # Decrementa no depth fail
        glCullFace(GL_FRONT)                                 # Culling das faces frontais



    @staticmethod
    def read():
        midStencilVal = 128 
        # 3. Restaurar Buffers para a Renderização Normal
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)      # Reativa escrita no color buffer
        glDepthMask(GL_TRUE)                                 # Reativa escrita no depth buffer

        # 4. Renderizar a Parte Iluminada da Cena
        glStencilFunc(GL_EQUAL, midStencilVal, 0xFFFFFFFF)   # Apenas onde o stencil == midStencilVal
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)               # Mantém o stencil inalterado
        glCullFace(GL_BACK)


    @staticmethod
    def write():
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glDepthMask(GL_TRUE)
        glStencilFunc(GL_NOTEQUAL, 0, ~0)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        #draw quad
    
    
    @staticmethod
    def end():
        glStencilFunc(GL_ALWAYS, 0, 0xFFFFFFFF)  # Ignora o stencil em renderizações futuras
        glDisable(GL_STENCIL_TEST)               # Desativa o teste de stencil
        Render.set_cull(True)
        Render.set_cull_mode(CullMode.Back)
        Render.set_depth_test(True)

   



class DepthBuffer:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.frame_buffer = 0
        self.color = 0
        self.depth = 0
        self.status = 0
        self.isBegin = False

    def init(self,width, height):
        self.width = width
        self.height = height
        self.frame_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)

        self.color = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color, 0)

        self.depth = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth, 0)

        
        self.status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if self.status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer is not complete")

        #glDrawBuffer(GL_COLOR_ATTACHMENT0)
        #glReadBuffer(GL_COLOR_ATTACHMENT0)

        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    
    def begin(self):
        if self.isBegin:
            return
        self.isBegin = True
        Render.save()
        Render.set_viewport(0, 0, self.width, self.height)
        Render.set_clear_color(0.0, 0.0, 0.0)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    

    def end(self):
        if not self.isBegin:    
            return
        self.isBegin = False
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        Render.restore()
        Render.shaders[0] = self.color
        Render.shaders[1] = self.depth

    def release(self):
        glDeleteFramebuffers(1, [self.frame_buffer])
        glDeleteTextures(2, [self.color, self.depth])

        

class ShadowCaster:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.texture_id = 0
        self.depth_buffer = 0
        self.framebuffer = 0
        self.status = 0
        self.is_begin = False

    def init(self):
        # Gerar e vincular o framebuffer
        self.framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)

        # Criar e configurar a textura
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Anexar a textura ao framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                               GL_TEXTURE_2D, self.texture_id, 0)

        # Criar e configurar o renderbuffer de profundidade
        self.depth_buffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24,
                              self.width, self.height)
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

        # Anexar o renderbuffer ao framebuffer
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                  GL_RENDERBUFFER, self.depth_buffer)

        # Verificar o status do framebuffer
        self.status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if self.status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer não está completo")

        # Desvincular o framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind_layer(self, layer):
        glActiveTexture(GL_TEXTURE0 + layer)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def begin(self):
        if self.is_begin:
            return
        self.is_begin = True
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glViewport(0, 0, self.width, self.height)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    def end(self):
        if not self.is_begin:
            return
        self.is_begin = False
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def destroy(self):
        glDeleteFramebuffers(1, [self.framebuffer])
        glDeleteRenderbuffers(1, [self.depth_buffer])
        glDeleteTextures(1, [self.texture_id])
        self.framebuffer = 0
        self.depth_buffer = 0
        self.texture_id = 0

class TextureCascade:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.count = 0
        self.textures = []

    def init(self, count, width, height):
        self.width = width
        self.height = height
        self.count = count
        self.textures = glGenTextures(count)

        for i in range(count):
            texture_id = self.textures[i]
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32, width, height, 0,
                         GL_DEPTH_COMPONENT, GL_FLOAT, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            border_color = [1.0, 1.0, 1.0, 1.0]
            glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)
            glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self, start):
        for i in range(self.count):
            glActiveTexture(GL_TEXTURE0 + start + i)
            glBindTexture(GL_TEXTURE_2D, self.textures[i])

    def set(self, id):
        if id >= self.count:
            print("Cascade Index out of range")
            return
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textures[id])

    def release(self):
        glDeleteTextures(len(self.textures), self.textures)
        self.textures = []

class CascadeShadow:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.count = 0
        self.depthMapFBO = 0
        self.textures = TextureCascade()

    def init(self, count, width, height):
        self.width = width
        self.height = height
        self.count = count
        self.textures.init(count, width, height)

        self.depthMapFBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        # Anexar a primeira textura de profundidade
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.textures.textures[0], 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Failure ao criar framebuffer de cascata")
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            return False

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return True

    def begin(self):
        glViewport(0, 0, self.width, self.height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)

    def set(self, index):
        if index >= self.count:
            print("Invalid depth map index")
            return
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.textures.textures[index], 0)
        glClear(GL_DEPTH_BUFFER_BIT)

    def end(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind_textures(self, start):
        self.textures.bind(start)

    def bind_texture(self, id):
        self.textures.set(id)

    def release(self):
        glDeleteFramebuffers(1, [self.depthMapFBO])
        self.textures.release()
