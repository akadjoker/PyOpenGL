from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core  import *
from .material import *
from .utils import Rectangle,BoundingBox




class Mesh:
    def __init__(self,material):

        self.material = material
        self.attributes=material.attributes
        self.mode =GL_TRIANGLES
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
        self.box = BoundingBox()

        self.vao = glGenVertexArrays(1)
        self.ebo = glGenBuffers(1)

        self.flags |= 1
        self.flags |= 128

        self.tris = 0
        self.vrtx = 0


    def get_total_vertices(self):
        return len(self.vertices) // 3
    
    def get_total_triangles(self):
        return len(self.indices) // 3
    
    def get_total_indices(self):
        return len(self.indices) 
    
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
                self.vrtx = len(self.vertices) // 3
                self.flags &= ~1
            elif attribute == Attribute.POSITION2D and self.flags & 1:
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[index])
                glBufferData(GL_ARRAY_BUFFER, np.array(self.vertices, dtype=np.float32), GL_STATIC_DRAW)
                self.vrtx = len(self.vertices) // 2
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
            self.tris = len(self.indices)
            self.flags &= ~128

        self.flags = 0
        glBindVertexArray(0)  


    def add_vertex(self,x,y,z):
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)
        self.flags |= 1
        return len(self.vertices)//3
    
    def add_vertex_textured(self,x,y,z,u,v):
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)
        self.texcoord0.append(u)
        self.texcoord0.append(v)
        self.flags |= 1
        self.flags |= 8
    def add_normal(self,x,y,z):
        self.normals.append(x)
        self.normals.append(y)
        self.normals.append(z)
        self.flags |= 2
        
    def set_normal(self,index,x,y,z):
        offset = index*3
        self.normals[offset] = x
        self.normals[offset+1] = y
        self.normals[offset+2] = z
        self.flags |= 2

    def add_triangle(self,a,b,c):
        self.indices.append(a)
        self.indices.append(b)
        self.indices.append(c)
        self.flags |= 128

    def get_normal(self,index):
        offset = index*3
        return glm.vec3(self.normals[offset],self.normals[offset+1],self.normals[offset+2])
        
    
    def set_position(self,index,x,y,z):
        offset = index*3
        self.vertices[offset] = x
        self.vertices[offset+1] = y
        self.vertices[offset+2] = z
        self.flags |= 1
    
    def get_position(self,index):
        offset = index*3
        return glm.vec3(self.vertices[offset],self.vertices[offset+1],self.vertices[offset+2])

    
    def calcula_normals(self):
        
        if len(self.normals)==0:
            count = len(self.vertices)//3
            for i in range(count):
                self.normals.append(0)
                self.normals.append(0)
                self.normals.append(0)
        faces = len(self.indices)//3
       
        for i in range(faces):
            a = self.indices[i*3]
            b = self.indices[i*3 + 1]
            c = self.indices[i*3 + 2]
            v1 = self.get_position(a)
            v2 = self.get_position(b)
            v3 = self.get_position(c)
            
            sub1 = v2 - v1
            sub2 = v3 - v1
            cross = glm.cross(sub1, sub2)
            normal = glm.normalize(cross)
            self.set_normal(a, normal.x, normal.y, normal.z)
            self.set_normal(b, normal.x, normal.y, normal.z)
            self.set_normal(c, normal.x, normal.y, normal.z)
        self.flags |= 2
        

    def calcula_smoth_normals(self):
       
        normals =[]
        self.normals.clear()
  
        count = len(self.vertices)//3
        for i in range(count):
            self.normals.append(0)
            self.normals.append(0)
            self.normals.append(0)
            normals.append(glm.vec3(0,0,0))

        faces = len(self.indices)//3
        for i in range(faces):
            a = self.indices[i*3]
            b = self.indices[i*3 + 1]
            c = self.indices[i*3 + 2]
            v1 = self.get_position(a)
            v2 = self.get_position(b)
            v3 = self.get_position(c)
            sub1 = v2 - v1
            sub2 = v3 - v1
            cross = glm.cross(sub1, sub2)
            normal = glm.normalize(cross)
            normals[a] += normal
            normals[b] += normal
            normals[c] += normal
        for i in range(count):
            normal = glm.normalize(normals[i])
            self.set_normal(i, normal.x, normal.y, normal.z)
        self.flags |= 2


    def calculate_bounding_box(self):
        min_point = glm.vec3(float('inf'), float('inf'), float('inf'))
        max_point = glm.vec3(float('-inf'), float('-inf'), float('-inf'))

        count = len(self.vertices) // 3

        for i in range(count):
            v = self.get_position(i)
            
            min_point.x = min(min_point.x, v.x)
            min_point.y = min(min_point.y, v.y)
            min_point.z = min(min_point.z, v.z)

            max_point.x = max(max_point.x, v.x)
            max_point.y = max(max_point.y, v.y)
            max_point.z = max(max_point.z, v.z)

        self.box.min = min_point
        self.box.max = max_point
        return self.box
