
import math
from pathlib import Path
import os

from .shader import Shader
from .texture import Texture
from .material import Material
from .mesh import Mesh
from .color import *
from .core import *
from .stream import ByteStream


class Mat:
    def __init__(self, name):
        self.name = name
        self.diffuse = (1.0, 1.0, 1.0)  
        self.specular = (1.0, 1.0, 1.0)  
        self.shininess = 32.0 
        self.diffuse_map = None  
        self.specular_map = None 
        self.normal_map = None 
        self.shininess_map = None

  
class Importer:
    def __init__(self,model,atributes):
        self.stack = []
        self.stream = ByteStream()
        self.texturePath = ''
        self.model = model
        self.attributes = atributes

        
    
    def load(self,  fileName,texturePath):
        self.texturePath = texturePath
        self.stream.load(fileName)
        self.stack = []
        HEADER=['0','0','0','0']
        HEADER[0] = self.stream.read_char()
        HEADER[1] = self.stream.read_char()
        HEADER[2] = self.stream.read_char()
        HEADER[3] = self.stream.read_char()
        if HEADER[0] != 'H' or HEADER[1] != '3' or HEADER[2] != 'D' or HEADER[3] != 'S':
            print("Error loading file")
            return False
        
        version  = self.stream.read_short()
        #print(f"Version: {version}")
        if version != 5:
            print("Error loading file")
            return False

  

        while self.stream.position() < self.stream.size():
            chunk_id, chunk_size = self.read_chunk()  # Lê o identificador e o tamanho do chunk
            #print(f"Lendo chunk: {chunk_id}, tamanho: {chunk_size}")
       
            if chunk_id == 'MAT#':  
                 self.read_material_data(chunk_size)
            elif chunk_id == 'MESH':
                self.read_mesh_data(chunk_size)
            else:
                print(f"Chunk {chunk_id} not found")
            
            self.break_chunk()

        return True

    def read_material_data(self, chunk_size):
        initial_pos = self.stream.position() 
        material = Material()
        self.model.add_material(material)
        while self.stream.position() - initial_pos < chunk_size:
            tex_chunk_id, tex_chunk_size = self.read_chunk()  
            if tex_chunk_id == 'TEX#':
                self.read_textures(material,tex_chunk_size) 
            else:
                print(f"Chunk {tex_chunk_id} not found")
            self.break_chunk()
  


    def read_textures(self, material, chunk_size):
        initial_pos = self.stream.position()  
        while self.stream.position() - initial_pos < chunk_size:
            texture_name = Path(self.stream.read_UTFstring()).name
            texture_name =texture_name.lower()
            

            textureId = texture_name.split(".")[0]
           
            base_name, ext = os.path.splitext(texture_name) 

            diffuse_texture  = f"{base_name}{ext}"
            normal_texture   = f"{base_name}_normal{ext}"  
            specular_texture = f"{base_name}_specular{ext}"  

            if  os.path.exists(self.texturePath+diffuse_texture):
                texture = Render.load_texture(self.texturePath+diffuse_texture, textureId)
                material.add_texture(texture)
                if os.path.exists(self.texturePath+normal_texture):
                    texture = Render.load_texture(self.texturePath+normal_texture, "normal_"+textureId)
                    material.add_texture(texture)
                #if os.path.exists(self.texturePath+specular_texture):
                #    texture = Render.load_texture(self.texturePath+specular_texture, "specular_"+textureId)
                #    material.add_texture(texture)
            else:
                print(f" Tetxure with name {diffuse_texture} not found")
                
            

            

          
    def read_mesh_data(self, chunk_size):
        while self.chunk_size() > 0:
            chunk_id, chunk_size = self.read_chunk()  # Lê o identificador e o tamanho do chunk
            if chunk_id == 'SURF':
                self.read_surface_data(chunk_size)
           
            self.break_chunk()


           
            
    def read_surface_data(self, chunk_size): 
        material = self.stream.read_short()
        mesh = Mesh(material)
        #print(f"Mehs Material: {material}")
        while self.chunk_size():
            chunk_id, chunk_size = self.read_chunk()  
            if chunk_id == 'VRTS':
                self.read_vertices(mesh,chunk_size)
            elif chunk_id == 'TRIS':
                self.read_indices(mesh,chunk_size)            
            self.break_chunk()
        
        mesh.calculate_bounding_box()
        mesh.calculate_tangents()
        mesh.set_attributes(self.attributes)
        self.model.add_mesh(mesh)
            
        


    def read_vertices(self, mesh,chunk_size):
        stride = (3 + 3 + 2) * 4
        size = chunk_size // stride
        index = 0
        while index < size:
            x = self.stream.read_float()
            y = self.stream.read_float()
            z = self.stream.read_float()
            nx = self.stream.read_float()
            ny = self.stream.read_float()
            nz = self.stream.read_float()
            u = self.stream.read_float()
            v = self.stream.read_float()
            mesh.add_vertex(x, y, z,u,v, nx, ny, nz)
            index += 1
            #print(f"Vertice: ({x}, {y}, {z}) ({nx}, {ny}, {nz}) ({u}, {v})")

    def read_indices(self,mesh, chunk_size):
        stride = 3 * 4
        size = chunk_size // stride
        index = 0
        while index < size:
            a = self.stream.read_int()
            b = self.stream.read_int()
            c = self.stream.read_int()
            mesh.add_triangle(a, b, c)
            index += 1
            #print(f"Indice: {a}, {b}, {c}")

    def read_chunk(self):
        chunk_id = self.stream.read_string_size(4)
        chunk_size = self.stream.read_int()
        self.stack.append(self.stream.position() + chunk_size)
        return chunk_id, chunk_size
    
    def break_chunk(self):
        end_pos = self.stack.pop()  
        self.stream.seek(end_pos)   

    def chunk_size(self):
        back = self.stack[-1]
        return back - self.stream.position()
    

