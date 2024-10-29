import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.render import *
from core.scene import Entity,Camera,CameraFPS,Scene,LensFlare
from core.batch import *
from core.font import Font
from core.sprite import SpriteBatch
from core.gui import Gui
from core.input import Input
from core.material import *
from core.utils import UtilMath

import sys
import glm
import math   


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(SCREEN_WIDTH, SCREEN_HEIGHT, "OpenGL Simples Shadow")


flaresTexture =Render.load_texture("assets/sprites.png","flares") 

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
sphere = Builder.create_sphere(10, 10)
mesh = Builder.load_obj("assets/room.obj")
mesh.rotate(0,90,0)

Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)

#light =  scene.create_ambient_light(glm.vec3(0.1, 0.1, 0.1))
#scene.create_directional_light(glm.vec3(0.01, 0.01, 0.01), glm.vec3(0.0, -0.8, 0.4))
#scene.create_ambient_light(glm.vec3(0.2, 0.2, 0.2))


#render to depth buffer

buffer = DepthTexture()
buffer.init(1024, 1024)
depthShader = DepthShader()


#normal shader
shader = SingleShadowShader()


#for debug shadow
screenShader = ScreenShader()
quadrender = SingleRender()
quadrender.init()

camera = Camera(45.0,core.width / core.height)
camera.set_perspective(60.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)

scene.set_camera(camera)

floor = scene.create_model()
floor.add_material(Material(Render.get_texture("default")))
floor.add_mesh(plane)
floor.add_mesh(mesh)
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


lensFlare =LensFlare(flaresTexture)

mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)
Render.linesBatch = lines
position = glm.vec3(0.0, 5.0, 0.0)
range = 100.0

lightPos = glm.vec3(-2.0, 4.0, -1.0)
showQuad = False
showGrid = False
while core.run():
    
    Render.clear()

  

    speed =  1

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
    

    Render.set_blend(False)
    Render.set_depth_test(True)
    Render.set_clear_mode(True)


    scene.update()

    

    near_plane = 0.1
    far_plane = 40.5

    size = 20

    lightProjection = glm.ortho(-size, size, -size, size,  near_plane, far_plane)
    lightView = glm.lookAt(lightPos, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
    lightSpaceMatrix = lightProjection * lightView
    
    Render.set_shader(depthShader)

    depthShader.set_matrix4fv("uLightSpaceMatrix", glm.value_ptr(lightSpaceMatrix))
    buffer.begin()
    scene.render(depthShader,False)
    
    buffer.end()

    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()


    Render.set_shader(shader)
    shader.set_vector3f("lightPos", lightPos)
    shader.set_vector3f("viewPos", camera.get_local_position())
    shader.set_matrix4fv("uLightSpaceMatrix", glm.value_ptr(lightSpaceMatrix))
    shader.set_int("diffuseMap", 0)
    shader.set_int("shadowMap", 1)

    # glActiveTexture(GL_TEXTURE0)
    # glBindTexture(GL_TEXTURE_2D, mainTexture.id)
    # glActiveTexture(GL_TEXTURE1)
    # glBindTexture(GL_TEXTURE_2D, buffer.color)
    #Render.set_texture(mainTexture.id,0)
    Render.set_texture(buffer.id,1)
    
    scene.render(shader)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, 0)

    lensFlare.update(scene,lightPos,camera.get_local_position(),camera.get_local_rotation())

  




    pick = False
    




    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_clear_mode(True)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    if showGrid:
        lines.grid(10, 10, True)

    #cube.debug_transform(model.get_world_tform().matrix,lines,True,True,0.5)

    lines.sphere(lightPos.x,lightPos.y,lightPos.z,0.4)
    lines.render() 

    #2d stuff
    Render.set_clear_mode(False)
    Render.set_depth_test(False)
    Render.set_blend(True)
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

        showQuad,_ = Gui.checkbox(5, 160, "Show quad", showQuad)
        showGrid,_ = Gui.checkbox(5, 180, "Show grid", showGrid)

    Gui.end()

    Gui.render(core.width , core.height)



    if showQuad:
        Render.set_shader(screenShader)
        Render.set_texture(buffer.id, 0)
        quadrender.render(0.0,0.0,1.0,1.0)

    Render.set_cull(False)
    Render.set_depth_test(False)
    Render.set_blend(True)
    Render.set_blend_mode(BlendMode.Normal)
    lensFlare.render()


    core.flip()

core.close() 
