from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core  import *
from .material import *
from .utils import Rectangle,BoundingBox,Plane3D




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
        self.no_verts = 0


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

        self.no_verts += 1
        self.flags |= 1
        return self.no_verts - 1
    
    def add_vertex_textured(self,x,y,z,u,v):
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)
        self.texcoord0.append(u)
        self.texcoord0.append(v)
        self.no_verts += 1
        self.flags |= 1
        return self.no_verts - 1
    
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

    def set_tex_coords(self,index,u,v):
        offset = index*2
        self.texcoord0[offset] = u
        self.texcoord0[offset+1] = v
        self.flags |= 8

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
    def make_planar_mapping(self, resolution):
        if len(self.vertices) == 0 or len(self.texcoord0) == 0 or len(self.indices) == 0:
            print("Mesh has no vertices or indices")
            return

        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i + 1]
            c = self.indices[i + 2]

            v0 = self.get_position(a)
            v1 = self.get_position(b)
            v2 = self.get_position(c)

            plane = Plane3D.from_points(v0, v1, v2)

            # Convertendo as componentes da normal para valores absolutos
            plane.normal.x = abs(plane.normal.x)
            plane.normal.y = abs(plane.normal.y)
            plane.normal.z = abs(plane.normal.z)

            # Mapeamento planar baseado na maior componente da normal
            if plane.normal.x > plane.normal.y and plane.normal.x > plane.normal.z:
                self.set_tex_coords(a, v0.y * resolution, v0.z * resolution)
                self.set_tex_coords(b, v1.y * resolution, v1.z * resolution)
                self.set_tex_coords(c, v2.y * resolution, v2.z * resolution)
            elif plane.normal.y > plane.normal.x and plane.normal.y > plane.normal.z:
                self.set_tex_coords(a, v0.x * resolution, v0.z * resolution)
                self.set_tex_coords(b, v1.x * resolution, v1.z * resolution)
                self.set_tex_coords(c, v2.x * resolution, v2.z * resolution)
            else:
                self.set_tex_coords(a, v0.x * resolution, v0.y * resolution)
                self.set_tex_coords(b, v1.x * resolution, v1.y * resolution)
                self.set_tex_coords(c, v2.x * resolution, v2.y * resolution)


    def make_cube_mapping(self, resolution=1.0):
        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i+1]
            c = self.indices[i+2]

            v0 = self.get_position(a)
            v1 = self.get_position(b)
            v2 = self.get_position(c)

            # Para cada vértice, define as coordenadas UV baseadas na posição
            for v, idx in [(v0, a), (v1, b), (v2, c)]:
                u, v = 0, 0
                abs_x, abs_y, abs_z = abs(v.x), abs(v.y), abs(v.z)

                if abs_x > abs_y and abs_x > abs_z:  # Eixo X é dominante
                    u = v.z * resolution
                    v = v.y * resolution
                elif abs_y > abs_x and abs_y > abs_z:  # Eixo Y é dominante
                    u = v.x * resolution
                    v = v.z * resolution
                else:  # Eixo Z é dominante
                    u = v.x * resolution
                    v = v.y * resolution

                    self.set_texcoord(idx, u, v)
    def remove_duplicate_vertices(self):
        unique_vertices = {}
        new_indices = []
        new_vertices = []

        for i in range(len(self.indices)):
            v = self.get_position(self.indices[i])

            # Converta o vértice para uma tupla para poder comparar diretamente
            v_key = (v.x, v.y, v.z)

            if v_key not in unique_vertices:
                unique_vertices[v_key] = len(new_vertices)  # Novo índice
                new_vertices.append(v)

            # Substitui o índice antigo pelo novo
            new_indices.append(unique_vertices[v_key])

        self.vertices = new_vertices
        self.indices = new_indices
        self.flags |= 1  
        self.flags |= 128

    def remove_nearby_duplicate_vertices(self, tolerance=1e-5):
        unique_vertices = {}
        new_indices = []
        new_vertices = []

        def is_near(v1, v2, tolerance):
            return glm.length(v1 - v2) < tolerance

        for i in range(len(self.indices)):
            v = self.get_position(self.indices[i])

            # Verifica se o vértice está próximo de outros já existentes
            found = False
            for key, idx in unique_vertices.items():
                if is_near(glm.vec3(*key), v, tolerance):
                    new_indices.append(idx)
                    found = True
                    break

            if not found:
                # Se não encontrou nenhum vértice próximo, adiciona um novo
                unique_vertices[(v.x, v.y, v.z)] = len(new_vertices)
                new_vertices.append(v)
                new_indices.append(len(new_vertices) - 1)

  
        self.vertices = new_vertices
        self.indices = new_indices
        self.flags |= 1  
        self.flags |= 128  

    def merge_vertices_in_flat_areas(self, angle_threshold=0.01):
        normals = self.compute_normals()

        new_indices = []
        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i + 1]
            c = self.indices[i + 2]

            n0 = normals[a]
            n1 = normals[b]
            n2 = normals[c]

            angle1 = glm.dot(n0, n1)
            angle2 = glm.dot(n1, n2)
            angle3 = glm.dot(n2, n0)

            # Se os ângulos entre as normais forem menores que o threshold, podemos combinar os vértices
            if angle1 > angle_threshold and angle2 > angle_threshold and angle3 > angle_threshold:
                v_avg = (self.get_position(a) + self.get_position(b) + self.get_position(c)) / 3
                self.set_position(a, v_avg.x, v_avg.y, v_avg.z)
                new_indices.extend([a, a, a])  # Combina todos os índices em um único vértice
            else:
                new_indices.extend([a, b, c])

        self.indices = new_indices
        self.flags |= 1  
        self.flags |= 128
