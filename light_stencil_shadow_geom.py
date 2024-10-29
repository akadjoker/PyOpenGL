import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.render import *
from core.scene import Entity,Camera,CameraFPS,Scene
from core.batch import *
from core.font import Font
from core.sprite import SpriteBatch
from core.gui import Gui
from core.input import Input
from core.material import *

import sys
import glm
import math   



def startStencil():
    glEnable(GL_STENCIL_TEST)
    glClearStencil(Render.StencilValue)
    glClear(GL_STENCIL_BUFFER_BIT)
    glDepthMask(GL_FALSE)
    glColorMask( GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE )
    glEnable( GL_CULL_FACE )

def endStencil():
    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
    glDepthMask(GL_TRUE)
    glStencilOp( GL_KEEP, GL_KEEP, GL_KEEP )
    glDisable(GL_STENCIL_TEST)
    

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(SCREEN_WIDTH, SCREEN_HEIGHT, "OpenGL Simples Shadow")


mainTexture =Render.load_texture("assets/brickwall_diffuse.jpg","brickwall")
#Render.load_texture("assets/brickwall_specular.jpg","brickwall_specular")

mainTexture = Render.load_texture("assets/defaultTexture.png","default")
#Render.load_texture("assets/defaultTexture_specular.png","default_specular")





scene = Scene()


tile_size = (5.0, 5.0)
tile_count = (10, 10)
hill_height = 1.0
hill_count = (1.0, 1.0)
texture_repeat_count = (4.0, 4.0)
plane = Builder.create_hill_plane_mesh(tile_size, tile_count, hill_height, hill_count, texture_repeat_count)

#plane = create_plane(5,5,5,5)
cube = Builder.create_cube()
room = Builder.load_obj("assets/room.obj")
room.rotate(0,90,0)

Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)

#light =  scene.create_ambient_light(glm.vec3(0.1, 0.1, 0.1))
#scene.create_directional_light(glm.vec3(0.01, 0.01, 0.01), glm.vec3(0.0, -0.8, 0.4))
#scene.create_ambient_light(glm.vec3(0.2, 0.2, 0.2))


#render to depth buffer




depthShader = VolumeDepthShader()


#normal shader
shader = SunShader()


#for stancil
stencilShader = StencilShader()
quadrender = FullScreenQuad()



camera = Camera(45.0,core.width / core.height)
camera.set_perspective(45.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)

scene.set_camera(camera)

floor = scene.create_model()
floor.add_material(Material(Render.get_texture("default")))
floor.add_mesh(plane)
floor.add_mesh(room)
#model.scale(20.0, 1.0, 20.0)

# terrain = scene.create_terrain_block(shader,"assets/terrain-texture.jpg","assets/terrain-heightmap.png", 
#     stretch_size=(1.0, 1.0),  # tamanho do terreno
#     max_height=6.0,  # máxima do terreno
#     max_vtx_block_size=(64, 64),  #  máximo dos blocos
#     debug_borders=False)


model = scene.create_model()
model.add_material(Material(Render.get_texture("brickwall")))
model.add_mesh(cube)
model.translate(0.0, 1.0, 0.0)


mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)
position = glm.vec3(0.0, 5.0, 0.0)
range = 100.0

lightPos = glm.vec3(-2.0, 4.0, 2.0)
showQuad = False
showGrid = False

volumes = []
volume = cube.create_shadow_volume(lightPos)
volumes.append(volume)
#volumes.append(room)


