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
from core.material import AmbientShader
import sys
import glm
import math   


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(1024, 920, "OpenGL Demo")


Render.load_texture("assets/cube.png")
Render.load_texture("assets/FloorTexture.png")
Render.load_texture("assets/defaultTexture.png")




scene = Scene()

plane = create_plane(5,5,5,5)
cube = create_cube()
sphere = load_obj("assets/42.obj")
sphere.translate(0.0, 2.0, 0.0)


Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)


shader = AmbientShader()

camera = Camera(45.0,core.width / core.height)
camera.set_perspective(45.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)

scene.set_camera(camera)

model = scene.create_model(shader)
model.add_material(Material(Render.get_texture("defaultTexture")))
model.add_mesh(plane)

model.scale(20.0, 1.0, 20.0)


model = scene.create_model(shader)
model.add_material(Material(Render.get_texture("cube")))
model.add_material(Material(Render.get_texture("FloorTexture")))

model.add_mesh(cube)
model.add_mesh(sphere)

model.translate(0.0, 1.0, 0.0)

mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)


while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()



    speed = core.get_delta_time() * 125

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

    scene.render()
    scene.update()

    pick = False
    light = Render.get_light(0)

    #ray = scene.camera_ray(Input.get_mouse_x(), Input.get_mouse_y())
    ray = scene.unproject(Input.get_mouse_x(), Input.get_mouse_y())



    Render.set_blend(True)
    Render.set_depth_test(False)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_clear_mode(True)
    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    lines.grid(10, 10, True)
    lines.cube(light.position.x, light.position.y, light.position.z, 0.5)

    for node in scene.nodes:
        if ray.intersects_box(node.get_bounding_box()):
            lines.draw_bounding_box(node.get_bounding_box(), RED)
            
        else:
            lines.draw_bounding_box(node.get_bounding_box(), GREEN)



    #if pick:
    #    scene.debug(lines)
    lines.render() 

    Gui.begin(0,10, core.height-80, 260, 80, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()


    light.camera = camera.get_world_position()

    Gui.begin(1, 10,40, 300, 250, options={"background": True,'dragging': True, "bar": True, "title": "Light"})
    
    Gui.label(120, 15, "Ambient Strength")
    Gui.label(120, 35, "Specular Strength")
    light.ambient_strength = Gui.slider(5, 5, 80,20, 0, 1.0,  light.ambient_strength)
    light.specular_strength = Gui.slider(5, 25, 80,20, 0, 1.0,  light.specular_strength)


    Gui.label(120, 55, "Light X")
    Gui.label(120, 75, "Light Y")
    Gui.label(120, 95, "Light Z")

    light.position.x = Gui.slider(5, 45, 80,20, -100, 100,  light.position.x)
    light.position.y = Gui.slider(5, 65, 80,20, -100, 100,  light.position.y)
    light.position.z = Gui.slider(5, 85, 80,20, -100, 100,  light.position.z)

    Gui.label(120, 115, "Light Color")

    light.color.r = Gui.slider(5, 105, 80,20, 0, 1.0,  light.color.r)
    light.color.g = light.color.r
    light.color.b = light.color.r
    
    Gui.end()
    


    Gui.render(core.width , core.height)


    core.flip()

core.close() 