class Exporter:
    def __init__(self):
        self.stack = []
        self.stream = ByteStream()
    

    def beginChunk(self, tag):
        self.stream.write_string_size(tag, 4)
        self.stack.append(self.stream.position())
        self.stream.write_int(0)



    
    def endChunk(self):
        pos = self.stream.position()  # Posição atual do cursor (final do chunk)
        start_pos = self.stack.pop()
        chunk_size = pos - (start_pos + 4)
        self.stream.seek(start_pos)
        self.stream.write_int(chunk_size)  # Escreve o tamanho do chunk
        self.stream.seek(pos)

  

class Builder:
    def __init__(self):
        pass

    

    @staticmethod
    def load_static_model(model,attributes,file_path, texturePath):
        impoter = Importer(model,attributes)
        return impoter.load(file_path, texturePath)

    @staticmethod
    def create_cube(material=0):
        mesh = Mesh(material)

        # Face de trás (normal (0, 0, -1)) 
        mesh.add_vertex(-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, -1.0)  # V0
        mesh.add_vertex( 0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, -1.0)  # V1
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 1.0, 0.0, 0.0, -1.0)  # V2
        mesh.add_vertex(-0.5,  0.5, -0.5, 0.0, 1.0, 0.0, 0.0, -1.0)  # V3

        # Face da frente (normal (0, 0, 1)) 
        mesh.add_vertex(-0.5, -0.5,  0.5, 0.0, 0.0, 0.0, 0.0, 1.0)  # V4
        mesh.add_vertex( 0.5, -0.5,  0.5, 1.0, 0.0, 0.0, 0.0, 1.0)  # V5
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, 0.0, 0.0, 1.0)  # V6
        mesh.add_vertex(-0.5,  0.5,  0.5, 0.0, 1.0, 0.0, 0.0, 1.0)  # V7

        # Face da esquerda (normal (-1, 0, 0)) 
        mesh.add_vertex(-0.5, -0.5, 0.5, 0.0, 0.0, -1.0, 0.0, 0.0)  # V8
        mesh.add_vertex(-0.5,  0.5, 0.5, 1.0, 0.0, -1.0, 0.0, 0.0)  # V9
        mesh.add_vertex(-0.5,  0.5,  -0.5, 1.0, 1.0, -1.0, 0.0, 0.0)  # V10
        mesh.add_vertex(-0.5, -0.5,  -0.5, 0.0, 1.0, -1.0, 0.0, 0.0)  # V11

        # Face da direita (normal (1, 0, 0)) 
        mesh.add_vertex( 0.5, -0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 0.0)  # V12
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 0.0, 1.0, 0.0, 0.0)  # V13
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, 1.0, 0.0, 0.0)  # V14
        mesh.add_vertex( 0.5, -0.5,  0.5, 0.0, 1.0, 1.0, 0.0, 0.0)  # V15

        # Face de cima (normal (0, 1, 0)) 
        mesh.add_vertex(-0.5,  0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0)  # V16
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0)  # V17
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, 0.0, 1.0, 0.0)  # V18
        mesh.add_vertex(-0.5,  0.5,  0.5, 0.0, 1.0, 0.0, 1.0, 0.0)  # V19

        # Face de baixo (normal (0, -1, 0)) - Sentido anti-horário (CCW)
        mesh.add_vertex(-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.0, 0.0)  # V20
        mesh.add_vertex( 0.5, -0.5, -0.5, 1.0, 0.0, 0.0, -1.0, 0.0)  # V21
        mesh.add_vertex( 0.5, -0.5,  0.5, 1.0, 1.0, 0.0, -1.0, 0.0)  # V22
        mesh.add_vertex(-0.5, -0.5,  0.5, 0.0, 1.0, 0.0, -1.0, 0.0)  # V23

        # Índices para os triângulos de cada face (organizados em sentido anti-horário)
        mesh.indices = [
            2, 1, 0,  3, 2, 0,   # Face de trás
            4, 5, 6,  4, 6, 7,   # Face da frente
            8, 9, 10,  8, 10, 11, # Face da esquerda
           12, 13, 14,  12, 14, 15, # Face da direita
            18, 17, 16,  19, 18, 16, # Face de cima
            20, 21, 22,  20, 22, 23  # Face de baixo
        ]

        mesh.calculate_bounding_box()

        return mesh

    @staticmethod
    def create_cube_double(material=0):
        mesh = Mesh(material)

        # Face de trás (normal (0, 0, -1)) 
        mesh.add_vertex(-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 1.0)  # V0
        mesh.add_vertex( 0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0)  # V1
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 1.0, 0.0, 0.0, 1.0)  # V2
        mesh.add_vertex(-0.5,  0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0)  # V3

        # Face da frente (normal (0, 0, 1)) 
        mesh.add_vertex(-0.5, -0.5,  0.5, 0.0, 0.0, 0.0, 0.0, -1.0)  # V4
        mesh.add_vertex( 0.5, -0.5,  0.5, 1.0, 0.0, 0.0, 0.0, -1.0)  # V5
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, 0.0, 0.0, -1.0)  # V6
        mesh.add_vertex(-0.5,  0.5,  0.5, 0.0, 1.0, 0.0, 0.0, -1.0)  # V7

        # Face da esquerda (normal (-1, 0, 0)) 
        mesh.add_vertex(-0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0)  # V8
        mesh.add_vertex(-0.5,  0.5, 0.5, 1.0, 0.0, 1.0, 0.0, 0.0)  # V9
        mesh.add_vertex(-0.5,  0.5,  -0.5, 1.0, 1.0, 1.0, 0.0, 0.0)  # V10
        mesh.add_vertex(-0.5, -0.5,  -0.5, 0.0, 1.0, 1.0, 0.0, 0.0)  # V11

        # Face da direita (normal (1, 0, 0)) 
        mesh.add_vertex( 0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0)  # V12
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 0.0, -1.0, 0.0, 0.0)  # V13
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, -1.0, 0.0, 0.0)  # V14
        mesh.add_vertex( 0.5, -0.5,  0.5, 0.0, 1.0, -1.0, 0.0, 0.0)  # V15

        # Face de cima (normal (0, 1, 0)) 
        mesh.add_vertex(-0.5,  0.5, -0.5, 0.0, 0.0, 0.0, -1.0, 0.0)  # V16
        mesh.add_vertex( 0.5,  0.5, -0.5, 1.0, 0.0, 0.0, -1.0, 0.0)  # V17
        mesh.add_vertex( 0.5,  0.5,  0.5, 1.0, 1.0, 0.0, -1.0, 0.0)  # V18
        mesh.add_vertex(-0.5,  0.5,  0.5, 0.0, 1.0, 0.0, -1.0, 0.0)  # V19

        # Face de baixo (normal (0, -1, 0)) - Sentido anti-horário (CCW)
        mesh.add_vertex(-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0)  # V20
        mesh.add_vertex( 0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0)  # V21
        mesh.add_vertex( 0.5, -0.5,  0.5, 1.0, 1.0, 0.0, 1.0, 0.0)  # V22
        mesh.add_vertex(-0.5, -0.5,  0.5, 0.0, 1.0, 0.0, 1.0, 0.0)  # V23

        # Índices para os triângulos de cada face (organizados em sentido anti-horário)
        mesh.indices = [
            1,2,0,   0,2,3,
            6, 5, 4,  7, 6, 4,
            10, 9, 8,  11, 10, 8,
            14, 13, 12,  15, 14, 12,
            16, 17, 18,  16, 18, 19,
            22, 21, 20,  23, 22, 20
        ]

        mesh.calculate_bounding_box()

        return mesh

    @staticmethod
    def create_tiles(stacks, slices, tilesX, tilesY, material=0):

        mesh = Mesh(material)
        min_point = glm.vec3(float('inf'), 0, float('inf'))
        max_point = glm.vec3(float('-inf'), 0, float('-inf'))

        for i in range(stacks + 1):  
            y = i / stacks * tilesY
            for j in range(slices + 1): 
                x = j / slices * tilesX
                mesh.add_vertex(x, 0, y, x, y,0,1,0)
                


                min_point.x = min(min_point.x, x)
                min_point.z = min(min_point.z, y)
                max_point.x = max(max_point.x, x)
                max_point.z = max(max_point.z, y)

        center = (min_point + max_point) * 0.5


        for i in range(mesh.get_total_vertices()):
            v = mesh.get_position(i)
            v.x -= center.x
            v.z -= center.z
            mesh.set_position(i, v.x, v.y, v.z)

        for i in range(stacks):
            for j in range(slices):
                index = i * (slices + 1) + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)

        
        mesh.calculate_bounding_box()
        
        return mesh
    @staticmethod
    def create_plane(w,d, material=0):

        mesh = Mesh(material)

        mesh.add_vertex(-w/2.0,0.0,-d/2.0,0.0,1.0,0.0,0.0,1.0)
        mesh.add_vertex(-w/2.0,0.0, d/2.0,0.0,0.0,0.0,0.0,1.0)
        mesh.add_vertex( w/2.0,0.0, d/2.0,1.0,0.0,0.0,0.0,1.0)
        mesh.add_vertex( w/2.0,0.0,-d/2.0,1.0,1.0,0.0,0.0,1.0)

        mesh.add_triangle(0, 1, 2)
        mesh.add_triangle(0, 2, 3)
      
        
        mesh.calculate_bounding_box()
        
        return mesh
    @staticmethod
    def create_sphere(stacks, slices, material=0):
        mesh = Mesh(material)
        pi = 3.14159265359

        for i in range(stacks + 1): 
            phi = i * pi / stacks  
            for j in range(slices + 1):  
                theta = j * 2.0 * pi / slices  

    
                x = math.sin(phi) * math.cos(theta)
                y = math.cos(phi)
                z = math.sin(phi) * math.sin(theta)

    
                nx, ny, nz = x, y, z

                u = j / slices
                v = i / stacks


                mesh.add_vertex(x, y, z, u, v, nx, ny, nz)


        for i in range(stacks):
            for j in range(slices):
                index = (slices + 1) * i + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)

        mesh.calculate_bounding_box

        return mesh



    @staticmethod
    def create_cone(stacks, slices, material=0):
        mesh = Mesh(material)
        pi = math.pi
        stack_height = 1.0 / stacks
        slice_angle = 2.0 * pi / slices

        # Geração dos vértices e normais para o corpo do cone
        for i in range(stacks + 1):
            y = -0.5 + i * stack_height  # Altura de cada stack
            radius = 0.5 - y  # Raio diminui à medida que subimos o cone
            for j in range(slices + 1):
                x = radius * math.cos(j * slice_angle)
                z = radius * math.sin(j * slice_angle)

                # Calcular normal para o corpo do cone
                nx = math.cos(j * slice_angle)
                nz = math.sin(j * slice_angle)
                ny = 0.5  

                normal = glm.normalize(glm.vec3(nx, ny, nz))  


                u = j / slices
                v = i / stacks

                # Adicionar vértice com posição, textura e normal
                mesh.add_vertex(x, y, z, u, v, normal.x, normal.y, normal.z)
                mesh.box.add_point(x, y, z)

        # Gerar os triângulos para o corpo do cone
        for i in range(stacks):
            for j in range(slices):
                index = (slices + 1) * i + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)

        # Geração da base do cone
        base_start_index = mesh.get_total_vertices()
        y_bottom = -0.5

        # Vértice central da base
        mesh.add_vertex(0.0, y_bottom, 0.0, 0.5, 0.5, 0.0, -1.0, 0.0)  # Normal apontando para baixo

        # Geração dos vértices ao redor da base
        for i in range(slices + 1):
            x = math.cos(i * slice_angle)
            z = math.sin(i * slice_angle)

            # Adicionar vértices com normais apontando para baixo
            mesh.add_vertex(x, y_bottom, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0), 0.0, -1.0, 0.0)
            mesh.box.add_point(x, y_bottom, z)

        # Gerar os triângulos da base
        for i in range(slices):
            mesh.add_triangle(base_start_index, base_start_index + i + 1, base_start_index + (i + 1) % slices + 1)
        
        mesh.calculate_bounding_box()

        return mesh




    @staticmethod
    def create_torus(stacks, slices, inner_radius, outer_radius, material=0):
        mesh = Mesh(material)
        pi = math.pi
        stack_angle = 2.0 * pi / stacks
        slice_angle = 2.0 * pi / slices


        for i in range(stacks + 1):
            u = i * stack_angle
            for j in range(slices + 1):
                v = j * slice_angle
                x = (outer_radius + inner_radius * math.cos(v)) * math.cos(u)
                y = (outer_radius + inner_radius * math.cos(v)) * math.sin(u)
                z = inner_radius * math.sin(v)


                nx = math.cos(v) * math.cos(u)
                ny = math.cos(v) * math.sin(u)
                nz = math.sin(v)

                normal = glm.normalize(glm.vec3(nx, ny, nz))  
                texture_u = i / stacks
                texture_v = j / slices
                mesh.box.add_point(x, y, z)
                mesh.add_vertex(x, y, z, texture_u, texture_v, normal.x, normal.y, normal.z)


        for i in range(stacks):
            for j in range(slices):
                index = (slices + 1) * i + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)

        mesh.calculate_bounding_box()
        return mesh

    @staticmethod
    def create_cylinder(stacks, slices, radius, height, material=0):
        mesh = Mesh(material)
        pi = math.pi
        stack_height = height / stacks
        slice_angle = 2.0 * pi / slices

    
        for i in range(stacks + 1):
            y = -height / 2.0 + i * stack_height
            for j in range(slices + 1):
                x = radius * math.cos(j * slice_angle)
                z = radius * math.sin(j * slice_angle)
                nx = math.cos(j * slice_angle)
                nz = math.sin(j * slice_angle)
                normal = glm.normalize(glm.vec3(nx, 0.0, nz))  
                mesh.add_vertex(x, y, z, j / slices, i / stacks, normal.x, normal.y, normal.z)
                mesh.box.add_point(x, y, z)

    
        for i in range(stacks):
            for j in range(slices):
                index = (slices + 1) * i + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)


        base_start_index = mesh.get_total_vertices()
        y_bottom = -height / 2.0
        y_top = height / 2.0

    
        mesh.add_vertex(0.0, y_bottom, 0.0, 0.5, 0.5, 0.0, -1.0, 0.0) 
        for j in range(slices + 1):
            x = radius * math.cos(j * slice_angle)
            z = radius * math.sin(j * slice_angle)
            mesh.add_vertex(x, y_bottom, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0), 0.0, -1.0, 0.0)  
            mesh.box.add_point(x, y_bottom, z)


        for j in range(slices):
            mesh.add_triangle(base_start_index, base_start_index + j + 1, base_start_index + (j + 1) % slices + 1)


        top_start_index = mesh.get_total_vertices()
        mesh.add_vertex(0.0, y_top, 0.0, 0.5, 0.5, 0.0, 1.0, 0.0)  
        for j in range(slices + 1):
            x = radius * math.cos(j * slice_angle)
            z = radius * math.sin(j * slice_angle)
            mesh.add_vertex(x, y_top, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0), 0.0, 1.0, 0.0)  
            mesh.box.add_point(x, y_top, z)


        for j in range(slices):
            mesh.add_triangle(top_start_index, top_start_index + (j + 1) % slices + 1, top_start_index + j + 1)

        mesh.calculate_bounding_box()
        return mesh

    @staticmethod
    def create_pyramid(sides, height, material=0):
        mesh = Mesh(material)
        pi = math.pi
        slice_angle = 2.0 * pi / sides

        base_y = -height / 2.0
        mesh.add_vertex(0.0, base_y, 0.0, 0.5, 0.5, 0.0, -1.0, 0.0)  
        for i in range(sides + 1):
            x = math.cos(i * slice_angle)
            z = math.sin(i * slice_angle)
            mesh.add_vertex(x, base_y, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0), 0.0, -1.0, 0.0)  
            mesh.box.add_point(x, base_y, z)


        top_y = height / 2.0
        mesh.add_vertex(0.0, top_y, 0.0, 0.5, 0.5, 0.0, 1.0, 0.0)  
        mesh.box.add_point(0.0, top_y, 0.0)

        top_index = mesh.get_total_vertices() - 1
        for i in range(sides):
            x1 = math.cos(i * slice_angle)
            z1 = math.sin(i * slice_angle)
            x2 = math.cos((i + 1) % sides * slice_angle)
            z2 = math.sin((i + 1) % sides * slice_angle)


            face_normal = glm.normalize(glm.cross(glm.vec3(x2 - x1, top_y - base_y, z2 - z1), glm.vec3(0, 1, 0)))


            mesh.add_triangle(top_index, i + 1, (i + 2) % (sides + 1))
            mesh.add_triangle(0, (i + 2) % (sides + 1), i + 1)


        mesh.calculate_bounding_box()
        return mesh

    @staticmethod
    def create_spherical_plane(stacks, slices, radius, material=0):
        mesh = Mesh(material)
        pi = math.pi

        for i in range(stacks + 1):
            phi = i * pi / stacks / 2  
            for j in range(slices + 1):
                theta = j * 2.0 * pi / slices
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)

        
                normal = glm.normalize(glm.vec3(x, y, z))

    
                u = j / slices
                v = i / stacks

            
                mesh.add_vertex(x, y, z, u, v, normal.x, normal.y, normal.z)
                mesh.box.add_point(x, y, z)


        for i in range(stacks):
            for j in range(slices):
                index = (slices + 1) * i + j
                mesh.add_triangle(index, index + slices + 1, index + slices + 2)
                mesh.add_triangle(index, index + slices + 2, index + 1)

        mesh.calculate_bounding_box()
        return mesh

    @staticmethod
    def create_disc(slices, radius, material=0):
        mesh = Mesh(material)
        pi = math.pi
        slice_angle = 2.0 * pi / slices

        mesh.add_vertex(0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 1.0, 0.0)  

    
        for i in range(slices + 1):
            x = radius * math.cos(i * slice_angle)
            z = radius * math.sin(i * slice_angle)

        
            mesh.add_vertex(x, 0.0, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0), 0.0, 1.0, 0.0)


        for i in range(slices):
            mesh.add_triangle(0, i + 1, (i + 2) % (slices + 1))

        mesh.calculate_bounding_box()

        return mesh
    

    @staticmethod
    def load_mtl(filename):
        materials = {}
        current_material = None

        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if not parts or parts[0].startswith('#'):
                    continue

                if parts[0] == 'newmtl':  # Novo material
                    current_material = Mat(parts[1])
                    materials[parts[1]] = current_material

                elif parts[0] == 'Kd':  # Cor difusa
                    current_material.diffuse = (float(parts[1]), float(parts[2]), float(parts[3]))

                elif parts[0] == 'Ks':  # Cor especular
                    current_material.specular = (float(parts[1]), float(parts[2]), float(parts[3]))

                elif parts[0] == 'Ns':  # Brilho
                    current_material.shininess = float(parts[1])

                elif parts[0] == 'map_Kd':  # Textura difusa
                    current_material.diffuse_map = parts[1]

                elif parts[0] == 'map_Ks':  # Textura especular
                    current_material.specular_map = parts[1]

                elif parts[0] == 'map_Ns':  # Textura brilho
                    current_material.shininess_map = parts[1]

                elif parts[0] == 'map_bump':  # Textura normal
                    current_material.normal_map = parts[1]

        return materials

    @staticmethod
    def load_obj(file_path, material=0):
        with open(file_path, 'r') as file:
            data = file.read()

        return Builder.process_obj(data, material)

    @staticmethod
    def process_obj(data, material):
        mesh = Mesh(material)
        vertices = []
        texcoords = []
        normals = []
        faces = []
        lines = data.split("\n")
        hasNormals = False
        hasTexCoords = False
        for line in lines:
            parts = line.strip().split()
            if not parts or parts[0].startswith('#'):
                continue  # Ignorar 

            if parts[0] == 'v':  # Vértices
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vertices.append((x, y, z))

            elif parts[0] == 'vt':  # Coordenadas de textura
                u, v = float(parts[1]), float(parts[2])
                texcoords.append((u, v))
                hasTexCoords = True

            elif parts[0] == 'vn':  # Normais
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                normals.append((nx, ny, nz))
                hasNormals = True

            elif parts[0] == 'f':  # Faces
                face = []
                for vert in parts[1:]:
                    # Tratar vértices no formato: v/vt/vn 
                    indices = vert.split('/')
                    vertex_index = int(indices[0]) - 1
                    texcoord_index = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None
                    normal_index = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else None
                    face.append((vertex_index, texcoord_index, normal_index))
                faces.append(face)

        for face in faces:
            indices = []
            for vertex_index, texcoord_index, normal_index in face:
                x, y, z = vertices[vertex_index]
                u, v = texcoords[texcoord_index] if texcoord_index is not None else (0.0, 0.0)
                nx, ny, nz = normals[normal_index] if normal_index is not None else (0.0, 0.0, 0.0)
                index = mesh.add_vertex(x, y, z, u, v, nx, ny, nz)
                indices.append(index)


            if len(indices) == 3:
                mesh.add_triangle(indices[0], indices[1], indices[2])

            elif len(indices) == 4:
                mesh.add_triangle(indices[0], indices[1], indices[2])
                mesh.add_triangle(indices[0], indices[2], indices[3])

        if not hasNormals:
            mesh.recalculate_normals(smooth=True, angle_weighted=False)
        if  not hasTexCoords:
            mesh.make_planar_mapping(1.0)
        mesh.calculate_bounding_box()

        return mesh
    
    @staticmethod
    def load_objs(file_path, material_lib):
        with open(file_path, 'r') as file:
            data = file.read()

        return Builder.process_objs(data, material_lib)
    
    @staticmethod
    def process_objs(data, material_lib=None):
        meshes = []
        vertices = []
        texcoords = []
        normals = []
        faces = []
        materials = []
        material_index_map = {}
        current_material_id = -1
        current_mesh = None


        if material_lib:
            loaded_materials = Builder.load_mtl(material_lib)
            for i, (name, mat) in enumerate(loaded_materials.items()):
                material_index_map[name] = i
                materials.append(mat)

        
        lines = data.split("\n")
        hasNormals = False
        hasTexCoords = False

        for line in lines:
            parts = line.strip().split()
            if not parts or parts[0].startswith('#'):
                continue  

            if parts[0] == 'v':  # Vértices
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vertices.append((x, y, z))

            elif parts[0] == 'vt':  # Coordenadas de textura
                u, v = float(parts[1]), float(parts[2])
                texcoords.append((u, v))
                hasTexCoords = True

            elif parts[0] == 'vn':  # Normais
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                normals.append((nx, ny, nz))
                hasNormals = True

            elif parts[0] == 'f':  # Faces
                face = []
                for vert in parts[1:]:
                    indices = vert.split('/')
                    vertex_index = int(indices[0]) - 1
                    texcoord_index = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None
                    normal_index = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else None
                    face.append((vertex_index, texcoord_index, normal_index))
                
   
                if current_mesh:
                    current_mesh.faces.append(face)

            elif parts[0] == 'usemtl':  # Trocar material
                material_name = parts[1]
                current_material_id = material_index_map.get(material_name, -1)
                

                if current_mesh:
                    meshes.append(current_mesh)


                current_mesh = Mesh(current_material_id)
                current_mesh.faces = []  

            elif parts[0] == 'mtllib':  
                material_lib = parts[1]  


        if current_mesh:
            meshes.append(current_mesh)

        # Processar as faces e adicionar os vértices às malhas correspondentes
        for mesh in meshes:
            for face in mesh.faces:
                indices = []
                for vertex_index, texcoord_index, normal_index in face:
                    x, y, z = vertices[vertex_index]
                    u, v = texcoords[texcoord_index] if texcoord_index is not None else (0.0, 0.0)
                    nx, ny, nz = normals[normal_index] if normal_index is not None else (0.0, 0.0, 0.0)
                    index = mesh.add_vertex(x, y, z, u, v, nx, ny, nz)
                    indices.append(index)

                if len(indices) == 3:
                    mesh.add_triangle(indices[0], indices[1], indices[2])

                elif len(indices) == 4:
                    mesh.add_triangle(indices[0], indices[1], indices[2])
                    mesh.add_triangle(indices[0], indices[2], indices[3])

            if not hasNormals:
                mesh.recalculate_normals(smooth=True, angle_weighted=False)
            if not hasTexCoords:
                mesh.make_planar_mapping(1.0)

            mesh.calculate_bounding_box()

        return meshes, materials  

    @staticmethod
    def create_hill_plane_mesh(tile_size, tile_count, hill_height, hill_count, texture_repeat_count):
        count_hills = hill_count
        if count_hills[0] < 0.01:
            count_hills[0] = 1.0
        if count_hills[1] < 0.01:
            count_hills[1] = 1.0

        center = (
            (tile_size[0] * tile_count[0]) * 0.5,
            (tile_size[1] * tile_count[1]) * 0.5
        )

    
        tx = (
            texture_repeat_count[0] / tile_count[0],
            texture_repeat_count[1] / tile_count[1]
        )

        # Incrementar o tile_count para incluir o ponto extra em cada direção
        tile_count = (tile_count[0] + 1, tile_count[1] + 1)

        mesh = Mesh()

        sx = 0.0
        tsx = 0.0
        for x in range(tile_count[0]):
            sy = 0.0
            tsy = 0.0
            for y in range(tile_count[1]):
                vx = sx - center[0]
                vy = 0.0
                vz = sy - center[1]

                if hill_height != 0.0:
                    vy = math.sin(vx * count_hills[0] * math.pi / center[0]) * \
                        math.cos(vz * count_hills[1] * math.pi / center[1]) * hill_height

                mesh.add_vertex(vx, vy, vz, tsx, 1.0 - tsy, 0, 1, 0)

                sy += tile_size[1]
                tsy += tx[1]

            sx += tile_size[0]
            tsx += tx[0]

        for x in range(tile_count[0] - 1):
            for y in range(tile_count[1] - 1):
                current = x * tile_count[1] + y
                mesh.add_triangle(current, current + 1, current + tile_count[1])
                mesh.add_triangle(current + 1, current + 1 + tile_count[1], current + tile_count[1])

        mesh.recalculate_normals()

        mesh.calculate_bounding_box()

        return mesh
    



    @staticmethod
    def create_terrain_mesh(model,texture_image_path, heightmap_image_path, stretch_size, max_height, max_vtx_block_size, debug_borders=False):
        
        texture_image = Image.open(texture_image_path)
        heightmap = Image.open(heightmap_image_path).convert('L')  # Convert to grayscale for heightmap

        if not texture_image or not heightmap:
            print("Texture or heightmap not found.")
            return None

        #texture_image = texture_image.transpose(Image.FLIP_TOP_BOTTOM)  

        # Definir o tamanho da mesh com base nas dimensões das imagens
        hmap_size = heightmap.size  # (width, height)
        tmap_size = texture_image.size  # (width, height)
        th_rel = (tmap_size[0] / hmap_size[0], tmap_size[1] / hmap_size[1])

        max_height /= 255.0  # O valor de altura vai de 0 a 255

        
        processed_x = 0
        processed_y = 0

        border_skip = 0 if debug_borders else 1
        index =0

        while processed_y < hmap_size[1]:
            while processed_x < hmap_size[0]:
                # Definir o tamanho do bloco de vértices (sub-malha)
                block_size_width = min(max_vtx_block_size[0], hmap_size[0] - processed_x)
                block_size_height = min(max_vtx_block_size[1], hmap_size[1] - processed_y)


                mesh = Mesh(index)  # Novo bloco de terreno
                index += 1

                bs = glm.vec2(1.0/block_size_width, 1.0/block_size_height)
                tc = glm.vec2(0.0,0.5*bs.y)

                # Adicionar vértices ao bloco
                for y in range(block_size_height):
                    tc.x=0.5*bs.x
                    for x in range(block_size_width):
                        # Obter o valor de altura do mapa de alturas
                        height_value = heightmap.getpixel((x + processed_x, y + processed_y)) * max_height

                        vx = (x + processed_x) * stretch_size[0]
                        vy = height_value
                        vz = (y + processed_y) * stretch_size[1]

                        mesh.add_vertex(vx, vy, vz, tc.x,tc.y, 0,1,0)
                        tc.x += bs.x
                    tc.y+=bs.y
                for y in range(block_size_height - 1):
                    for x in range(block_size_width - 1):
                        idx = (y * block_size_width) + x
                        mesh.add_triangle(idx, idx + block_size_width, idx + 1)
                        mesh.add_triangle(idx + 1, idx + block_size_width, idx + block_size_width + 1)

                # Processar a textura para o bloco
                block_texture = texture_image.crop((
                    int(processed_x * th_rel[0]),
                    int(processed_y * th_rel[1]),
                    int((processed_x + block_size_width) * th_rel[0]),
                    int((processed_y + block_size_height) * th_rel[1])
                ))
                texture = Texture2D()
                texture.load_from_image(block_texture)
                model.add_material(Material(texture))


                #block_texture.save(f"block_texture_{processed_x}_{processed_y}_{index}.png")

                
                mesh.calculate_bounding_box()
                mesh.recalculate_normals()
                model.add_mesh(mesh)

                
                processed_x += max_vtx_block_size[0] - border_skip

            processed_x = 0
            processed_y += max_vtx_block_size[1] - border_skip

