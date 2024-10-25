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


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(SCREEN_WIDTH, SCREEN_HEIGHT, "OpenGL Demo")


diffuse = Render.load_texture("assets/brickwall_diffuse.jpg","brickwall")
normal = Render.load_texture("assets/brickwall_normal.jpg","brickwall_normal")







scene = Scene()


buffer = DepthTexture()
buffer.init(2048, 2048)
depthShader = DepthShader()


#scene shader
shader = DirectionalPbrShadowShader()


#for debug shadow
screenShader = ScreenShader()
quadrender = SingleRender()
quadrender.init()
# mesh = Builder.load_obj("assets/crypt/crypt.obj")
# mesh.calculate_tangents()
# mesh.set_attributes(shader.attributes)
cone = Builder.create_cone(10, 10)
cone.calculate_tangents()
cone.set_attributes(shader.attributes)





Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)




camera = Camera(45.0,core.width / core.height)
camera.set_perspective(45.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)

scene.set_camera(camera)



mesh42 = Builder.load_obj("assets/42.obj")
mesh42.recalculate_normals()
mesh42.make_planar_mapping(1)
mesh42.calculate_tangents()
mesh42.set_attributes(shader.attributes)

model42 = scene.create_model()
model42.add_material(Material(diffuse, normal))
model42.add_mesh(mesh42)
model42.translate(0.4, 2.0, 0.0)
model42.rotate(0,-90,0)


lightModel = scene.create_model()
lightModel.add_material(Material(Render.defaultTexture,Render.defaultTexture))
lightModel.add_mesh(cone)
lightModel.materials[0].castShadow = False
lightModel.translate(0.0, 9.0, 14.0)


mouseSensitivity = 90

bigMehs = scene.create_model()
Builder.load_static_model(bigMehs,shader.attributes, "assets/models/scene.h3d", "assets/models/Textures/")
bigMehs.rotate(0.0, 90.0, 90.0)

Gui.init()
lines = LinesBatch(1024*8)
direction = glm.vec3(0.0, -1.0, 0.0)

light_yaw = 0.0    # Rotação ao redor do eixo Y (esquerda-direita)
light_pitch = 30.0 # Rotação ao redor do eixo X (cima-baixo)
light_roll = 0.0   # Rotação ao redor do eixo Z (inclinação)


light_color = glm.vec3(1.0, 1.0, 1.0)
light_direction = glm.vec3(0.0, -1.0, 0.0)

normalStrength = 0
metal = 0.0
roughness = 0.0
lightIntensity = 2.5
lightPos = glm.vec3(-2.0, 4.0, -1.0)
showGrid = False
showQuad = False
isPressed = False

