
from core.input import Input
from core.core import *
from core.batch import *
from core.font import Font, TextAlign 
from core.sprite import SpriteBatch
from core.color import Color
from core.utils import Rectangle,point_in_rect, point_in_circle
from core.render import Render


class Theme:
    def __init__(self):
        self.backgroundColor = Color(0.5, 0.5, 0.5, 1)
        self.overColor = Color(0.43, 0.41, 0.48, 1)
        self.checkBoxSelectedColor = Color(0.1, 0.1, 0.1, 1)
        self.buttonColor = Color(0.5, 0.5, 0.5, 1)
        self.buttonOverColor = Color(0.93, 0.81, 0.98, 1)
        self.buttonLabelColor = Color(0.8, 0.8, 0.8, 1)
        self.sliderFillColor = Color(0.53, 0.81, 0.98, 1)
        self.progressBarFillColor = Color(0.3, 0.91, 0.3, 1)
        self.editCursorColor = Color(0.8, 0.3, 0.3, 1)
        self.editFontColor = Color(1, 1, 1, 1)
        self.editFontColorDeactive = Color(0.89, 0.89, 0.89, 1)
        self.panelColor = Color(30/225.0, 30/225.0, 30/225.0, 0.8)
        self.windowColor = Color(0.2, 0.2, 0.2, 1)
        self.windowBarColor = Color(0.4, 0.4, 0.6, 1)
        self.fontOverColor = Color(0.9, 0.9, 0.99, 1)
        self.fontColor = Color(1, 1, 1, 1)
        self.fontOverSize = 18
        self.fontSize = 14

class Window:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.enable = False
        self.dragging = False
        self.focus = False
        self.visible = True
        self.id = 0
        self.start_x = 0
        self.start_y = 0
        self.width = 0
        self.height = 0
        self.dragX = 0
        self.dragY = 0



