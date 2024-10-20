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



def update_light_positions(light,position, time, radius):
    base_position = position
    angle = time + (math.pi / 2)  
    new_x = base_position.x + radius * math.cos(angle)
    new_z = base_position.z + radius * math.sin(angle)

    light.position =  glm.vec3(new_x, base_position.y, new_z)

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(1024, 920, "OpenGL Demo")


Render.load_texture("assets/brickwall_diffuse.jpg","brickwall")
Render.load_texture("assets/brickwall_specular.jpg","brickwall_specular")

Render.load_texture("assets/defaultTexture.png","default")
Render.load_texture("assets/defaultTexture_specular.png","default_specular")





scene = Scene()


tile_size = (15.0, 15.0)
tile_count = (10, 10)
hill_height = 1.0
hill_count = (1.0, 1.0)
texture_repeat_count = (4.0, 4.0)
plane = create_hill_plane_mesh(tile_size, tile_count, hill_height, hill_count, texture_repeat_count)

#plane = create_plane(5,5,5,5)
cube = create_cube()
sphere = create_sphere(10, 10)
mesh = load_obj("assets/room.obj")
mesh.rotate(0,90,0)



Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)

light =  scene.create_ambient_light(glm.vec3(0.1, 0.1, 0.1))
#scene.create_directional_light(glm.vec3(0.01, 0.01, 0.01), glm.vec3(0.0, -0.8, 0.4))
#scene.create_ambient_light(glm.vec3(0.2, 0.2, 0.2))
shader = light.shader

lights =  []
positions = []

point = scene.create_point_light(glm.vec3(1.0, 0.0, 0.0), glm.vec3(40.0, 2.0, 40.0))
lights.append(point)
point = scene.create_point_light(glm.vec3(1.0, 0.0, 0.0), glm.vec3(-40.0, 2.0, 40.0))
lights.append(point)
point = scene.create_point_light(glm.vec3(0.0, 0.0, 1.0), glm.vec3(-40.0, 2.0, -40.0))
lights.append(point)
point = scene.create_point_light(glm.vec3(0.0, 0.0, 1.0), glm.vec3(40.0, 2.0, -40.0))
lights.append(point)


positions.append(glm.vec3(40.0,2.0,40.0))
positions.append(glm.vec3(-40.0,2.0,40.0))
positions.append(glm.vec3(-40.0,2.0,-40.0))
positions.append(glm.vec3(40.0,2.0,-40.0))


camera = Camera(45.0,core.width / core.height)
camera.set_perspective(45.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)

scene.set_camera(camera)

floor = scene.create_model(shader)
floor.add_material(Material(Render.get_texture("default"), Render.get_texture("default_specular")))
floor.add_mesh(plane)
floor.add_mesh(mesh)


model = scene.create_model(shader)
model.add_material(Material(Render.get_texture("brickwall"), Render.get_texture("brickwall_specular")))
model.add_mesh(cube)
model.translate(0.0, 1.0, 0.0)


# terrain = scene.create_terrain_block(shader,"assets/terrain-texture.jpg","assets/terrain-heightmap.png", 
#     stretch_size=(1.0, 1.0),  # tamanho do terreno
#     max_height=6.0,  # máxima do terreno
#     max_vtx_block_size=(64, 64),  #  máximo dos blocos
#     debug_borders=False)


mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)
position = glm.vec3(0.0, 5.0, 0.0)
range = 100.0
time = 0.0
radius =5.0
while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()


    update_light_positions(lights[0],positions[0],  time, radius)
    update_light_positions(lights[1],positions[1],  time, radius)
    update_light_positions(lights[2],positions[2],  time, radius)
    update_light_positions(lights[3],positions[3],  time, radius)

    time += 0.02


    speed =  4

    for i, light in enumerate(lights):
            if i > 4:
                if light.enable:
                    #light.position.x -= 0.5
                    if light.position.x < -50.0:
                        light.enable =False
        

    if Input.mouse_down(0) and not Gui.has_focus():
        yaw   += Input.get_mouse_delta_x()  *  mouseSensitivity
        pitch -= Input.get_mouse_delta_y()  *  mouseSensitivity
        pitch = max(-89.0, min(89.0, pitch))
        camera.rotate(pitch, yaw, 0.0)

    if Input.mouse_released(1):
        position = camera.get_world_position()
        have =False
        for i, light in enumerate(lights):
            if i > 4:
                if not light.enable:
                    light.position=glm.vec3(position.x, position.y, position.z) 
                    light.enable =True
                    have = True
                    break

        if not have:
            point = scene.create_point_light(glm.vec3(0.2, 0.2, 0.2),glm.vec3(position.x, position.y, position.z))
            lights.append(point)


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
    scene.render_forward()

    pick = False





    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.Normal)
    Render.set_clear_mode(True)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    #lines.grid(10, 10, True)


    lines.render() 

    Gui.begin(0,10, core.height-80, 260, 80, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()



    Gui.begin(1, 10,40, 300, 250, options={"background": True,'dragging': True, "bar": True, "title": "Light"})
    


    

    


    # Gui.label(120, 155, "Light ambient")

    # light.diffuse.r = Gui.slider(5, 145, 80,20, 0, 1.0,  light.ambient.r)
    # light.diffuse.g = light.diffuse.r
    # light.diffuse.b = light.diffuse.r




    
    Gui.end()
    


    Gui.render(core.width , core.height)






    core.flip()

core.close() 

