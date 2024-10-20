from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core  import *
from .material import *
from .utils import Rectangle,BoundingBox,Plane3D
import glm
import math


def get_angle_weight(v1, v2, v3):
    a = glm.distance2(v2, v3)
    asqrt = math.sqrt(a)
    b = glm.distance2(v1, v3)
    bsqrt = math.sqrt(b)
    c = glm.distance2(v1, v2)
    csqrt = math.sqrt(c)
    if bsqrt * csqrt == 0 or asqrt * csqrt == 0 or bsqrt * asqrt == 0:
        return glm.vec3(1.0, 1.0, 1.0)

    angle1 = math.acos((b + c - a) / (2 * bsqrt * csqrt))
    angle2 = math.acos((-b + c + a) / (2 * asqrt * csqrt))
    angle3 = math.acos((b - c + a) / (2 * bsqrt * asqrt))

    return glm.vec3(angle1, angle2, angle3)


class Mesh:
    def __init__(self,material=0):

        self.material = material
        self.attributes=[]
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

    def set_attributes(self,attribute):
        self.attributes = attribute
        self.update()

    def get_bounding_box(self):
        return self.box
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


    def add_vertex(self,x,y,z,u,v,nx,ny,nz):
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)
        self.texcoord0.append(u)
        self.texcoord0.append(v)
        self.normals.append(nx)
        self.normals.append(ny)
        self.normals.append(nz)
        self.no_verts += 1
        self.flags |= 1
        self.flags |= 2
        self.flags |= 8
        return self.no_verts - 1

    def add_position(self,x,y,z):
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
        
        return glm.vec3(self.vertices[index*3],self.vertices[index*3+1],self.vertices[index*3+2])

    def flip_triangles(self):
        for i in range(0, len(self.indices), 3):
            self.indices[i+1], self.indices[i+2] = self.indices[i+2], self.indices[i+1]
        self.flags |= 128  


    
    def debug(self, batch,cor):
        batch.set_color(cor)
        for i in range(0, len(self.indices), 3):
            i0, i1, i2 = self.indices[i], self.indices[i+1], self.indices[i+2]
            v1 = glm.vec3(self.vertices[i0*3], self.vertices[i0*3+1], self.vertices[i0*3+2])
            v2 = glm.vec3(self.vertices[i1*3], self.vertices[i1*3+1], self.vertices[i1*3+2])
            v3 = glm.vec3(self.vertices[i2*3], self.vertices[i2*3+1], self.vertices[i2*3+2])
            batch.triangle_3d(v1, v2, v3)

    def recalculate_normals(self, smooth=True, angle_weighted=False):
        if not self.vertices or not self.indices:
            return
        
        self.normals = [0.0] * len(self.vertices)

        for i in range(0, len(self.indices), 3):
            i0, i1, i2 = self.indices[i], self.indices[i+1], self.indices[i+2]
            v1 = glm.vec3(self.vertices[i0*3], self.vertices[i0*3+1], self.vertices[i0*3+2])
            v2 = glm.vec3(self.vertices[i1*3], self.vertices[i1*3+1], self.vertices[i1*3+2])
            v3 = glm.vec3(self.vertices[i2*3], self.vertices[i2*3+1], self.vertices[i2*3+2])
            
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = glm.normalize(glm.cross(edge1, edge2))
                    

            if smooth:
                weight = glm.vec3(1.0, 1.0, 1.0)
                if angle_weighted:
                    weight = get_angle_weight(v1, v2, v3)

                self.normals[i0*3]   += weight.x * normal.x
                self.normals[i0*3+1] += weight.x * normal.y
                self.normals[i0*3+2] += weight.x * normal.z

                self.normals[i1*3]   += weight.y * normal.x
                self.normals[i1*3+1] += weight.y * normal.y
                self.normals[i1*3+2] += weight.y * normal.z

                self.normals[i2*3]   += weight.z * normal.x
                self.normals[i2*3+1] += weight.z * normal.y
                self.normals[i2*3+2] += weight.z * normal.z
            else:
                for idx in [i0, i1, i2]:
                    self.normals[idx*3] = normal.x
                    self.normals[idx*3+1] = normal.y
                    self.normals[idx*3+2] = normal.z

        if smooth:
            for i in range(0, len(self.normals), 3):
                normal = glm.vec3(self.normals[i], self.normals[i+1], self.normals[i+2])
                normalized = glm.normalize(normal)
                self.normals[i] = normalized.x
                self.normals[i+1] = normalized.y
                self.normals[i+2] = normalized.z
        
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
        if len(self.vertices) == 0 or len(self.indices) == 0:
            print("Mesh has no vertices or indices")
        if len(self.texcoord0) == 0:
            self.texcoord0 = [0.0] * (len(self.vertices) // 3 * 2)  # 2 floats por vertice
        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i + 1]
            c = self.indices[i + 2]

            v0 = self.get_position(a)
            v1 = self.get_position(b)
            v2 = self.get_position(c)

            
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = glm.normalize(glm.cross(edge1, edge2))
          

            # Normalizar a normal do plano (valores absolutos)
            normal.x = abs(normal.x)
            normal.y = abs(normal.y)
            normal.z = abs(normal.z)

            # Mapeamento planar baseado na maior componente da normal
            if normal.x > normal.y and normal.x > normal.z:
                # Eixo X dominante (projetar no plano YZ)
                self.set_tex_coords(a, v0.y * resolution, v0.z * resolution)
                self.set_tex_coords(b, v1.y * resolution, v1.z * resolution)
                self.set_tex_coords(c, v2.y * resolution, v2.z * resolution)
            elif normal.y > normal.x and normal.y > normal.z:
                # Eixo Y dominante (projetar no plano XZ)
                self.set_tex_coords(a, v0.x * resolution, v0.z * resolution)
                self.set_tex_coords(b, v1.x * resolution, v1.z * resolution)
                self.set_tex_coords(c, v2.x * resolution, v2.z * resolution)
            else:
                # Eixo Z dominante (projetar no plano XY)
                self.set_tex_coords(a, v0.x * resolution, v0.y * resolution)
                self.set_tex_coords(b, v1.x * resolution, v1.y * resolution)
                self.set_tex_coords(c, v2.x * resolution, v2.y * resolution)

    def make_cube_mapping(self, resolution=1.0):
        if len(self.vertices) == 0 or len(self.indices) == 0:
            print("Mesh has no vertices or indices")
            return
        if len(self.texcoord0) == 0:
            self.texcoord0 = [0.0] * (len(self.vertices) // 3 * 2)  # 2 floats por vertice

        for i in range(len(self.vertices) // 3):
            v = self.get_position(i)

            # Calcular o mapeamento cúbico com base na maior componente
            abs_x, abs_y, abs_z = abs(v.x), abs(v.y), abs(v.z)

            if abs_x >= abs_y and abs_x >= abs_z:
                # Mapeamento para as faces X positivas/negativas
                if v.x > 0:
                    # Face X positiva (projetar no plano YZ)
                    u = (v.z / resolution + 1.0) * 0.5
                    v = (v.y / resolution + 1.0) * 0.5
                else:
                    # Face X negativa (projetar no plano YZ)
                    u = (v.z / resolution + 1.0) * 0.5
                    v = (v.y / resolution + 1.0) * 0.5

            elif abs_y >= abs_x and abs_y >= abs_z:
                # Mapeamento para as faces Y positivas/negativas
                if v.y > 0:
                    # Face Y positiva (projetar no plano XZ)
                    u = (v.x / resolution + 1.0) * 0.5
                    v = (v.z / resolution + 1.0) * 0.5
                else:
                    # Face Y negativa (projetar no plano XZ)
                    u = (v.x / resolution + 1.0) * 0.5
                    v = (v.z / resolution + 1.0) * 0.5

            else:
                # Mapeamento para as faces Z positivas/negativas
                if v.z > 0:
                    # Face Z positiva (projetar no plano XY)
                    u = (v.x / resolution + 1.0) * 0.5
                    v = (v.y / resolution + 1.0) * 0.5
                else:
                    # Face Z negativa (projetar no plano XY)
                    u = (v.x / resolution + 1.0) * 0.5
                    v = (v.y / resolution + 1.0) * 0.5
            self.set_tex_coords(i, u, v)

    def make_spherical_mapping(self, radius=1.0):
        if len(self.vertices) == 0 or len(self.indices) == 0:
            print("Mesh has no vertices or indices")
            return
        if len(self.texcoord0) == 0:
            self.texcoord0 = [0.0] * (len(self.vertices) // 3 * 2)  # 2 floats por vertice


        for i in range(len(self.vertices) // 3):
            v = self.get_position(i)
            x, y, z = v.x / radius, v.y / radius, v.z / radius

            theta = math.atan2(z, x)  # Ângulo em torno do eixo Y
            phi = math.acos(y / math.sqrt(x * x + y * y + z * z))  # Ângulo a partir do eixo Y
            u = (theta + math.pi) / (2 * math.pi)  # u mapeado de [0, 2*pi] para [0, 1]
            v = phi / math.pi  # v mapeado de [0, pi] para [0, 1]

            self.set_tex_coords(i, u, v)

    def calculate_tangents(self):
        if len(self.vertices) == 0 or len(self.indices) == 0 or len(self.texcoord0) == 0:
            print("Mesh has no vertices, indices, or texture coordinates")
            return

        self.tangents = [0.0] * len(self.vertices)
        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i + 1]
            c = self.indices[i + 2]

            v0 = self.get_position(a)
            v1 = self.get_position(b)
            v2 = self.get_position(c)

            uv0 = self.get_tex_coords(a)
            uv1 = self.get_tex_coords(b)
            uv2 = self.get_tex_coords(c)

            delta_pos1 = v1 - v0
            delta_pos2 = v2 - v0

            # Calcular as diferenças de coordenadas de textura
            delta_uv1 = glm.vec2(uv1.x - uv0.x, uv1.y - uv0.y)
            delta_uv2 = glm.vec2(uv2.x - uv0.x, uv2.y - uv0.y)

            # Calcular o fator do determinante
            determinant = delta_uv1.x * delta_uv2.y - delta_uv1.y * delta_uv2.x
            if determinant == 0.0:
                determinant = 1.0  # Evitar divisão por zero

            r = 1.0 / determinant

            # Calcular o vetor tangente para o triângulo
            tangent = (delta_pos1 * delta_uv2.y - delta_pos2 * delta_uv1.y) * r

            # Acumular o tangente nos vértices do triângulo
            for idx in [a, b, c]:
                self.tangents[idx * 3] += tangent.x
                self.tangents[idx * 3 + 1] += tangent.y
                self.tangents[idx * 3 + 2] += tangent.z

        # Normalizar os tangentes acumulados para cada vértice
        for i in range(0, len(self.tangents), 3):
            tangent = glm.vec3(self.tangents[i], self.tangents[i + 1], self.tangents[i + 2])
            normalized_tangent = glm.normalize(tangent)
            self.tangents[i] = normalized_tangent.x
            self.tangents[i + 1] = normalized_tangent.y
            self.tangents[i + 2] = normalized_tangent.z

    def calculate_tangents_and_bitangents(self):
        if len(self.vertices) == 0 or len(self.indices) == 0 or len(self.texcoord0) == 0:
            print("Mesh has no vertices, indices, or texture coordinates")
            return


        self.tangents = [0.0] * len(self.vertices)
        self.bitangents = [0.0] * len(self.vertices)

        for i in range(0, len(self.indices), 3):
            a = self.indices[i]
            b = self.indices[i + 1]
            c = self.indices[i + 2]

            v0 = self.get_position(a)
            v1 = self.get_position(b)
            v2 = self.get_position(c)

            uv0 = self.get_tex_coords(a)
            uv1 = self.get_tex_coords(b)
            uv2 = self.get_tex_coords(c)

            delta_pos1 = v1 - v0
            delta_pos2 = v2 - v0

            delta_uv1 = glm.vec2(uv1.x - uv0.x, uv1.y - uv0.y)
            delta_uv2 = glm.vec2(uv2.x - uv0.x, uv2.y - uv0.y)

            # Calcular o fator do determinante
            determinant = delta_uv1.x * delta_uv2.y - delta_uv1.y * delta_uv2.x
            if determinant == 0.0:
                determinant = 1.0 

            r = 1.0 / determinant

            # Calcular os vetores tangente e bitangente para o triângulo
            tangent = (delta_pos1 * delta_uv2.y - delta_pos2 * delta_uv1.y) * r
            bitangent = (delta_pos2 * delta_uv1.x - delta_pos1 * delta_uv2.x) * r

            # Acumular os tangentes e bitangentes nos vértices do triângulo
            for idx in [a, b, c]:
                self.tangents[idx * 3] += tangent.x
                self.tangents[idx * 3 + 1] += tangent.y
                self.tangents[idx * 3 + 2] += tangent.z

                self.bitangents[idx * 3] += bitangent.x
                self.bitangents[idx * 3 + 1] += bitangent.y
                self.bitangents[idx * 3 + 2] += bitangent.z

        # Normalizar os tangentes e bitangentes acumulados para cada vértice
        for i in range(0, len(self.tangents), 3):
            tangent = glm.vec3(self.tangents[i], self.tangents[i + 1], self.tangents[i + 2])
            normalized_tangent = glm.normalize(tangent)
            self.tangents[i] = normalized_tangent.x
            self.tangents[i + 1] = normalized_tangent.y
            self.tangents[i + 2] = normalized_tangent.z

            bitangent = glm.vec3(self.bitangents[i], self.bitangents[i + 1], self.bitangents[i + 2])
            normalized_bitangent = glm.normalize(bitangent)
            self.bitangents[i] = normalized_bitangent.x
            self.bitangents[i + 1] = normalized_bitangent.y
            self.bitangents[i + 2] = normalized_bitangent.z


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

    def transform(self, matrix):
        for i in range(self.get_total_vertices()):
            v = self.get_position(i)
            v = glm.vec3(matrix * glm.vec4(v, 1))
            self.set_position(i, v.x, v.y, v.z)
        self.calculate_bounding_box()
    def translate(self, x, y, z):
        for i in range(self.get_total_vertices()):
            v = self.get_position(i)
            v = glm.vec3(v.x + x, v.y + y, v.z + z)
            self.set_position(i, v.x, v.y, v.z)
        self.calculate_bounding_box()
    def scale (self, x, y, z):
        for i in range(self.get_total_vertices()):
            v = self.get_position(i)
            v = glm.vec3(v.x * x, v.y * y, v.z * z)
            self.set_position(i, v.x, v.y, v.z)
        self.calculate_bounding_box()