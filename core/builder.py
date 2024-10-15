

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
