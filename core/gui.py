
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
        self.backgroundColorOff = Color(0.5, 0.5, 0.5, 0.8)
        self.overColor = Color(0.43, 0.41, 0.48, 1)
        self.checkBoxSelectedColor = Color(0.1, 0.1, 0.1, 1)
        self.buttonColor = Color(0.5, 0.5, 0.5, 1)
        self.buttonOverColor = Color(0.93, 0.81, 0.98, 1)
        self.buttonLabelColor = Color(0.8, 0.8, 0.8, 1)
        self.sliderFillColor = Color(0.53, 0.91, 0.98, 1)
        self.sliderFillColorOff = Color(0.53, 0.91, 0.98, 0.8)
        self.lineColor = Color(0.8, 0.8, 0.8, 1)
        self.progressBarFillColor = Color(0.23, 0.91, 0.28, 1)
        self.progressBarFillColorOff = Color(0.23, 0.91, 0.28, 0.8)
        self.editCursorColor = Color(0.8, 0.3, 0.3, 1)
        self.editFontColor = Color(1, 1, 1, 1)
        self.editFontColorDeactive = Color(0.89, 0.89, 0.89, 1)
        self.panelColor = Color(30/225.0, 30/225.0, 30/225.0, 0.8)
        self.windowColor = Color(0.2, 0.2, 0.2, 1)
        self.windowBarColor = Color(0.4, 0.4, 0.6, 1)
        self.windowBarColorOff = Color(0.4, 0.4, 0.6, 0.8)
        self.fontOverColor = Color(0.9, 0.9, 0.99, 1)
        self.selectedColor = Color(0.3, 0.3, 0.3, 1)
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
            Gui.fill.set_clip(X, Y-barHeight, WIDTH, HEIGHT)
            Gui.font.enable_clip(False)

            OnBar =  point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y-barHeight, WIDTH, barHeight-4)
            OnTerminal = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            Gui.hasFocus = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y, WIDTH, HEIGHT) or OnBar or OnTerminal or Gui.window.dragging
           
     
            if title:
                Gui.font.set_color(WHITE)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                offY = Y - (barHeight ) +  ( (Gui.font.maxHeight / Gui.theme.fontSize) / 2) 
                Gui.font.write(X + 5, offY ,title)
            if OnTerminal and Input.mouse_pressed(0):
                Gui.window.visible = not Gui.window.visible
           
            if background and Gui.visible:
                Gui.fill.set_color(Gui.theme.windowColor)
                Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)


            if bar:
                if OnBar:
                    Gui.fill.set_color(Gui.theme.windowBarColor)
                else :
                    Gui.fill.set_color(Gui.theme.windowBarColorOff)
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
                
            Gui.line.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.fill.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.font.set_clip(X, Y, WIDTH, HEIGHT-barHeight)



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
            
            

    
            # Gui.line.set_color(RED)
            # Gui.line.rectangle( X, Y-barHeight, WIDTH, barHeight-4)
            # Gui.line.rectangle(  X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            # Gui.line.rectangle(  X, Y, WIDTH, HEIGHT)

            Gui.X = Gui.window.x
            Gui.Y = Gui.window.y 
            Gui.WIDTH = Gui.window.width
            Gui.HEIGHT = Gui.window.height
            Gui.fill.set_color(WHITE)
            Gui.line.set_color(WHITE)
            Gui.sprites.set_color(WHITE)
            Gui.font.set_color(WHITE)

        @staticmethod
        def begin_scroll(x, y, w, h, content_height=None, scroll_value=0,options=None):
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
            if content_height is None:
                content_height = HEIGHT

            max_scroll = max(0, content_height - HEIGHT)
            scroll_value = max(0, min(scroll_value, max_scroll))

            Gui.save_viewport = Render.get_scissor_box()
            Gui.fill.set_clip(X, Y-barHeight, WIDTH, HEIGHT)
            Gui.font.enable_clip(False)

            OnBar =  point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y-barHeight, WIDTH, barHeight-4)
            OnTerminal = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            Gui.hasFocus = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y, WIDTH, HEIGHT) or OnBar or OnTerminal or Gui.window.dragging
           
     
            if title:
                Gui.font.set_color(WHITE)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                offY = Y - (barHeight ) +  ( (Gui.font.maxHeight / Gui.theme.fontSize) / 2) 
                Gui.font.write(X + 5, offY ,title)
            if OnTerminal and Input.mouse_pressed(0):
                Gui.window.visible = not Gui.window.visible
           
            if background and Gui.visible:
                Gui.fill.set_color(Gui.theme.windowColor)
                Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)


            if bar:
                if OnBar:
                    Gui.fill.set_color(Gui.theme.windowBarColor)
                else :
                    Gui.fill.set_color(Gui.theme.windowBarColorOff)
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
                
            Gui.line.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.fill.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.font.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            # Handle scroll bar if content exceeds window height
            if content_height > HEIGHT and Gui.window.enable:
                scrollbar_height = int((HEIGHT / content_height) * HEIGHT)
                scrollbar_y = Y + (scroll_value / max_scroll) * (HEIGHT - scrollbar_height)
                
                onScroll = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X + WIDTH - 10, scrollbar_y, 10, scrollbar_height)
                if onScroll:
                    Gui.fill.set_color(WHITE)
                else:
                    Gui.fill.set_color(Gui.theme.backgroundColor)

                Gui.fill.rectangle(X + WIDTH - 10, scrollbar_y, 10, scrollbar_height)

                # Update scroll value if mouse is on scrollbar
                if onScroll and Input.mouse_down(0):
                    new_scroll_value = ((Input.get_mouse_y() - Y) / HEIGHT) * max_scroll
                    scroll_value = max(0, min(new_scroll_value, max_scroll))
                    


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
            
            

    
            # Gui.line.set_color(RED)
            # Gui.line.rectangle( X, Y-barHeight, WIDTH, barHeight-4)
            # Gui.line.rectangle(  X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            # Gui.line.rectangle(  X, Y, WIDTH, HEIGHT)

            Gui.X = Gui.window.x
            Gui.Y = Gui.window.y - scroll_value
            Gui.WIDTH = Gui.window.width
            Gui.HEIGHT = Gui.window.height
            Gui.fill.set_color(WHITE)
            Gui.line.set_color(WHITE)
            Gui.sprites.set_color(WHITE)
            Gui.font.set_color(WHITE)

            return scroll_value

        @staticmethod
        def end():
            Gui.isBegin = False
            Gui.window.enable = False

            

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
        def text(x, y, label):
          

          

            Gui.font.set_size(Gui.theme.fontSize)
            WIDTH  = Gui.font.get_text_width(label)
            HEIGHT = Gui.font.get_max_width()

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, x, y, WIDTH, HEIGHT)

            if isOver:
                Gui.font.set_color(Gui.theme.fontOverColor)
                Gui.FocusId = Gui.ID-1
            else:
                Gui.font.set_color(Gui.theme.fontColor)

            Gui.font.set_allign(TextAlign.Center)
            offY = y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)
            Gui.font.write(x+(WIDTH*0.5), offY, label)

            
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
            isPressed = False


            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, size, size)
            if isOver:
                Gui.FocusId = Gui.ID-1
                Gui.fill.set_color(Gui.theme.backgroundColor)
                Gui.font.set_color(Gui.theme.fontOverColor)
            else:
                Gui.fill.set_color(Gui.theme.backgroundColorOff)
                Gui.font.set_color(Gui.theme.fontColor)
            if isOver and Input.mouse_pressed(0):
                isChecked = not isChecked
                Gui.FocusId = Gui.ID-1
                isPressed = True
            
  
            Gui.fill.rectangle(X, Y, size, size)

            if isChecked:
                Gui.fill.set_color(Gui.theme.checkBoxSelectedColor)
                Gui.fill.rectangle(X + 4, Y + 4, size - 8, size - 8)

      


            
            Gui.font.set_size(Gui.theme.fontSize)
            Gui.font.set_color(Gui.theme.fontColor)
            Gui.font.set_allign(TextAlign.Left)
            OFFY = Gui.font.get_max_width()
            Gui.font.write(X + size + 8, Y -2  , label)

            return (isChecked, isPressed)

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


    
            if isOver:
                Gui.fill.set_color(Gui.theme.sliderFillColor)
            else:
                Gui.fill.set_color(Gui.theme.sliderFillColorOff)


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
            Gui.fill.rectangle(X, Y , WIDTH, HEIGHT)

            percentage = max(0, min(percentage, 100))

            slider_pos = int((percentage / 100) * WIDTH)
            isInBound = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)



            if isInBound:
                Gui.fill.set_color(Gui.theme.progressBarFillColor)

            else:
                Gui.fill.set_color(Gui.theme.progressBarFillColorOff)

            Gui.fill.rectangle(X , Y, slider_pos , HEIGHT)

            if isInBound and Input.mouse_down(0):
                new_percentage = (mouse_x - X) / WIDTH * 100

                percentage = max(0, min(new_percentage, 100))   

            return percentage

                    
        @staticmethod
        def slider_vertical(x, y, w, h, min_value, max_value, value):
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
            Gui.fill.rectangle(X + (WIDTH // 2) - 2, Y, 4, HEIGHT)  


            slider_pos = int((value - min_value) / (max_value - min_value) * HEIGHT)
            isOver = point_in_rect(mouse_x, mouse_y, X, Y + slider_pos - (WIDTH // 2), WIDTH, WIDTH)

            if isOver:
                Gui.fill.set_color(Gui.theme.sliderFillColor)
            else:
                Gui.fill.set_color(Gui.theme.sliderFillColorOff)

            
            Gui.fill.rectangle(X, Y + slider_pos - (WIDTH // 2), WIDTH, WIDTH)  

            isInBound = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)

            if isInBound and Input.mouse_down(0):
                new_value = (mouse_y - Y) / HEIGHT * (max_value - min_value) + min_value
                value = max(min(new_value, max_value), min_value) 

            return value
        @staticmethod
        def scrollbar_vertical(x, y, w, h, percentage):
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
            Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)  


            percentage = max(0, min(percentage, 100))


            slider_pos = int((percentage / 100) * HEIGHT)
            isOver = point_in_rect(mouse_x, mouse_y, X, Y + slider_pos - (WIDTH // 2), WIDTH, WIDTH)


            if isOver:
                Gui.fill.set_color(Gui.theme.progressBarFillColor)
            else:
                Gui.fill.set_color(Gui.theme.progressBarFillColorOff)

            
            Gui.fill.rectangle(X, Y, WIDTH, slider_pos)  

            isInBound = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)

            if isInBound and Input.mouse_down(0):
                new_percentage = (mouse_y - Y) / HEIGHT * 100
                percentage = max(0, min(new_percentage, 100))  

            return percentage

        @staticmethod
        def radio(x, y, w, h, label, value):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return (-1, False)
            
            if not Gui.visible:
                return (-1, False)

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h
            radius = min(WIDTH, HEIGHT) * 0.5

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X - (WIDTH * 0.5), Y - (HEIGHT * 0.5), WIDTH, HEIGHT)
            isPressed = False

            if isOver and Input.mouse_pressed(0):
                isPressed = True


            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.circle(X, Y, radius)

            if isOver:
                Gui.fill.set_color(Gui.theme.overColor)
                Gui.fill.circle(X, Y, radius + 2)

            if isPressed:
                value = not value


            if value:
                Gui.fill.set_color(Gui.theme.checkBoxSelectedColor)
                Gui.fill.circle(X, Y, radius * 0.5)


            if isOver:
                Gui.font.set_color(Gui.theme.fontOverColor)
                Gui.font.set_size(Gui.theme.fontOverSize - 2)
                Gui.FocusId = Gui.ID - 1
            else:
                Gui.font.set_color(Gui.theme.fontColor)
                Gui.font.set_size(Gui.theme.fontSize + 2)


            offY = Y - (Gui.font.get_max_height() * 0.5)
            offX = X + (WIDTH * 0.5) + (Gui.font.get_max_width() * 0.5)

            Gui.font.set_allign(TextAlign.Left)
            Gui.font.write(offX, offY, label)

            return (value, isPressed)

        @staticmethod
        def radio_group(x, y, w, h, gap, cols, labels, border=False, title=""):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return (-1, False)
            
            if not Gui.visible:
                return (-1, False)

            Gui.ID += 1

            count = len(labels)
            space = 60
            index = -1
            row = 0
            col = 0
            offX = x
            offY = y
            X = Gui.X + x
            Y = Gui.Y + y

            maxWidth = 1
            max_width = 0
            max_height = 0
            isPressed = False
            isChanged = False


            for label in labels:
                width = Gui.font.get_text_width(label['caption'])
                if width > maxWidth:
                    maxWidth = width
            
            space = (maxWidth + gap) + w


            for i in range(count):
                if col >= cols:
                    col = 0
                    row += 1
                    offX = x
                    offY += h + gap
                
                label = labels[i]['caption']
                value = labels[i]['state']

                value, isChanged = Gui.radio(offX, offY, w, h, label, value)

                if isChanged:
                    isPressed = True

                if value:
                    index = i
                    for j in range(count):
                        if j != i:
                            labels[j]['state'] = False
                
                labels[i]['state'] = value

                col += 1
                offX += w + space

            max_width = (w + space) * cols + (w * 0.5)
            max_height = (h + gap) * (row + 1) + h

            if border:
                Gui.line.set_color(GRAY)
                Gui.line.line2d(X - w, Y - h, X - w, Y - h + max_height)
                Gui.line.line2d(X - w, Y - h + max_height, X - w + max_width, Y - h + max_height)
                Gui.line.line2d(X - w + max_width, Y - h + max_height, X - w + max_width, Y - h)

                textWidth = Gui.font.get_text_width(title)

                Gui.line.line2d(X - w, Y - h, X - 1, Y - h)
                Gui.line.line2d(X - w + textWidth + w, Y - h, X - w + max_width, Y - h)

            if title:
                Gui.font.set_color(Gui.theme.fontColor)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                Gui.font.write(w + X - w, Y - h - 15, title)

            return (index, isPressed)

        @staticmethod
        def checkbox_group(x, y, w, h, gap, cols, labels, border=False, title=""):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return labels
            
            if not Gui.visible:
                return labels

            Gui.ID += 1

            count = len(labels)
            space = 60
            row = 0
            col = 0
            offX = x
            offY = y
            X = Gui.X + x
            Y = Gui.Y + y

            maxWidth = 1
            max_width = 0
            max_height = 0
            isChanged = False
            isPressed = False

            # Calcula a largura máxima dos labels
            for label in labels:
                width = Gui.font.get_text_width(label['caption'])
                if width > maxWidth:
                    maxWidth = width
            
            space = (maxWidth + gap) + w

            # Renderiza os checkboxes
            for i in range(count):
                if col >= cols:
                    col = 0
                    row += 1
                    offX = x
                    offY += h + gap
                
                label = labels[i]['caption']
                value = labels[i]['state']

                value, isChanged = Gui.checkbox(offX, offY,  label, value)

                if isChanged:
                    isPressed = True
                labels[i]['state'] = value

                col += 1
                offX += w + space

            max_width = (w + space) * cols + (w * 0.5)
            max_height = (h + gap) * (row + 1) + h

            if border:
                Gui.line.set_color(GRAY)
                Gui.line.line2d(X - w, Y - h, X - w, Y - h + max_height)
                Gui.line.line2d(X - w, Y - h + max_height, X - w + max_width, Y - h + max_height)
                Gui.line.line2d(X - w + max_width, Y - h + max_height, X - w + max_width, Y - h)

                textWidth = Gui.font.get_text_width(title)

                Gui.line.line2d(X - w, Y - h, X - 1, Y - h)
                Gui.line.line2d(X - w + textWidth + w, Y - h, X - w + max_width, Y - h)

            if title:
                Gui.font.set_color(Gui.theme.fontColor)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                Gui.font.write(w + X - w, Y - h - 15, title)

            return labels, isPressed

        @staticmethod
        def panel(x, y, w, h):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return

            if not Gui.visible: return

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            Gui.fill.set_color(Gui.theme.panelColor)
            Gui.fill.rectangle( X, Y, WIDTH, HEIGHT)


            return
        
        @staticmethod
        def separator(x, y, w, h,Color=GRAY,fill=True):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return

            if not Gui.visible: return

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            Gui.fill.set_color( Color)

            if fill:
                Gui.fill.rectangle( X, Y, WIDTH, HEIGHT)
            else: 
                Gui.line.rectangle(X, Y,  WIDTH, HEIGHT)

            return

        @staticmethod
        def progress_bar(x, y, w, h,  max, value):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return

            if not Gui.visible: return

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            if value > max:
                value = max

            if value < 0:   
                value = 0
            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT)
            if isOver:
                Gui.FocusId =Gui.ID-1

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle( X, Y, WIDTH, HEIGHT)
            Gui.fill.setColor(Gui.theme.progressBarFillColor)
            Gui.fill.rectangle( X, Y, WIDTH * (value / max), HEIGHT)

            return value




        @staticmethod
        def listbox(x, y, w, h, items, scroll_value):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return (-1, False, scroll_value)
            if not Gui.visible:
                return (-1, False, scroll_value)

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h
            item_height = 20  # Altura de cada item (ajustar ??)
            visible_items = h // item_height  # Quantos itens podem ser mostrados de uma vez??
            selected = -1
            isDown = False
            
            

            Gui.panel(x, y, w, h)

            # Calcula o máximo de scroll baseado no número de itens
            max_scroll = max(0, len(items) - visible_items)
            scroll_value = max(0, min(scroll_value, max_scroll))
            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            
             
            # Desenha os itens visíveis dentro do painel
            start_index = int(scroll_value)
            for i in range(visible_items):
                if start_index + i >= len(items):
                    break  
                item_label = items[start_index + i]
                item_y = item_height  + i * item_height  # Ajusta a posição Y do item
                
                onItem = point_in_rect(mouse_x, mouse_y, X, Y + (item_y-10) - (item_height//2), WIDTH-12, item_height)
                if onItem or selected == start_index + i:
                     Gui.separator(x, (y + item_y)- (item_height-2), w-12, item_height, Color=RED,fill=False)
                     if Input.mouse_down(0):
                        Gui.separator(x, (y + item_y)- (item_height-2), w-12, item_height, Color=GRAY,fill=True)
                        selected = start_index + i
                        isDown = True
                    
         
                
                Gui.text(X + 5, (Y + item_y)-(item_height//2), item_label)  # Ajuste do label dentro do item


            # Desenhar a barra de scroll se houver mais itens do que espaço
            if len(items) > visible_items:
                scrollbar_height = int((visible_items / len(items)) * HEIGHT)
                scrollbar_y = Y + (scroll_value / max_scroll) * (HEIGHT - scrollbar_height)
                
            
                onScroll = point_in_rect(mouse_x, mouse_y, X + w - 10, scrollbar_y, 20, scrollbar_height)
                if onScroll:
                    Gui.fill.set_color(WHITE) 
                else:
                    Gui.fill.set_color(Gui.theme.backgroundColor)  


                Gui.fill.rectangle(X + w - 10, scrollbar_y, 10, scrollbar_height)


                if onScroll and Input.mouse_down(0):
                    new_scroll_value = ((mouse_y - Y) / HEIGHT) * max_scroll
                    scroll_value = max(0, min(new_scroll_value, max_scroll))

            return (selected, isDown, scroll_value)

        @staticmethod
        def _combobox_button(x, y, w, h, label):
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
            if isOver and Input.mouse_pressed(0):
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
        def combobox(x, y, w, h, items, selected_index, is_open, scroll_value):
            if not Gui.isBegin:
                print("widgets must be chamados entre Begin() e End()")
                return (selected_index, is_open, scroll_value)
            
            if not Gui.visible:
                return (selected_index, is_open, scroll_value)

            Gui.ID += 1


            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()


            selected_item = items[selected_index] if selected_index >= 0 else ""
            isButtonPressed = Gui._combobox_button(x, y, w, h, selected_item)  

            # Alterna o estado do combobox (abrir/fechar) quando o botão é pressionado
            if isButtonPressed:
                is_open = not is_open

            # Se o combobox estiver aberto, renderiza a lista suspensa dentro da janela
            if is_open:
                listbox_height = min(4, len(items)) * 20  # Ajusta o tamanho da lista visível (máx. 4 itens????)
                new_selected, isItemPressed, scroll_value = Gui.listbox(x, y + h, w, listbox_height, items, scroll_value)


                if isItemPressed:
                    selected_index = new_selected
                    is_open = False 
        
            if is_open and not point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT + listbox_height):
                if Input.mouse_pressed(0):  
                    is_open = False  
            return (selected_index, is_open, scroll_value)