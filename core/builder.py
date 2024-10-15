
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

    mesh.calcula_normals()
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


    mesh.calcula_normals()
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


    mesh.calcula_normals()  
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

    mesh.calcula_normals()
    mesh.update()

    return mesh