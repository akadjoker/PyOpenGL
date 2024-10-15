
import math
import numpy as np
from .shader import Shader
from .texture import Texture
from .mesh import Mesh
from .color import *
from .core import *


def create_cube(size,material):
    mesh = Mesh(material)

    mesh.add_vertex_textured(0, 0, 0, 0.0, 1.0)
    mesh.add_vertex_textured(1, 0, 0, 1.0, 1.0)
    mesh.add_vertex_textured(1, 1, 0, 1.0, 0.0)
    mesh.add_vertex_textured(0, 1, 0, 0.0, 0.0)
    mesh.add_vertex_textured(1, 0, 1, 0.0, 1.0)
    mesh.add_vertex_textured(1, 1, 1, 0.0, 0.0)
    mesh.add_vertex_textured(0, 1, 1, 1.0, 0.0)
    mesh.add_vertex_textured(0, 0, 1, 1.0, 1.0)
    mesh.add_vertex_textured(0, 1, 1, 0.0, 1.0)
    mesh.add_vertex_textured(0, 1, 0, 1.0, 1.0)
    mesh.add_vertex_textured(1, 0, 1, 1.0, 0.0)
    mesh.add_vertex_textured(1, 0, 0, 0.0, 0.0)


    mesh.indices=[ 0,2,1,   0,3,2,   
                    1,5,4,   1,2,5,   
                    4,6,7,   4,5,6,        
                    7,3,0,   7,6,3,   
                    9,5,2,   9,8,5,   
                    0,11,10,   0,10,7]
    
    for i in range(12):
        pos = mesh.get_position(i)
        pos.x -= 0.5
        pos.y -= 0.5
        pos.z -= 0.5
        mesh.set_position(i, pos.x * size, pos.y  * size, pos.z  * size)

    mesh.calcula_smoth_normals()
    mesh.update()

    return mesh

def create_plane(stacks, slices, tilesX, tilesY, material):

    mesh = Mesh(material)
    min_point = glm.vec3(float('inf'), 0, float('inf'))
    max_point = glm.vec3(float('-inf'), 0, float('-inf'))

    for i in range(stacks + 1):  
        y = i / stacks * tilesY
        for j in range(slices + 1): 
            x = j / slices * tilesX
            mesh.add_vertex_textured(x, 0, y, x, y)
            mesh.add_normal(0, 1, 0)


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

    mesh.update()
    return mesh


def create_sphere(stacks, slices, material):
    mesh = Mesh(material)
    pi = 3.14159265359

    for i in range(stacks + 1): 
        phi = i * pi / stacks
        for j in range(slices + 1):  
            theta = j * 2.0 * pi / slices
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            u = j / slices  #  U
            v = i / stacks  # C V
            mesh.add_vertex_textured(x, y, z, u, v)


    for i in range(stacks):
        for j in range(slices):
            index = (slices + 1) * i + j
            mesh.add_triangle(index, index + slices + 1, index + slices + 2) 
            mesh.add_triangle(index, index + slices + 2, index + 1)          


    mesh.calcula_smoth_normals()
    mesh.update()

    return mesh



def create_cone(stacks, slices, material):
    mesh = Mesh(material)
    pi = math.pi
    stack_height = 1.0 / stacks
    slice_angle = 2.0 * pi / slices


 
    for i in range(stacks + 1):
        y = -0.5 + i * stack_height
        radius = 0.5 - y  # Raio diminui à medida que subimos o cone
        for j in range(slices + 1):
            x = radius * math.cos(j * slice_angle)
            z = radius * math.sin(j * slice_angle)
            mesh.add_vertex_textured(x, y, z, j / slices, i / stacks)
            mesh.box.add_point(x, y, z)

    #  o corpo do cone
    for i in range(stacks):
        for j in range(slices):
            index = (slices + 1) * i + j
            mesh.add_triangle(index, index + slices + 1, index + slices + 2)
            mesh.add_triangle(index, index + slices + 2, index + 1)

    # Criar a base do cone (círculo na parte inferior)
    base_start_index = mesh.get_total_vertices()
    y_bottom = -0.5
    mesh.add_vertex_textured(0.0, y_bottom, 0.0, 0.5, 0.5)  #  central da base

    for i in range(slices + 1):
        x = math.cos(i * slice_angle)
        z = math.sin(i * slice_angle)
        mesh.add_vertex_textured(x, y_bottom, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0))
        mesh.box.add_point(x, y_bottom, z)

    #  base do cone
    for i in range(slices):
        mesh.add_triangle(base_start_index, base_start_index + i + 1, base_start_index + (i + 1) % slices + 1)


    mesh.calcula_smoth_normals()  
    mesh.update()

    return mesh



