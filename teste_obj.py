import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.scene import Entity,Camera
import sys
import glm
import math    


yaw = -90.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(720, 480, "OpenGL Demo")
render = core.render

render.load_texture("assets/cube.png")

material = TextureMaterial(render.get_texture("cube"))


mesh = load_obj("assets/42.obj", material)
entity = Entity()

plane = create_plane(5,5,5,5, material)


render.set_blend(False)
render.set_depth_test(True)
render.set_blend_mode(BlendMode.Normal)
render.set_clear_color(0.0, 0.0, 0.4)
render.set_clear_mode(True)



camera = Camera(45.0,core.width / core.height)
camera.translate(0.0, 0.5, 15.0)
camera.rotate(0, 0, 0.0)

#view_mat = glm.lookAt(glm.vec3(0.0, 0.5, -5.0), glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 1.0, 0.0))
#proj_mat = glm.perspective(glm.radians(45.0), core.width / core.height, 0.1, 1000.0)
model_mat = glm.mat4(1.0)



render.set_model_matrix(model_mat)

rotate =0




while core.run():
    render.set_viewport(0, 0, core.width, core.height)
    render.clear()


    if core.key_down(glfw.KEY_W):
        entity.move(0, 0, -1)
    if core.key_down(glfw.KEY_S):
        entity.move(0, 0, 1)


    render.set_view_matrix(camera.get_view_matrix())
    render.set_projection_matrix(camera.get_projection_matrix())

   # camera.turn(0, 1, 0)

    model_mat = glm.mat4(1.0)
    #model_mat = entity.get_world_tform().matrix
    render.set_model_matrix(model_mat)
    render.render_mesh(mesh)
    rotate += 1

    model_mat = glm.mat4(1.0)
    render.set_model_matrix(model_mat)
    render.render_mesh(plane)

   


    core.flip()

core.close() 

