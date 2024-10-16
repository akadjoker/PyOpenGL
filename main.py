import core 
from core.core import *
from core.mesh import *
from core.input import Key
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")
render = core.render
input = core.input

render.load_texture("assets/wabbit_alpha.png")

mesh = Mesh(TextureColorMaterial(render.get_texture("wabbit_alpha")))


mesh.vertices = [    -0.5, -0.5, 0.0, 
                      0.5, -0.5, 0.0, 
                      0.5,  0.5, 0.0, 
                     -0.5,  0.5, 0.0 ]

mesh.colors.append(WHITE.data)
mesh.colors.append(WHITE.data)
mesh.colors.append(WHITE.data)
mesh.colors.append(WHITE.data)


mesh.texcoord0 = [0.0, 0.0, 
                  1.0, 0.0, 
                  1.0, 1.0, 
                  0.0, 1.0]

mesh.indices = [0, 1, 2, 2, 3, 0]



mesh.update()

render.set_blend(True)
render.set_blend_mode(BlendMode.Normal)
render.set_clear_color(0.0, 0.0, 0.4)


view_mat = glm.lookAt(glm.vec3(0.0, 0.5, 5.0), glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 1.0, 0.0))
proj_mat = glm.perspective(glm.radians(45.0), core.width / core.height, 0.1, 1000.0)
model_mat = glm.mat4(1.0)

render.set_view_matrix(view_mat)
render.set_projection_matrix(proj_mat)
render.set_model_matrix(model_mat)

while core.run():
    render.set_viewport(0, 0, core.width, core.height)
    render.clear()
    render.render_mesh(mesh)
    core.flip()

    if input.keyboard_check(65):
        print("A")

core.close() 

