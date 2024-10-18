import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.scene import Camera2D
from core.batch import *
from core.font import Font
from core.sprite import SpriteBatch
from core.gui import Gui
import sys
import glm
import math    

core = Core(720, 480, "OpenGL Demo")

Render.load_texture("assets/cube.png")
Render.load_texture("assets/font.png")
Render.load_texture("assets/explosion.png")










Render.set_blend(True)
Render.set_depth_test(False)
Render.set_blend_mode(BlendMode.NONE)
Render.set_clear_color(0.0, 0.2, 0.4)
Render.set_clear_mode(True)




camera = Camera2D(720, 480)
lines = LinesBatch(1024)
fill = FillBatch(1024)
sprites = SpriteBatch(1024)
font = Font(256)
font.load("assets/font.fnt", Render.get_texture("font"))

view_mat  = camera.get_view_matrix()
proj_mat =  camera.get_projection_matrix()


Render.set_matrix(VIEW_MATRIX, view_mat)
Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())

Gui.init()

chackValue= True
percent =0
rotate =0
selected_index=0
updated_options=0
options = [
    {"caption": "Option 1", "state": False},
    {"caption": "Option 2", "state": False},
    {"caption": "Option 3", "state": False},
]


box_options = [
        {"caption": "Check 1", "state": False},
        {"caption": "Check 2", "state": True},
        {"caption": "Check 3", "state": False},
    ]

items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10", "Item 11", "Item 12", "Item 13", "Item 14", "Item 15", "Item 16", "Item 17", "Item 18", "Item 19", "Item 20"]
scroll_value = 0

selected_index = 0  # Índice do item atualmente selecionado
is_open = False  # Estado do combobox (aberto ou fechado)
scroll_value = 0  # Posição do scroll na lista

while core.run():
    Render.set_viewport(0, 0, core.width, core.height)
    camera.set_size(core.width, core.height)
    Render.clear()


    Render.set_matrix(VIEW_MATRIX, view_mat)
    Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())


    #Render.set_scissor_test(True)
    #Render.set_scissor(100,100,200,200)

    #lines.set_clip(100,100,200,200)
    #font.set_clip(100,100,200,200)
   
   
    lines.line2d(200,100, 100,400)
    lines.circle(300,300, 25,16)
    lines.rectangle(100,100,200,200)
    
    fill.color3f(1.0,0.0,0.0)
    fill.rectangle(50,50,100,100)
    fill.circle(100,100, 25,16)

   
    fill.render()
    lines.render()

    sprites.draw_rotate( Render.get_texture("explosion"),300,60, 64,64, 0,0, 1024/5, 1024/5, rotate)
    sprites.draw( Render.get_texture("explosion"),300,260, 64,64)

    sprites.render()



    #font.draw_sprite(200,100,164, 164, 0.0, 0.0, 1.0, 1.0)

    font.writef(10,10,"Fps:", core.get_fps())


    font.render()

    window_options={'background': True,'dragging': True, 'bar': True, 'title': "Config"}
    scroll_value=Gui.begin_scroll(400,100,280,300,400,scroll_value,window_options)

    if Gui.button(20,20,100,20,"Button 1"):
        print("Button 1")

    Gui.label(20, 50, "Label 1")
 
    # chackValue = Gui.checkbox(20, 80, "Checkbox 1", chackValue)
    # rotate = Gui.slider(20, 100, 200, 16, 0, 360, rotate)
    
    # percent = Gui.scrollbar(20, 120, 200, 20, percent)

    
    # selected_index,isChanged = Gui.radio_group(50, 160, 14, 14, 10, 2, options, border=True, title="Choose an option")
    
    # if isChanged:
    #     print(f"Selected radio index: {selected_index} isChanged: {isChanged}")

    # updated_options = Gui.checkbox_group(50, 220, 20, 20, 10, 2, box_options, border=True, title="Select options")
   

    Gui.end()


    Gui.begin(50, 50, 300, 250, options={"background": True,'dragging': True, "bar": True, "title": "ListBox Example"})
    #selected ,down,scroll_value = Gui.listbox(100, 100, 180, 130, items, scroll_value)

    if Gui.button(20,20,100,20,"Button 1"):
        print("Button 1")

    Gui.label(20, 50, "Label 1")

    #print(f"selected: {selected} down: {down} scroll_value: {scroll_value}")

    #selected_index, is_open, scroll_value = Gui.combobox(10, 10, 150, 25, items, selected_index, is_open, scroll_value)
    Gui.end()

    Gui.render()

    #Render.set_scissor_test(False)

    
   
    core.flip()

core.close() 