def create_torus(stacks, slices, inner_radius, outer_radius, material):
    mesh = Mesh(material)
    pi = math.pi
    stack_angle = 2.0 * pi / stacks
    slice_angle = 2.0 * pi / slices
 

    # Gerar vértices para o toro
    for i in range(stacks + 1):
        u = i * stack_angle
        for j in range(slices + 1):
            v = j * slice_angle
            x = (outer_radius + inner_radius * math.cos(v)) * math.cos(u)
            y = (outer_radius + inner_radius * math.cos(v)) * math.sin(u)
            z = inner_radius * math.sin(v)
            texture_u = i / stacks
            texture_v = j / slices
            mesh.box.add_point(x, y, z)
            mesh.add_vertex_textured(x, y, z, texture_u, texture_v)

    # Gerar triângulos para o toro
    for i in range(stacks):
        for j in range(slices):
            index = (slices + 1) * i + j
            mesh.add_triangle(index, index + slices + 1, index + slices + 2)
            mesh.add_triangle(index, index + slices + 2, index + 1)

    mesh.calcula_smoth_normals()
    mesh.update()

    return mesh


def create_cylinder(stacks, slices, radius, height, material):
    mesh = Mesh(material)
    pi = math.pi
    stack_height = height / stacks
    slice_angle = 2.0 * pi / slices


    # corpo do cilindro
    for i in range(stacks + 1):
        y = -height / 2.0 + i * stack_height
        for j in range(slices + 1):
            x = radius * math.cos(j * slice_angle)
            z = radius * math.sin(j * slice_angle)
            mesh.add_vertex_textured(x, y, z, j / slices, i / stacks)
            mesh.box.add_point(x, y, z)

    # Gerar triângulos para o corpo
    for i in range(stacks):
        for j in range(slices):
            index = (slices + 1) * i + j
            mesh.add_triangle(index, index + slices + 1, index + slices + 2)
            mesh.add_triangle(index, index + slices + 2, index + 1)

    # Criar base e topo do cilindro
    base_start_index = mesh.get_total_vertices()
    y_bottom = -height / 2.0
    y_top = height / 2.0

    # Base inferior
    mesh.add_vertex_textured(0.0, y_bottom, 0.0, 0.5, 0.5)  # Centro da base
    for j in range(slices + 1):
        x = radius * math.cos(j * slice_angle)
        z = radius * math.sin(j * slice_angle)
        mesh.add_vertex_textured(x, y_bottom, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0))
        mesh.box.add_point(x, y_bottom, z)

    # Triângulos para a base inferior
    for j in range(slices):
        mesh.add_triangle(base_start_index, base_start_index + j + 1, base_start_index + (j + 1) % slices + 1)

    # Base superior
    top_start_index = mesh.get_total_vertices()
    mesh.add_vertex_textured(0.0, y_top, 0.0, 0.5, 0.5)  # Centro do topo
    for j in range(slices + 1):
        x = radius * math.cos(j * slice_angle)
        z = radius * math.sin(j * slice_angle)
        mesh.add_vertex_textured(x, y_top, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0))
        mesh.box.add_point(x, y_top, z)

    # Triângulos para a base superior
    for j in range(slices):
        mesh.add_triangle(top_start_index, top_start_index + (j + 1) % slices + 1, top_start_index + j + 1)


    mesh.calcula_smoth_normals()
    mesh.update()

    return mesh



def create_pyramid(sides, height, material):
    mesh = Mesh(material)
    pi = math.pi
    slice_angle = 2.0 * pi / sides
  


    base_y = -height / 2.0
    mesh.add_vertex_textured(0.0, base_y, 0.0, 0.5, 0.5)  # Centro da base
    for i in range(sides + 1):
        x = math.cos(i * slice_angle)
        z = math.sin(i * slice_angle)
        mesh.add_vertex_textured(x, base_y, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0))
        mesh.box.add_point(x, base_y, z)


    top_y = height / 2.0
    mesh.add_vertex_textured(0.0, top_y, 0.0, 0.5, 0.5) 
    mesh.box.add_point(0.0, top_y, 0.0) 


    top_index = mesh.get_total_vertices() - 1
    for i in range(sides):
        mesh.add_triangle(top_index, i + 1, (i + 2) % (sides + 1))


    for i in range(sides):
        mesh.add_triangle(0, (i + 2) % (sides + 1), i + 1)


    mesh.calcula_smoth_normals()

    mesh.update()

    return mesh


def create_spherical_plane(stacks, slices, radius, material):
    mesh = Mesh(material)
    pi = math.pi
    


    for i in range(stacks + 1):
        phi = i * pi / stacks / 2  # Apenas uma seção da esfera
        for j in range(slices + 1):
            theta = j * 2.0 * pi / slices
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)
            u = j / slices
            v = i / stacks
            mesh.add_vertex_textured(x, y, z, u, v)
            mesh.box.add_point(x, y, z)

    
    for i in range(stacks):
        for j in range(slices):
            index = (slices + 1) * i + j
            mesh.add_triangle(index, index + slices + 1, index + slices + 2)
            mesh.add_triangle(index, index + slices + 2, index + 1)
    mesh.calcula_smoth_normals()
    mesh.update()

    return mesh