while core.run():
    
    Render.clear()

  

    speed = 1

    if Input.mouse_down(0) and not Gui.has_focus():
        yaw   += Input.get_mouse_delta_x()  *  mouseSensitivity
        pitch -= Input.get_mouse_delta_y()  *  mouseSensitivity
        pitch = max(-89.0, min(89.0, pitch))
        camera.rotate(pitch, yaw, 0.0)




    if Input.keyboard_down(glfw.KEY_W):
        camera.move(0, 0, -speed)
    if Input.keyboard_down(glfw.KEY_S):
        camera.move(0, 0, speed)

    if Input.keyboard_down(glfw.KEY_A):
        camera.move(-speed,0,0)
    if Input.keyboard_down(glfw.KEY_D):
        camera.move(speed,0,0)


    #
    model.turn(0,1,0)
    


    scene.update()

    near_plane = 0.1
    far_plane = 40.5

    size = 20

  

    # volumes=[]
    # volume = cube.create_shadow_volume(lightPos)
    # volumes.append(volume)
    # volume = room.create_shadow_volume(lightPos)
    # volumes.append(volume)



    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()



    Render.set_blend(False)
    Render.set_depth_test(True)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_clear_mode(True)

    Render.set_shader(shader)
    shader.set_vector3f("lightPos", lightPos)
    scene.render(shader)

    Render.set_matrix(VIEW_MATRIX, camera.get_view_matrix())
    Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())
      



    Render.set_shader(depthShader)
    #depthShader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    #depthShader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
    depthShader.set_vector3f("lightPos", lightPos)



  
  
    midStencilVal = Render.StencilValue
    glEnable( GL_CULL_FACE )
    glEnable(GL_STENCIL_TEST)
    glClearStencil(midStencilVal)
    glClear(GL_STENCIL_BUFFER_BIT)
    glDepthMask(GL_FALSE)
    glColorMask( GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE )


    glStencilFunc( GL_ALWAYS, 0, 0xff)
    glStencilOp( GL_KEEP, GL_INCR_WRAP, GL_KEEP ) 
    glCullFace( GL_BACK   )
    scene.render_reometry(depthShader)

    glStencilOp( GL_KEEP, GL_DECR_WRAP, GL_KEEP ) 
    glCullFace(GL_FRONT)
    scene.render_reometry(depthShader)
   


    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
    glDepthMask(GL_TRUE)
    glStencilOp( GL_KEEP, GL_KEEP, GL_KEEP )

    glCullFace(GL_BACK)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glStencilFunc(GL_NOTEQUAL, midStencilVal, 0xffffff)
    Render.set_shader(stencilShader)
    quadrender.render()
    glDisable(GL_STENCIL_TEST)
    glClear(GL_STENCIL_BUFFER_BIT)
    glCullFace(GL_BACK)
    glEnable(GL_BLEND)
    glDisable(GL_CULL_FACE )




    # pick = False
    




    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    if showGrid:
        lines.grid(10, 10, True)

    lines.sphere(lightPos.x,lightPos.y,lightPos.z,0.4)

    # for volume in volumes:
    #     volume.debug(lines,False,True,RED)

    lines.render() 

    #2d stuff
    #Render.set_clear_mode(False)
    Render.set_blend_mode(BlendMode.Normal)




    Gui.begin(0,10, core.height-80, 260, 80, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()



    Gui.begin(1, 10,20, 300, 250, options={"background": True,'dragging': True, "bar": True, "title": "Light"})
    if Gui.is_window_visible(1):            
        Gui.label(120, 5, "Light position")

        lightPos.x = Gui.slider(5, 20, 80,20, -10.0, 10.0,  lightPos.x)
        lightPos.y = Gui.slider(5, 40, 80,20, -10.0, 10.0,  lightPos.y)
        lightPos.z = Gui.slider(5, 80, 80,20, -10.0, 10.0,  lightPos.z)
        


        Gui.label(120, 115, "Light ambient")

        # light.ambient.r = Gui.slider(5, 125, 80,20, 0, 1.0,  light.ambient.r)
        # light.ambient.g = light.ambient.r
        # light.ambient.b = light.ambient.r


        showGrid,_ = Gui.checkbox(5, 180, "Show grid", showGrid)
        showQuad,_ = Gui.checkbox(5, 200, "Show quad", showQuad)

    Gui.end()

    Gui.render(core.width , core.height)



    Render.set_cull(True)
    Render.set_cull_mode(CullMode.Back)
    Render.set_depth_test(True)



    core.flip()

core.close() 

