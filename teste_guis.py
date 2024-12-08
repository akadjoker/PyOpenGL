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

Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)







Gui.init()
lines = LinesBatch(1024*8)
Render.linesBatch = lines

slider_value = 50
button_clicks = 0
checked = False
scroll = 50

radio_labels = [
    {'caption': 'Opção 1', 'state': False},
    {'caption': 'Opção 2', 'state': False},
    {'caption': 'Opção 3', 'state': False}
]

combo_items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
selected_index = 0
is_combo_open = False
scroll_value = 0

while core.run():
    
    Render.clear()


    #2d stuff
    Render.set_clear_mode(False)
    Render.set_depth_test(False)
    Render.set_blend(True)
    Render.set_blend_mode(BlendMode.Normal)

    # Gui.begin("MainWindow", 40, 40, 250,450, {
    #         'dragging': True,
    #         'bar': True,
    #         'background': True,
    #         'title': "Test Window"
    #     })
        
    # slider_value = Gui.slider(20, 50, 200, 20, 0, 100, slider_value)
    
    # Gui.text(20, 80, f"Slider value: {slider_value:.1f}")
    
    # if Gui.button(20, 120, 150, 30, "Click Me!"):
    #     button_clicks += 1
    
    # Gui.text(20, 160, f"Button clicks: {button_clicks}")
    
    # checked, pressed = Gui.checkbox(20, 250, "Test Checkbox", checked)
    # if pressed:
    #     print("Checkbox changed to:", checked)
        
    # scroll = Gui.scrollbar(20, 200, 200, 20, scroll)
    # Gui.text(20, 230, f"Scroll value: {scroll:.1f}%")
    

    # Gui.end()


    Gui.begin("Test", 10, 10, 400, 300)
    
    selected_index, is_combo_open, scroll_value = Gui.combobox(20, 150, 200, 30, 
                                                             combo_items, selected_index, 
                                                             is_combo_open, scroll_value)
 
    
    Gui.end()


    Gui.begin(0,10, core.height-80, 260, 80, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()


    Gui.render(core.width , core.height)




    core.flip()

core.close() 



# chackValue= True
# percent =0
# rotate =0
# selected_index=0
# updated_options=0
# options = [
#     {"caption": "Option 1", "state": False},
#     {"caption": "Option 2", "state": False},
#     {"caption": "Option 3", "state": False},
# ]


# box_options = [
#         {"caption": "Check 1", "state": False},
#         {"caption": "Check 2", "state": True},
#         {"caption": "Check 3", "state": False},
#     ]

# items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10", "Item 11", "Item 12", "Item 13", "Item 14", "Item 15", "Item 16", "Item 17", "Item 18", "Item 19", "Item 20"]


# selected_index = 0  # Índice do item atualmente selecionado
# is_open = False  # Estado do combobox (aberto ou fechado)
# scroll_value = 0  # Posição do scroll na lista
# numbers =10

# string = {"text": "Hello World","select":False,"numbers":True}
# while core.run():
#     Render.set_viewport(0, 0, core.width, core.height)
#     camera.set_size(core.width, core.height)
#     Render.clear()


#     Render.set_matrix(VIEW_MATRIX, view_mat)
#     Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())




#     #Render.set_scissor_test(True)
#     #Render.set_scissor(100,100,200,200)

#     #lines.set_clip(100,100,200,200)
#     #font.set_clip(100,100,200,200)
   
   
#     lines.line2d(200,100, 100,400)
#     lines.circle(300,300, 25,16)
#     lines.rectangle(100,100,200,200)
    
#     fill.color3f(1.0,0.0,0.0)
#     fill.rectangle(50,50,100,100)
#     fill.circle(100,100, 25,16)

   
#     fill.render()
#     lines.render()

#     sprites.draw_rotate( Render.get_texture("explosion"),300,60, 64,64, 0,0, 1024/5, 1024/5, rotate)
#     sprites.draw( Render.get_texture("explosion"),300,260, 64,64)

#     sprites.render()



#     #font.draw_sprite(200,100,164, 164, 0.0, 0.0, 1.0, 1.0)

#     font.writef(10,10,"Fps:", core.get_fps())


#     font.render()

#     window_options={'background': True,'dragging': True, 'bar': True, 'title': "Config"}
#     scroll_value = Gui.begin(0,400,100,280,300, window_options, 400,  scroll_value)

#     if Gui.button(20,20,100,20,"Button 1"):
#         print("Button 1")

#     Gui.label(20, 50, "Label 1")
 
#     chackValue = Gui.checkbox(20, 80, "Checkbox 1", chackValue)
#     rotate = Gui.slider(20, 100, 200, 16, 0, 360, rotate)
    
#     percent = Gui.scrollbar(20, 120, 200, 20, percent)

    
#     Gui.radio_group(50, 180, 14, 14, 10, 2, options, border=True, title="Choose an option")
    

#     updated_options = Gui.checkbox_group(50, 260, 20, 20, 10, 2, box_options, border=True, title="Select options")
   

#     Gui.end()


#     Gui.begin(1,50, 50, 300, 250, options={"background": True,'dragging': True, "bar": True, "title": "ListBox Example"})
#     #selected ,down,scroll_value = Gui.listbox(100, 100, 180, 130, items, scroll_value)

#     if Gui.button(20,20,100,20,"Button 1"):
#         print("Button 1")

#     Gui.label(20, 50, "Label 1")

#     Gui.input_text(20, 80, 180, 20,string)

#     numbers = Gui.spin(20, 120, 40, 20, 0, 100, numbers,5)

   
#     selected_index, is_open, scroll_value = Gui.combobox(10, 10, 150, 25, items, selected_index, is_open, scroll_value)
#     Gui.end()

#     Gui.render(core.width , core.height)

#     #Render.set_scissor_test(False)

    
   
#     core.flip()

# core.close() 