def create_disc(slices, radius, material):
    mesh = Mesh(material)
    pi = math.pi
    slice_angle = 2.0 * pi / slices
  
    mesh.add_vertex_textured(0.0, 0.0, 0.0, 0.5, 0.5)


    for i in range(slices + 1):
        x = radius * math.cos(i * slice_angle)
        z = radius * math.sin(i * slice_angle)
        mesh.add_vertex_textured(x, 0.0, z, 0.5 * (x + 1.0), 0.5 * (z + 1.0))


    for i in range(slices):
        mesh.add_triangle(0, i + 1, (i + 2) % (slices + 1))

    mesh.calcula_smoth_normals()
    mesh.calculate_bounding_box()
    mesh.update()

    return mesh


def load_obj(file_path, material):
    with open(file_path, 'r') as file:
        data = file.read()

    return process_obj(data, material)

def process_obj(data, material):
    mesh = Mesh(material)

    
    lines = data.split("\n")
    vertices = []
    normals = []
    texcoords = []

 
    def add_triangle(vertices, normals, texcoords, a, b, c):
        data_a = a.split("/")
        data_b = b.split("/")
        data_c = c.split("/")

        vert_id_a = int(data_a[0]) - 1
        vert_id_b = int(data_b[0]) - 1
        vert_id_c = int(data_c[0]) - 1

        has_normals = len(normals) > 0
        has_texcoords = len(texcoords) > 0

        v_a = vertices[vert_id_a]
        v_b = vertices[vert_id_b]
        v_c = vertices[vert_id_c]

        n_a = glm.vec3(0, 0, 0)
        n_b = glm.vec3(0, 0, 0)
        n_c = glm.vec3(0, 0, 0)

        uv_a = glm.vec2(0, 0)
        uv_b = glm.vec2(0, 0)
        uv_c = glm.vec2(0, 0)

        if has_normals:
            norm_id_a = int(data_a[2]) - 1
            norm_id_b = int(data_b[2]) - 1
            norm_id_c = int(data_c[2]) - 1
            n_a = normals[norm_id_a]
            n_b = normals[norm_id_b]
            n_c = normals[norm_id_c]

        if has_texcoords:
            tex_id_a = int(data_a[1]) - 1
            tex_id_b = int(data_b[1]) - 1
            tex_id_c = int(data_c[1]) - 1
            uv_a = texcoords[tex_id_a]
            uv_b = texcoords[tex_id_b]
            uv_c = texcoords[tex_id_c]

        index_a = mesh.add_vertex_textured(v_a.x, v_a.y, v_a.z, uv_a.x, uv_a.y)
        index_b = mesh.add_vertex_textured(v_b.x, v_b.y, v_b.z, uv_b.x, uv_b.y)
        index_c = mesh.add_vertex_textured(v_c.x, v_c.y, v_c.z, uv_c.x, uv_c.y)

        mesh.add_triangle(index_a, index_b, index_c)
    has_normals = False
    has_texcoords = False
    for line in lines:
        line = line.strip()
        tokens = line.split()

        if len(tokens) == 0:
            continue

        if tokens[0] == "v":  # Vertex position
            x = float(tokens[1])
            y = float(tokens[2])
            z = float(tokens[3])
            vertices.append(glm.vec3(x, y, z))
    
        elif tokens[0] == "vn":  # Vertex normal
            x = float(tokens[1])
            y = float(tokens[2])
            z = float(tokens[3])
            has_normals = True
            normals.append(glm.vec3(x, y, z))


        elif tokens[0] == "vt":  # Vertex texture coordinate
            u = float(tokens[1])
            v = float(tokens[2])
            has_texcoords = True
            texcoords.append(glm.vec2(u, v))


        elif tokens[0] == "f":  # Face (triangles or quads)
            if len(tokens) == 4:  # Triangle
                add_triangle(vertices, normals, texcoords, tokens[1], tokens[2], tokens[3])
            elif len(tokens) == 5:  # Quad (split into two triangles)
                add_triangle(vertices, normals, texcoords, tokens[1], tokens[2], tokens[3])
                add_triangle(vertices, normals, texcoords, tokens[1], tokens[3], tokens[4])

    if not has_normals: 
        mesh.calcula_smoth_normals()
    if not has_texcoords:
        mesh.make_planar_mapping(0.5)
    
    mesh.remove_duplicate_vertices()
    mesh.update()

    return mesh