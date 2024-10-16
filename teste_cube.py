import core 
from core.core import *
from core.mesh import *
from core.builder import *
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")

Render.load_texture("assets/cube.png")

mesh = create_cube(1,TextureMaterial(Render.get_texture("cube")))










mesh.update()


Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)
Render.set_clear_color(0.0, 0.0, 0.4)
Render.set_clear_mode(True)



view_mat = glm.lookAt(glm.vec3(0.0, 0.5, -5.0), glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 1.0, 0.0))
proj_mat = glm.perspective(glm.radians(45.0), core.width / core.height, 0.1, 1000.0)
model_mat = glm.mat4(1.0)

Render.set_view_matrix(view_mat)
Render.set_projection_matrix(proj_mat)
Render.set_model_matrix(model_mat)

rotate =0

while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()

    model_mat = glm.rotate(model_mat, glm.radians(1), glm.vec3(1.0, 0.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(1), glm.vec3(0.0, 1.0, 0.0))
    model_mat = glm.rotate(model_mat, glm.radians(1), glm.vec3(0.0, 0.0, 1.0))
    


    Render.set_model_matrix(model_mat)
    Render.render_mesh(mesh)
    core.flip()

core.close() 

