import core 
from core.core import *
from core.mesh import *
from core.builder import *
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")
render = core.render

render.load_texture("assets/cube.png")

material = TextureMaterial(render.get_texture("cube"))


cube = create_cube(1,material)

plane = create_plane(5,5,5,5, material)
sphere = create_sphere(20,20, material)
cone = create_cone(20,20, material)
torus = create_torus(20,20,0.5,0.8, material)





render.set_blend(False)
render.set_depth_test(True)
render.set_blend_mode(BlendMode.Normal)
render.set_clear_color(0.0, 0.0, 0.4)
render.set_clear_mode(True)



view_mat = glm.lookAt(glm.vec3(0.0, 0.5, -15.0), glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 1.0, 0.0))
proj_mat = glm.perspective(glm.radians(45.0), core.width / core.height, 0.1, 1000.0)
model_mat = glm.mat4(1.0)

render.set_view_matrix(view_mat)
render.set_projection_matrix(proj_mat)
render.set_model_matrix(model_mat)

rotate =0

while core.run():
    render.set_viewport(0, 0, core.width, core.height)
    render.clear()

    model_mat = glm.mat4(1.0)
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    render.set_model_matrix(model_mat)
    render.render_mesh(cube)
    rotate += 1

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.0, -0.5, 0.0))
    render.set_model_matrix(model_mat)
    render.render_mesh(plane)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(5.0, 0.5, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    render.set_model_matrix(model_mat)
    render.render_mesh(sphere)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(-5.0, 0.5, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    render.set_model_matrix(model_mat)
    render.render_mesh(cone)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.5, 0.5, 2.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
    render.set_model_matrix(model_mat)
    render.render_mesh(torus)

    core.flip()

core.close() 

