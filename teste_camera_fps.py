import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.render import *
from core.scene import Entity,Camera,CameraFPS
from core.input import Input
import sys
import glm
import math    


yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(720, 480, "OpenGL Demo")


Render.load_texture("assets/cube.png")

material = TextureMaterial(Render.get_texture("cube"))


mesh = load_obj("assets/42.obj", material)
entity = Entity()

plane = create_plane(5,5,5,5, material)


Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)
Render.set_clear_color(0.0, 0.0, 0.4)
Render.set_clear_mode(True)



camera = CameraFPS(45.0,core.width / core.height)
camera.translate(0.0, 0.5, 15.0)
camera.rotate(pitch, yaw, 0.0)

model_mat = glm.mat4(1.0)





rotate =0
mouseSensitivity = 90



while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()
    speed = core.get_delta_time() * 1

    if Input.mouse_down(0):
        yaw   += Input.get_mouse_delta_x()  *  mouseSensitivity
        pitch -= Input.get_mouse_delta_y()  *  mouseSensitivity
        pitch = max(-89.0, min(89.0, pitch))
        camera.rotate(pitch, yaw, 0.0)






    if Input.keyboard_down(glfw.KEY_W):
        camera.move_forward(speed)
    if Input.keyboard_down(glfw.KEY_S):
        camera.move_backward(speed)

    if Input.keyboard_down(glfw.KEY_A):
        camera.strafe_left(speed)
    if Input.keyboard_down(glfw.KEY_D):
        camera.strafe_right(speed)
    

    camera.update()



    Render.set_matrix(VIEW_MATRIX,camera.get_view_matrix())
    Render.set_matrix(PROJECTION_MATRIX,camera.get_projection_matrix())

    #camera.turn(0, 0.1, 0)

    model_mat = glm.mat4(1.0)
    model_mat = entity.get_world_tform().matrix
    Render.set_matrix(MODEL_MATRIX,model_mat)
    Render.render_mesh(mesh)
    rotate += 1

    model_mat = glm.mat4(1.0)
    Render.set_matrix(MODEL_MATRIX,model_mat)
    Render.render_mesh(plane)

   


    core.flip()

core.close() 

