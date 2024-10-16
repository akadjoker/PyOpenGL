import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.scene import Entity,Camera,CameraFPS
import sys
import glm
import math    


yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(720, 480, "OpenGL Demo")
render = core.render
input = core.input

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



camera = CameraFPS(45.0,core.width / core.height)
camera.translate(0.0, 0.5, 15.0)
camera.rotate(pitch, yaw, 0.0)

model_mat = glm.mat4(1.0)



render.set_model_matrix(model_mat)

rotate =0
mouseSensitivity = 90



while core.run():
    render.set_viewport(0, 0, core.width, core.height)
    render.clear()
    speed = core.get_delta_time() * 1

    if input.mouse_down(0):
        yaw   += input.get_mouse_delta_x()  *  mouseSensitivity
        pitch -= input.get_mouse_delta_y()  *  mouseSensitivity
        pitch = max(-89.0, min(89.0, pitch))
        camera.rotate(pitch, yaw, 0.0)






    if input.keyboard_down(glfw.KEY_W):
        camera.move_forward(speed)
    if input.keyboard_down(glfw.KEY_S):
        camera.move_backward(speed)

    if input.keyboard_down(glfw.KEY_A):
        camera.strafe_left(speed)
    if input.keyboard_down(glfw.KEY_D):
        camera.strafe_right(speed)
    

    camera.update()



    render.set_view_matrix(camera.get_view_matrix())
    render.set_projection_matrix(camera.get_projection_matrix())

    #camera.turn(0, 0.1, 0)

    model_mat = glm.mat4(1.0)
    model_mat = entity.get_world_tform().matrix
    render.set_model_matrix(model_mat)
    render.render_mesh(mesh)
    rotate += 1

    model_mat = glm.mat4(1.0)
    render.set_model_matrix(model_mat)
    render.render_mesh(plane)

   


    core.flip()

core.close() 

