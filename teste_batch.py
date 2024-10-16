import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.scene import Camera2D
from core.batch import *
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")

Render.load_texture("assets/cube.png")








Render.set_blend(False)
Render.set_depth_test(False)
Render.set_blend_mode(BlendMode.Normal)
Render.set_clear_color(0.0, 0.0, 0.4)
Render.set_clear_mode(True)

camera = Camera2D(720, 480)
lines = LinesBatch(1024)
fill = FillBatch(1024)
sprites = SpriteBatch(1024)

view_mat  = camera.get_view_matrix()
proj_mat =  camera.get_projection_matrix()


Render.set_matrix(VIEW_MATRIX, view_mat)
Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())





rotate =0

while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    camera.set_size(core.width, core.height)
    Render.clear()


    Render.set_matrix(VIEW_MATRIX, view_mat)
    Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())


    #Render.set_scissor_test(True)
    #Render.set_scissor(100,100,200,200)

    #lines.set_clip(100,100,200,200)
    #fill.set_clip(100,100,200,200)
   
   
    lines.line2d(200,100, 100,400)
    lines.circle(300,300, 25,16)
    
    fill.color3f(1.0,0.0,0.0)
    fill.rectangle(50,50,100,100)
    fill.circle(100,100, 25,16)

   
    fill.render()
    lines.render()

    sprites.draw_sprite(Input.get_mouse_x(),Input.get_mouse_y(), width=64, height=64, tu0=0.0, tv0=0.0, tu1=1.0, tv1=1.0)

    sprites.render()

    Render.set_scissor_test(False)

    
   
    core.flip()

core.close() 