class Gui:
        line   =  None
        fill    =  None
        sprites =  None
        font    =  None
        ID = 0
        FocusId = 0
        X=0
        Y=0
        lastX=0
        lastY=0
        WIDTH=0
        HEIGHT=0
        isBegin = False
        visible = True
        hasFocus = False
        mouse_last_x = 0
        mouse_last_y = 0
        save_viewport = None
        theme = Theme()
        window = Window()
    
        @staticmethod
        def init(maxBatch=1024):
            Gui.font = Render.defaultFont
            Gui.line = LinesBatch(maxBatch)
            Gui.fill = FillBatch(maxBatch)
            Gui.sprites = SpriteBatch(maxBatch)
     
        
        @staticmethod
        def render():
            Gui.fill.render()
            Gui.sprites.render()
            Gui.line.render()
            Gui.font.render()
            Gui.ID = 0


        @staticmethod
        def begin(x=0, y=0, w=0, h=0, options=None):
            if options is None:
                options = {}

            Gui.isBegin = True
            Gui.ID += 1
            Gui.fill.set_color(WHITE)
            Gui.line.set_color(WHITE)
            Gui.sprites.set_color(WHITE)
            Gui.font.set_color(WHITE)
            Gui.mouse_last_x = Input.get_mouse_x()
            Gui.mouse_last_y = Input.get_mouse_y()
            Gui.window.id = Gui.ID -1

            dragging = options.get('dragging', False)
            bar = options.get('bar', False)
            background = options.get('background', True) 
            title = options.get('title', False)
            barHeight = 20
            if not Gui.window.enable:
                Gui.window.x = x
                Gui.window.y = y
                Gui.window.width = w
                Gui.window.height = h
                Gui.window.enable = True
            X = Gui.window.x
            Y = Gui.window.y
            WIDTH = Gui.window.width
            HEIGHT = Gui.window.height

            Gui.save_viewport = Render.get_scissor_box()
            #Gui.line.set_clip(X, Y-barHeight, WIDTH, HEIGHT)
            #Gui.fill.set_clip(X, Y-barHeight, WIDTH, HEIGHT)
            #Gui.font.set_clip(X, Y-barHeight, WIDTH, HEIGHT)

            OnBar =  point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y-barHeight, WIDTH, barHeight)
            OnTerminal = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            Gui.hasFocus = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y, WIDTH, HEIGHT) or OnBar or OnTerminal or Gui.window.dragging
           
           
            if OnTerminal and Input.mouse_pressed(0):
                Gui.visible = not Gui.visible
           
            if background and Gui.visible:
                Gui.fill.set_color(Gui.theme.windowColor)
                Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)
            barColor = Gui.theme.windowBarColor
            if OnBar:
                barColor.data[3] = 0.8
            else :
                barColor.data[3] = 1


            if bar:
                Gui.fill.set_color(barColor)
                Gui.fill.rectangle(X, Y-barHeight, WIDTH, barHeight)
                onColor =GREEN
                ofColor =RED
                if OnTerminal:
                    onColor.fade(1)
                    ofColor.fade(1)
                else:
                    onColor.fade(0.8)
                    ofColor.fade(0.8)
                if Gui.visible:
                     Gui.fill.set_color(onColor)
                     Gui.fill.rectangle( X + WIDTH-20, Y-(barHeight *0.5)-5, 10, 10)
                else:
                     Gui.fill.set_color(ofColor)
                     Gui.fill.rectangle(  X + WIDTH-20, Y-(barHeight *0.5)-5, 10, 10)
                     Gui.hasFocus = False
                

            if title:
                Gui.font.set_color(WHITE)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                offY = Y - (barHeight ) +  ( (Gui.font.maxHeight / Gui.theme.fontSize) / 2) 
                Gui.font.write(X + 5, offY ,title)

            if dragging:
                if (OnBar or  Gui.window.dragging) and Input.mouse_down(0):
                    if not Gui.window.dragging:
                        Gui.window.dragging = True
                        Gui.window.dragX = Input.get_mouse_x() - Gui.window.x
                        Gui.window.dragY = Input.get_mouse_y() - Gui.window.y
                    Gui.window.x = Input.get_mouse_x() - Gui.window.dragX
                    Gui.window.y = Input.get_mouse_y() - Gui.window.dragY

                if Gui.window.dragging and Input.mouse_released(0):
                    Gui.window.dragging = False
            
            

    
            

            Gui.X = Gui.window.x
            Gui.Y = Gui.window.y
            Gui.WIDTH = Gui.window.width
            Gui.HEIGHT = Gui.window.height

        @staticmethod
        def end():
            Gui.isBegin = False


        @staticmethod
        def button(x, y, w, h, label):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return
            if not Gui.visible: return

            Gui.ID += 1

            X = Gui.X + x   
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)
            isPressed = False
            if isOver and Input.mouse_down(0):
                isPressed = True

            Gui.fill.set_color(Gui.theme.backgroundColor)
            move = 0
            if isPressed:
                move = 2
            Gui.fill.rectangle(X +move, Y + move, WIDTH, HEIGHT)

            if isOver:
                Gui.line.set_color(Gui.theme.overColor)
                Gui.line.rectangle(X-1, Y-1, WIDTH+2, HEIGHT+2)
                Gui.font.set_color(Gui.theme.fontOverColor)
                Gui.font.set_size(Gui.theme.fontOverSize)
                if isPressed:
                    Gui.font.set_size(Gui.theme.fontOverSize+2)

                Gui.FocusId = Gui.ID-1
            else:
                Gui.font.set_color(Gui.theme.buttonLabelColor)
                Gui.font.set_size(Gui.theme.fontOverSize)

            Gui.font.set_allign(TextAlign.Center)
            offY = Y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)
            Gui.font.write(X+(WIDTH*0.5), offY, label)

                    
        

            if isOver and Input.mouse_released(0):
                isPressed = False


            return isPressed

        @staticmethod
        def label(x, y, label):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return
            if not Gui.visible: return

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y

            Gui.font.set_size(Gui.theme.fontSize)
            WIDTH  = Gui.font.get_text_width(label)
            HEIGHT = Gui.font.get_max_width()

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)

            if isOver:
                Gui.font.set_color(Gui.theme.fontOverColor)
                Gui.FocusId = Gui.ID-1
            else:
                Gui.font.set_color(Gui.theme.fontColor)

            Gui.font.set_allign(TextAlign.Center)
            offY = Y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)
            Gui.font.write(X+(WIDTH*0.5), offY, label)


            
        @staticmethod
        def checkbox(x, y, label, isChecked):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return isChecked
            if not Gui.visible:
                return isChecked

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            size = 16


            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, size, size)
            if isOver and Input.mouse_pressed(0):
                isChecked = not isChecked
                Gui.FocusId = Gui.ID-1
            
  
            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y, size, size)

            if isChecked:
                Gui.fill.set_color(Gui.theme.checkBoxSelectedColor)
                Gui.fill.rectangle(X + 4, Y + 4, size - 8, size - 8)

      


            
            Gui.font.set_size(Gui.theme.fontSize)
            Gui.font.set_color(Gui.theme.fontColor)
            Gui.font.set_allign(TextAlign.Left)
            OFFY = Gui.font.get_max_width()
            Gui.font.write(X + size + 8, Y -2  , label)

            return isChecked

        @staticmethod
        def slider(x, y, w, h, min_value, max_value, value):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return value
            if not Gui.visible:
                return value

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y + (HEIGHT // 2) - 2, WIDTH, 4)

            slider_pos = int((value - min_value) / (max_value - min_value) * WIDTH)
            isOver = point_in_rect(mouse_x, mouse_y, X + slider_pos - (HEIGHT // 2), Y, HEIGHT, HEIGHT)


            color = Gui.theme.sliderFillColor
            if isOver:
                color.fade(1.0)
            else:
                color.fade(0.8)

            Gui.fill.set_color(color)
            Gui.fill.rectangle(X + slider_pos - (HEIGHT // 2), Y, HEIGHT, HEIGHT)


            isInBound = point_in_rect(mouse_x, mouse_y, X , Y, WIDTH, HEIGHT+5)


            if isInBound and Input.mouse_down(0):
                new_value = (mouse_x - X) / WIDTH * (max_value - min_value) + min_value
                value = max(min(new_value, max_value), min_value)  

            return value

        @staticmethod
        def scrollbar(x, y, w, h, percentage):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return percentage
            if not Gui.visible:
                return percentage

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y + (HEIGHT // 2) - 2, WIDTH, 4)

            percentage = max(0, min(percentage, 100))

            slider_pos = int((percentage / 100) * WIDTH)
            isOver = point_in_rect(mouse_x, mouse_y, X + slider_pos - (HEIGHT // 2), Y, HEIGHT, HEIGHT)
            isInBound = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)


            color = Gui.theme.sliderFillColor
            if isOver:
                color.fade(1.0)
            else:
                color.fade(0.8)

            Gui.fill.set_color(color)
            Gui.fill.rectangle(X + slider_pos - (HEIGHT // 2), Y, HEIGHT, HEIGHT)

            if isInBound and Input.mouse_down(0):
                    new_percentage = (mouse_x - X) / WIDTH * 100
            percentage = max(0, min(new_percentage, 100))   

            return percentage

            
