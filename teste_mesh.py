import core 
from core.core import *
from core.mesh import *
from core.builder import *
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")


Render.load_texture("assets/cube.png")

material = TextureMaterial(Render.get_texture("cube"))


cube = create_cube(1,material)

plane = create_plane(5,5,5,5, material)
sphere = create_sphere(20,20, material)
cone = create_cone(20,20, material)
torus = create_torus(20,20,0.5,0.8, material)
cylinder = create_cylinder(20,20,0.2, 1, material)




Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)
Render.set_clear_color(0.0, 0.0, 0.4)
Render.set_clear_mode(True)



view_mat = glm.lookAt(glm.vec3(0.0, 0.5, -15.0), glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 1.0, 0.0))
proj_mat = glm.perspective(glm.radians(45.0), core.width / core.height, 0.1, 1000.0)
model_mat = glm.mat4(1.0)

Render.set_matrix(VIEW_MATRIX, view_mat)
Render.set_matrix(PROJECTION_MATRIX, proj_mat)

Render.set_matrix(MODEL_MATRIX, model_mat)

rotate =0


def mouse_callback(xpos, ypos):
    print(xpos, ypos) 
def key_callback(key, scancode, action, mods):
    print(key, scancode, action, mods)

core.OnKeyPress = key_callback
core.OnMouseMove = mouse_callback


while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()

    model_mat = glm.mat4(1.0)
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(cube)
    rotate += 1

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.0, -0.5, 0.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(plane)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(5.0, 0.5, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(sphere)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(-5.0, 0.5, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(cone)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.5, 0.5, 2.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(torus)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(-1.2, 0.5, 2.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    Render.set_matrix(MODEL_MATRIX, model_mat)
    Render.render_mesh(cylinder)

    core.flip()

core.close() 