while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()

    model42.turn(0,1,0)

    speed = core.get_delta_time() * 125



  
    Gui.begin(1, 10,40, 300, 270, options={"background": True,'dragging': True, "bar": True, "title": "Light"})
    
    # Gui.label(120, 15, "Light Shininess")
    # light.shininess = Gui.slider(5, 5, 80,20, 0, 256,  light.shininess)

    Gui.label(120, 55, "Light X: " + str(lightPos.x))
    Gui.label(120, 75, "Light Y: " + str(lightPos.y))
    Gui.label(120, 95, "Light Z: " + str(lightPos.z))

    lightPos.x = Gui.slider(5, 20, 80,20, -10.0, 10.0,  lightPos.x)
    lightPos.y = Gui.slider(5, 40, 80,20, -10.0, 10.0,  lightPos.y)
    lightPos.z = Gui.slider(5, 80, 80,20, -10.0, 10.0,  lightPos.z)
        


    # light_pitch = Gui.slider(5, 45, 80,20, -360, 360,  light_pitch)
    # light_yaw = Gui.slider(5, 65, 80,20, -360, 360, light_yaw)
    # light_roll = Gui.slider(5, 85, 80,20, -360, 360,  light_roll)
    

    # Gui.label(120, 115, "Light specular")

    # light.specular.r = Gui.slider(5, 105, 80,20, 0, 1.0,  light.specular.r)
    # light.specular.g = light.specular.r
    # light.specular.b = light.specular.r

    Gui.label(120, 135, "Light diffuse")

    light_color.r = Gui.slider(5, 125, 80,20, 0, 1.0,  light_color.r)
    light_color.g = light_color.r
    light_color.b = light_color.r

    Gui.label(120, 155, "Normal Strength")
    normalStrength = Gui.slider(5, 155, 80,20, 0, 100,  normalStrength)

    Gui.label(120, 175, "Metal")
    metal = Gui.slider(5, 175, 80,20, 0, 100,  metal)

    Gui.label(120, 195, "Roughness")
    roughness = Gui.slider(5, 195, 80,20, 0, 100,  roughness)

    Gui.label(120, 215, "Light Intensity")
    lightIntensity = Gui.slider(5, 215, 80,20, 0, 10,  lightIntensity)

    # Gui.label(120, 155, "Light ambient")

    # light.ambient.r = Gui.slider(5, 145, 80,20, 0, 1.0,  light.ambient.r)
    # light.ambient.g = light.ambient.r
    # light.ambient.b = light.ambient.r


    showQuad,_ = Gui.checkbox(140, 10, "Show quad", showQuad)
    #showGrid,_ = Gui.checkbox(2, 10, "Show Grid", showGrid)


    
    Gui.end()

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


    Render.set_blend(False)
    Render.set_depth_test(True)
    Render.set_clear_mode(True)
    scene.update()

    near_plane = 1.1
    far_plane = 60.5

    size = 50

    lightProjection = glm.ortho(-size, size, -size, size,  near_plane, far_plane)
    lightView = glm.lookAt(lightPos, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
    lightSpaceMatrix = lightProjection * lightView
    
    Render.set_shader(depthShader)
    depthShader.set_matrix("uLightSpaceMatrix", lightSpaceMatrix)
    buffer.begin()
    scene.render(depthShader,False)
    buffer.end()

    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()



    # Render.set_texture(diffuse.id, 0)
    # Render.set_texture(normal.id, 1)

    Render.set_shader(shader)
    shader.set_int("albedoMap",0)
    shader.set_int("normalMap",1)
    shader.set_int("shadowMap",2)
    shader.set_matrix("uLightSpaceMatrix", lightSpaceMatrix)
    shader.set_vector3f("lightColor", light_color)
    shader.set_vector3f("lightPos", lightPos)
    shader.set_float("normalStrength", normalStrength/100.0)
    shader.set_float("fixedMetalness", metal/100.0)
    shader.set_float("fixedRoughness", roughness/100.0)
    shader.set_float("lightIntensity", lightIntensity)

    Render.set_texture(buffer.id,2)

    # glActiveTexture(GL_TEXTURE2)
    # glBindTexture(GL_TEXTURE_2D, buffer.id)

    scene.render(shader)

    pick = False

    Render.set_texture(0,1)
    Render.set_texture(0,2)
    

    # glActiveTexture(GL_TEXTURE1)
    # glBindTexture(GL_TEXTURE_2D, 0)
    # glActiveTexture(GL_TEXTURE2)
    # glBindTexture(GL_TEXTURE_2D, 0)



    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_clear_mode(True)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    if showGrid:
        lines.grid(10, 10, True)
    #lines.cube(light.position.x, light.position.y, light.position.z, 0.5)



    lines.render() 

    Gui.begin(0,10, core.height-100, 260, 100, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()


    



    Gui.render(core.width , core.height)

    if showQuad:
        Render.set_shader(screenShader)
        Render.set_texture(buffer.id, 0)
        quadrender.render(0.0,0.0,1.0,1.0)


    quat_yaw = glm.angleAxis(math.radians(light_yaw), glm.vec3(0.0, 1.0, 0.0))    # Rotação ao redor do eixo Y
    quat_pitch = glm.angleAxis(math.radians(light_pitch), glm.vec3(1.0, 0.0, 0.0)) # Rotação ao redor do eixo X
    quat_roll = glm.angleAxis(math.radians(light_roll), glm.vec3(0.0, 0.0, 1.0))   # Rotação ao redor do eixo Z
    combined_rotation = quat_yaw * quat_pitch * quat_roll
    rotated_direction = combined_rotation * direction

    #lightModel.set_local_rotation(combined_rotation)
    lightModel.set_local_position(lightPos)

    #light_direction = rotated_direction





    core.flip()

core.close() 

