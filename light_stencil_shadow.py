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
plane = Builder.create_plane(50,50)

#plane = create_plane(5,5,5,5)
cube = Builder.create_cube()
room =Builder.create_cube()
# # Builder.load_obj("assets/room.obj")
#room.rotate(0,90,0)

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

model2 = scene.create_model()
model2.add_material(Material(Render.get_texture("brickwall")))
model2.add_mesh(room)
model2.translate(0.0, 0.0, 0.0)
model2.scale(20.0, 0.1, 20.0)


mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)
position = glm.vec3(0.0, 5.0, 0.0)
range = 100.0

lightPos = glm.vec3(-2.0, 4.0, 2.0)
showQuad = False
showGrid = False

volumes =[]
volumes.append(MeshVolume(cube))

glEnable(GL_DEPTH_TEST)
glEnable(GL_STENCIL_TEST)
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

  

    

    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()


  


    glEnable(GL_CULL_FACE)
    if showGrid:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
   
    Render.set_shader(shader)
    shader.set_vector3f("lightPos", lightPos)
    scene.render(shader)

    for volume in volumes:
        volume.compute_volume(lightPos, thickness=50.0)
        #volume.set_model_matrix(model.get_matrix())


    Render.set_shader(depthShader)
    depthShader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    depthShader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
    if showQuad:
        for volume in volumes:
            volume.render()

  

    
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    midStencilVal =5#Render.StencilValue
    glClearStencil(0)
    glClear(GL_STENCIL_BUFFER_BIT)
    
    # Configurar stencil test
    glEnable(GL_STENCIL_TEST)
    glDepthMask(GL_FALSE)  # Desabilitar escrita no depth buffer
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)  # Desabilitar escrita no color buffer
    
    # Garantir que o depth test está habilitado e configurado corretamente
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    # Primeira passagem - faces traseiras
    glCullFace(GL_FRONT)
    glStencilFunc(GL_ALWAYS, 0, ~0)
    glStencilOp(GL_KEEP, GL_INCR_WRAP, GL_KEEP)  # Incrementar no depth fail
    
    for volume in volumes:
        volume.render()
    
    # Segunda passagem - faces frontais
    glCullFace(GL_BACK)
    glStencilOp(GL_KEEP, GL_DECR_WRAP, GL_KEEP)  # Decrementar no depth fail
    
    for volume in volumes:
        volume.render()
    
    # Configurar para renderizar o quad das sombras
    glDepthMask(GL_TRUE)  # Reabilitar escrita no depth buffer
    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)  # Reabilitar escrita no color buffer
    glStencilFunc(GL_NOTEQUAL, 0, ~0)  # Renderizar onde stencil != 0
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    
    # Configurar blending para as sombras
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Render the final shadowed quad
    Render.set_shader(stencilShader)
    quadrender.render()
    
    # Restore previous state

    glDisable(GL_STENCIL_TEST)
    glClear(GL_STENCIL_BUFFER_BIT)

    glDisable(GL_DEPTH_TEST)




    # pick = False
    




    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(100.0))
    # if showGrid:
    #     lines.grid(10, 10, True)

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
        showQuad,_ = Gui.checkbox(5, 200, "Show volume", showQuad)

    Gui.end()

    Gui.render(core.width , core.height)



    Render.set_cull(True)
    Render.set_cull_mode(CullMode.Back)
    Render.set_depth_test(True)



    core.flip()

core.close() 
