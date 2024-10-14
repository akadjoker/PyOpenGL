from enum import Enum
import glfw
from OpenGL.GL import *
import numpy as np
from core  import *


class Attribute(Enum):
    POSITION3D = 0
    POSITION2D = 1
    TEXCOORD0 = 2
    TEXCOORD1 = 3
    COLOR3 = 10
    COLOR4 = 11
    NORMAL = 12
    TANGENT = 13
    BITANGENT = 14


class Material:
    def __init__(self,name):
        self.shader = Shader()
        self.name = name
        self.attributes=[]
  
    
    def use(self):
        self.shader.use()
        self.apply()

    def apply(self):
        pass

class ColorMaterial(Material):
    def __init__(self):
        super().__init__("Color")
        self.attributes=[Attribute.POSITION3D,Attribute.COLOR3] 
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec3 aColor;
        out vec3 vColor;
        void main()
        {
            vColor = aColor;
            gl_Position = vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        in vec3 vColor;
        out vec4 fragColor;
        void main()
        {
            fragColor = vec4(vColor, 1.0);
        }
        """
        self.shader.createShader(vertex,fragment)

class TextureColorMaterial(Material):
    def __init__(self,texture):
        super().__init__("TextureColor")
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.COLOR3] 
        self.texture = texture
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec3 aColor;
        out vec3 vColor;
        out vec2 vTexCoord;
        void main()
        {
            vColor = aColor;
            vTexCoord = aTexCoord;
            gl_Position = vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        out vec4 fragColor;
        in vec3 vColor;
        in vec2 vTexCoord;
        uniform sampler2D texture0;
        void main()
        {
            fragColor =   texture(texture0, vTexCoord) ;
        }
        """
        self.shader.createShader(vertex,fragment)
        self.shader.set_int("texture0",0)

    def apply(self):
        self.texture.bind(0)


class Mesh:
    def __init__(self,material):

        self.material = material
        self.attributes=material.attributes

        self.vbo = {}
        self.vertices = []
        self.normals = []
        self.colors = []
        self.texcoord0 = []
        self.texcoord1 = []
        self.tangents = []
        self.bitangents = []
        self.indices = []
        self.flags = 0
        self.dynamic = False
        self.isConfigured = False
        self.data = 0

        self.vao = glGenVertexArrays(1)
        self.ebo = glGenBuffers(1)

        self.flags |= 1
        self.flags |= 128

        self.count = 0



    def configure(self):
        if self.isConfigured:
            return
        self.isConfigured = True
        offset = 0
        glBindVertexArray(self.vao)
        for index in range(len(self.attributes)):
            attribute = self.attributes[index]
            self.vbo[index] = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
            glEnableVertexAttribArray(index)

            if attribute == Attribute.POSITION3D:
                glVertexAttribPointer(index, 3, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 1
                offset += 3
            elif attribute == Attribute.POSITION2D:
                glVertexAttribPointer(index, 2, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 1
                offset += 2

            elif attribute == Attribute.NORMAL:
                glVertexAttribPointer(index, 3, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 2
                offset += 3
            elif attribute == Attribute.COLOR3:
                glVertexAttribPointer(index, 3, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 4
                offset += 3
            elif attribute == Attribute.COLOR4:
                glVertexAttribPointer(index, 4, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 4
                offset += 4
            elif attribute == Attribute.TEXCOORD0:
                glVertexAttribPointer(index, 2, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 8
                offset += 2
            elif attribute == Attribute.TEXCOORD1:
                glVertexAttribPointer(index, 2, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 8
                offset += 2
            elif attribute == Attribute.TANGENT:
                glVertexAttribPointer(index, 3, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 16
                offset += 3
            elif attribute == Attribute.BITANGENT:
                glVertexAttribPointer(index, 3, GL_FLOAT, GL_FALSE, 0, None)
                self.flags |= 32
                offset += 3
        glBindVertexArray(0)        

    def update(self):
        self.configure()
        if self.flags==0:
            return
        glBindVertexArray(self.vao)
        for index in range(len(self.attributes)):
            attribute = self.attributes[index]
            if attribute == Attribute.POSITION3D and self.flags & 1:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.vertices, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~1
            elif attribute == Attribute.POSITION2D and self.flags & 1:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.vertices, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~1
            elif attribute == Attribute.NORMAL and self.flags & 2:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.normals, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~2
            elif attribute == Attribute.COLOR3 and self.flags & 4:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.colors, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~4
            elif attribute == Attribute.COLOR4 and self.flags & 4:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.colors, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~4
            elif attribute == Attribute.TEXCOORD0 and self.flags & 8:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.texcoord0, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~8
            elif attribute == Attribute.TANGENT and self.flags & 16:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.tangent, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~16
            elif attribute == Attribute.BITANGENT and self.flags & 32:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.bitangent, dtype=np.float32), GL_STATIC_DRAW)
                self.flags &= ~32
            
      

        if self.flags & 128: 
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(self.indices, dtype=np.uint32), GL_STATIC_DRAW)
            self.count = len(self.indices)
            self.flags &= ~128

        self.flags = 0
        glBindVertexArray(0)  


    def render(self):
        if self.count == 0:
            return
        self.material.apply() 
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.count, GL_UNSIGNED_INT, None)
