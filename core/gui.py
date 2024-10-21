
from core.input import Input
from core.core import *
from core.batch import *
from core.font import Font, TextAlign 
from core.sprite import SpriteBatch
from core.color import Color
from core.utils import Rectangle,point_in_rect, point_in_circle
from core.render import Render
import time

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
        isBegin = False
        visible = True
        isDragging = -1
        hasFocus = False
        mouse_last_x = 0
        mouse_last_y = 0
        save_viewport = None
        theme = Theme()
        windows = {}
        window = None
        state = 0

        @staticmethod
        def has_focus():
            return Gui.hasFocus
    
        @staticmethod
        def init(maxBatch=1024):
            Gui.font = Render.defaultFont
            Gui.line = LinesBatch(maxBatch)
            Gui.fill = FillBatch(maxBatch)
            Gui.sprites = SpriteBatch(maxBatch)
     
        
        @staticmethod
        def render(width=0, height=0):
            
            Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
            Render.set_matrix(VIEW_MATRIX, glm.mat4(1.0))
            view = glm.ortho(0.0, width , height, 0.0, -1.0, 1.0)
            Render.set_matrix(PROJECTION_MATRIX, view)
            Gui.fill.render()
            Gui.sprites.render()
            Gui.line.render()
            Gui.font.render()
            Gui.ID = 0
            
            


        @staticmethod
        def _can_process():
            return Gui.isBegin and Gui.isDragging == -1
        

        @staticmethod
        def is_window_visible(ID):
            if ID in Gui.windows:
                return Gui.windows[ID]['visible']
            return False
        

        @staticmethod
        def begin(ID, x, y, w, h, options=None , content_height=None, scroll_value=0):
            if options is None:
                options = {}
            Gui.isBegin = True


            if ID not in Gui.windows:
                Gui.windows[ID] = {
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'dragging': False,
                'dragX': 0,
                'dragY': 0,
                'visible': True,
                'id': ID
            }
            window = Gui.windows[ID]
            Gui.window = window
            Gui.fill.set_color(WHITE)
            Gui.line.set_color(WHITE)
            Gui.sprites.set_color(WHITE)
            Gui.font.set_color(WHITE)
            Gui.mouse_last_x = Input.get_mouse_x()
            Gui.mouse_last_y = Input.get_mouse_y()
            
            
            dragging = options.get('dragging', False)
            bar = options.get('bar', False)
            background = options.get('background', True) 
            title = options.get('title', False)
            barHeight = 20
    
            X = window["x"]
            Y = window["y"]
            WIDTH = window["width"]
            HEIGHT = window["height"]
        
            if content_height is None:
                content_height = HEIGHT

            max_scroll = max(0, content_height - HEIGHT)
            scroll_value = max(0, min(scroll_value, max_scroll))



            Gui.save_viewport = Render.get_scissor_box()
            Gui.fill.set_clip(X, Y-barHeight, WIDTH, HEIGHT)
            Gui.font.enable_clip(False)

            OnBar =  point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y-barHeight, WIDTH, barHeight-4)
            OnTerminal = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X+WIDTH-25, Y-barHeight+4, 20, barHeight-8) 
            Gui.hasFocus = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X, Y, WIDTH, HEIGHT) or OnBar or OnTerminal or window['dragging']
            if (OnBar and Input.mouse_pressed(0)):
                Gui.isDragging = ID

           
     
            if title:
                Gui.font.set_color(WHITE)
                Gui.font.set_size(Gui.theme.fontSize)
                Gui.font.set_allign(TextAlign.Left)
                offY = Y - (barHeight ) +  ( (Gui.font.maxHeight / Gui.theme.fontSize) / 2) 
                Gui.font.write(X + 5, offY ,title)
            if bar:
                if OnBar:
                    Gui.fill.set_color(Gui.theme.windowBarColor)
                else :
                    Gui.fill.set_color(Gui.theme.windowBarColorOff)
                Gui.fill.rectangle(X, Y-barHeight, WIDTH, barHeight)
                onColor =GREEN
                ofColor =RED
                if OnTerminal :
                    onColor.fade(1)
                    ofColor.fade(1)
                else:
                    onColor.fade(0.8)
                    ofColor.fade(0.8)
                if window["visible"]:
                     Gui.fill.set_color(onColor)
                     Gui.fill.rectangle( X + WIDTH-20, Y-(barHeight *0.5)-5, 10, 10)
                else:
                     Gui.fill.set_color(ofColor)
                     Gui.fill.rectangle(  X + WIDTH-20, Y-(barHeight *0.5)-5, 10, 10)
                     Gui.hasFocus = False
            if OnTerminal and Input.mouse_pressed(0):
                window["visible"] = not window["visible"]
            Gui.visible = window["visible"]
            if not window["visible"]:
                return (scroll_value)
           
            if background and window["visible"]:
                Gui.fill.set_color(Gui.theme.windowColor)
                Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)


            isDragging = False 
            isScrolling = False
                
            Gui.line.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.fill.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            Gui.font.set_clip(X, Y, WIDTH, HEIGHT-barHeight)
            #Gui.font.enable_clip(False)
            # Handle scroll bar if content exceeds window height
            if content_height > HEIGHT:
                scrollbar_height = int((HEIGHT / content_height) * HEIGHT)
                scrollbar_y = Y + (scroll_value / max_scroll) * (HEIGHT - scrollbar_height)
                
                onScroll = point_in_rect(Input.get_mouse_x(), Input.get_mouse_y(), X + WIDTH - 10, scrollbar_y, 10, scrollbar_height) and Gui.isDragging == -1
                if onScroll:
                    Gui.fill.set_color(WHITE)
                else:
                    Gui.fill.set_color(Gui.theme.backgroundColor)

                Gui.fill.rectangle(X + WIDTH - 10, scrollbar_y, 10, scrollbar_height)

                # Update scroll value if mouse is on scrollbar
                if onScroll and Input.mouse_down(0):
                    new_scroll_value = ((Input.get_mouse_y() - Y) / HEIGHT) * max_scroll
                    scroll_value = max(0, min(new_scroll_value, max_scroll))
                    isScrolling = True
                    


            if dragging:
                if (OnBar or   window['dragging'] ) and Input.mouse_down(0):
                    if not  window['dragging']:
                        window['dragging'] = True
                        window['dragX'] = Input.get_mouse_x() - window["x"]
                        window['dragY'] = Input.get_mouse_y() - window["y"]
                    
                    if Gui.isDragging == ID:
                        window["x"] = Input.get_mouse_x() - window['dragX']
                        window["y"] = Input.get_mouse_y() - window['dragY']
                        isDragging = True


                if window['dragging'] and Input.mouse_released(0):
                    window['dragging'] = False
                    Gui.isDragging = -1
                    
            
            #if isDragging or isScrolling:
            #    Render.set_cursor("hand")
            
            

    
            # Gui.line.set_color(RED)
            # Gui.line.rectangle( X, Y-barHeight, WIDTH, barHeight-4)
            # Gui.line.rectangle(  X+WIDTH-25, Y-barHeight+4, 20, barHeight-8)
            # Gui.line.rectangle(  X, Y, WIDTH, HEIGHT)

            Gui.X = window["x"]
            Gui.Y = window["y"] - scroll_value
            Gui.WIDTH = window["width"]
            Gui.HEIGHT = window["height"]
            Gui.fill.set_color(WHITE)
            Gui.line.set_color(WHITE)
            Gui.sprites.set_color(WHITE)
            Gui.font.set_color(WHITE)
        

            return scroll_value

        @staticmethod
        def end():
            Gui.isBegin = False
        
            
   

            

            

        @staticmethod
        def button(x, y, w, h, label):
            if not Gui.isBegin :
                print("widgets must be called between Begin() and End()")
                return
            if not Gui.visible :
                return

            Gui.ID += 1

            X = Gui.X + x   
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
            isPressed = False
            if isOver and Input.mouse_down(0) and  Gui._can_process():
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
            if not Gui.visible:
                return

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y

            Gui.font.set_size(Gui.theme.fontSize)
            WIDTH  = Gui.font.get_text_width(label)
            HEIGHT = Gui.font.get_max_width()

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()

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
          
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return
            if not Gui.visible:
                return
          

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
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, size, size) and Gui._can_process()
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
                Render.set_cursor("hand")
            
                
            
  
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
            isOver = point_in_rect(mouse_x, mouse_y, X + slider_pos - (HEIGHT // 2), Y, HEIGHT, HEIGHT) and Gui._can_process()  


    
            if isOver:
                Gui.fill.set_color(Gui.theme.sliderFillColor)
            else:
                Gui.fill.set_color(Gui.theme.sliderFillColorOff)


            Gui.fill.rectangle(X + slider_pos - (HEIGHT // 2)+8, Y, 8, HEIGHT-2)


            isInBound = point_in_rect(mouse_x, mouse_y, X , Y, WIDTH, HEIGHT+5) and Gui._can_process()


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
            isInBound = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()



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
            isOver = point_in_rect(mouse_x, mouse_y, X, Y + slider_pos - (WIDTH // 2), WIDTH, WIDTH) and Gui._can_process()

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
            isOver = point_in_rect(mouse_x, mouse_y, X, Y + slider_pos - (WIDTH // 2), WIDTH, WIDTH) and Gui._can_process()


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
                return (value , False)
            if not Gui.visible:
                return (value , False)

            Gui.ID += 1

            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h
            radius = min(WIDTH, HEIGHT) * 0.5

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X - (WIDTH * 0.5), Y - (HEIGHT * 0.5), WIDTH, HEIGHT) and Gui._can_process()
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
                return (labels, False)
            if not Gui.visible:
                return (labels, False)

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
            if not Gui.visible:
                return

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
            if not Gui.visible:
                return

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
            if not Gui.visible:
                return

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
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
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
                return (-1, False,scroll_value)
            if not Gui.visible:
                return (-1, False,scroll_value)

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
                
                onItem = point_in_rect(mouse_x, mouse_y, X, Y + (item_y-10) - (item_height//2), WIDTH-12, item_height) and Gui._can_process()
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
                
            
                onScroll = point_in_rect(mouse_x, mouse_y, X + w - 10, scrollbar_y, 20, scrollbar_height) and Gui._can_process()
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

            Gui.ID += 1

            X = Gui.X + x   
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
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
                print("widgets must be between 'begin' and 'end'")
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
    
        @staticmethod
        def input_text(x, y, w, h, options=None):
            if not Gui.isBegin:
                    print("widgets must be between 'begin' and 'end'")
                    return False
                
            if not Gui.visible:
                    return False
            
            if options is None:
                options = {"text":"","select":False, "password":False, "multiline":False}

            Gui.ID += 1
            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h
            selected = options.get("select", False)
            text = options.get("text", "")
  
            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
            if isOver and Input.mouse_pressed(0):
                Gui.FocusId = Gui.ID-1  
                options["select"] = True

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)
            Gui.font.set_color(Gui.theme.fontOverColor)
            Gui.font.set_size(Gui.theme.fontOverSize)

                    

            if selected and not isOver and Input.mouse_down(0) :    
                options["select"] = False

            if selected or isOver:
                Gui.line.set_color(Gui.theme.overColor)
                Gui.line.rectangle(X-1, Y-1, WIDTH+2, HEIGHT+2)
            

            #clip = Gui.font.get_clip()
            #Gui.font.set_clip(X, Y, WIDTH, HEIGHT)
            code = ""
            isPassword =False

 

            #if options.get("multiline", False):
            #    text = text.replace("\n", "↵")

            Gui.font.set_allign(TextAlign.Left)
            offY = Y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)

            cursorX = X + Gui.font.get_text_width(text)
            if cursorX > X + WIDTH -2: 
                cursorX = X + WIDTH -2

            if selected and Input.keyboard_any():
                key = Input.keyboard_last_key()
                char = Input.keyboard_last_char()
                if key == glfw.KEY_SPACE and cursorX < (X + WIDTH) - 4:
                    text += " "
                if key == glfw.KEY_DELETE: 
                    if len(text) > 0:
                        text = text[:-1]
                if key == glfw.KEY_BACKSPACE:
                    if len(text) > 0:
                        text = text[:-1]
                if key == glfw.KEY_ENTER:
                    options["select"] = False
                    options["text"] = text
                    return selected
                if ((key>= 32 and key <= 126) and char is not None) and cursorX < (X + WIDTH) - 4:
                        text += char

            if options.get("password", False):
                code = "*" * len(text) +1
                isPassword = True
            if isPassword:
                Gui.font.write(X, offY, code)
            else:
                Gui.font.write(X, offY, text)

            if selected:
                Gui.fill.set_color(Gui.theme.backgroundColor)
                blink = int(time.time() * 500) % 500 > 250
                if blink:
                    Gui.fill.set_color(Gui.theme.editCursorColor)
                Gui.fill.rectangle(cursorX-1, Y, 4, HEIGHT)
            else:
                Gui.fill.set_color(Gui.theme.editCursorColor)
                Gui.fill.rectangle(cursorX-1, Y, 4, HEIGHT)
                

            #Gui.font.set_clip(clip.x, clip.y, clip.width, clip.height)
            options["text"] = text
            return selected
        
        @staticmethod
        def input_numeric(x, y, w, h, options=None):
            if not Gui.isBegin:
                    print("widgets must be between 'begin' and 'end'")
                    return False
                
            if not Gui.visible:
                    return False
            
            if options is None:
                options = {"text":"","select":False}

            Gui.ID += 1
            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH = w
            HEIGHT = h
            selected = options.get("select", False)
            text = options.get("text", "")

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
            if isOver and Input.mouse_pressed(0):
                Gui.FocusId = Gui.ID-1  
                options["select"] = True

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)
            Gui.font.set_color(Gui.theme.fontOverColor)
            Gui.font.set_size(Gui.theme.fontOverSize)

                    

            if selected and not isOver and Input.mouse_down(0) :    
                options["select"] = False

            if selected or isOver:
                Gui.line.set_color(Gui.theme.overColor)
                Gui.line.rectangle(X-1, Y-1, WIDTH+2, HEIGHT+2)
            

            clip = Gui.font.get_clip()
            #Gui.font.set_clip(X, Y, WIDTH, HEIGHT)

            Gui.font.set_allign(TextAlign.Left)
            offY = Y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)

            cursorX = X + Gui.font.get_text_width(text)
            if cursorX > X + WIDTH -2: 
                cursorX = X + WIDTH -2

            if selected and Input.keyboard_any():
                key = Input.keyboard_last_key()
                char = Input.keyboard_last_char()
                if key == glfw.KEY_SPACE and cursorX < (X + WIDTH) - 4:
                    text += " "
                if key == glfw.KEY_DELETE: 
                    if len(text) > 0:
                        text = text[:-1]
                if key == glfw.KEY_BACKSPACE:
                    if len(text) > 0:
                        text = text[:-1]
                if key == glfw.KEY_ENTER:
                    options["select"] = False
                    options["text"] = text
                    return selected
    
                if key >= 48 and key <= 57:
                    text += char
     
            Gui.font.write(X, offY, text)

            if selected:
                Gui.fill.set_color(Gui.theme.backgroundColor)
                blink = int(time.time() * 500) % 500 > 250
                if blink:
                    Gui.fill.set_color(Gui.theme.editCursorColor)
                Gui.fill.rectangle(cursorX-1, Y, 4, HEIGHT)
            else:
                Gui.fill.set_color(Gui.theme.editCursorColor)
                Gui.fill.rectangle(cursorX-1, Y, 4, HEIGHT)
                

            #Gui.font.set_clip(clip.x, clip.y, clip.width, clip.height)
            options["text"] = text
            return selected
        
        @staticmethod
        def spin(x, y, w, h, min_value,max_value,value,force=1):
            if not Gui.isBegin:
                    print("widgets must be between 'begin' and 'end'")
                    return value
                
            if not Gui.visible:
                    return value
     


            Gui.ID += 1
            X = Gui.X + x
            Y = Gui.Y + y
            WIDTH  = w - 20
            HEIGHT = h


            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
            if isOver and Input.mouse_pressed(0):
                Gui.FocusId = Gui.ID-1  
        
            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect(mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
            if isOver and Input.mouse_pressed(0):
                Gui.FocusId = Gui.ID-1  


            top    = Gui._dummy_button(WIDTH + x +1, y, 20, HEIGHT//2-1)
            bottom = Gui._dummy_button(WIDTH + x+1, y + HEIGHT//2, 20, HEIGHT//2)
            if top :
                value += force
            if bottom :
                value -= force
                
            if value < min_value:
                value = min_value
            if value > max_value:
                value = max_value

            Gui.fill.set_color(Gui.theme.backgroundColor)
            Gui.fill.rectangle(X, Y, WIDTH, HEIGHT)
            Gui.font.set_color(Gui.theme.fontOverColor)
            Gui.font.set_size(Gui.theme.fontOverSize)

                    


            if isOver:
                Gui.line.set_color(Gui.theme.overColor)
                Gui.line.rectangle(X-1, Y-1, WIDTH+2, HEIGHT+2)
            

            clip = Gui.font.get_clip()
            Gui.font.set_clip(X, Y, WIDTH, HEIGHT)

            Gui.font.set_allign(TextAlign.Left)
            offY = Y +(HEIGHT * 0.5) - (Gui.font.maxHeight *0.5)

            text = str(value)

            cursorX = X + Gui.font.get_text_width(text)
            if cursorX > X + WIDTH -2: 
                cursorX = X + WIDTH -2

            if isOver and Input.keyboard_any():
                key = Input.keyboard_last_key()
                char = Input.keyboard_last_char()

                if key == glfw.KEY_DELETE: 
                   value = 0
                   text = "0"
                if key == glfw.KEY_BACKSPACE:
                    value = 0
                    text = "0"

    
                if (key >= 48 and key <= 57) and cursorX < (X + WIDTH) - 4:
                    text += char
            
            if len(text) > 0: 
                value = int(text)
            Gui.font.write(X, offY, text)
                

            #Gui.font.set_clip(clip.x, clip.y, clip.width, clip.height)

            return value
        @staticmethod
        def _dummy_button(x, y, w, h):

            Gui.ID += 1

            X = Gui.X + x   
            Y = Gui.Y + y
            WIDTH  = w
            HEIGHT = h

            mouse_x = Input.get_mouse_x()
            mouse_y = Input.get_mouse_y()
            isOver = point_in_rect( mouse_x, mouse_y, X, Y, WIDTH, HEIGHT) and Gui._can_process()
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
    
                Gui.FocusId = Gui.ID-1



                    
        

            if isOver and Input.mouse_released(0):
                isPressed = False


            return isPressed                    
        


        @staticmethod
        def memo(x, y, w, h, items, scroll_value):
            if not Gui.isBegin:
                print("widgets must be called between Begin() and End()")
                return (-1, False,scroll_value)
            if not Gui.visible:
                return (-1, False,scroll_value)

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
                
                onItem = point_in_rect(mouse_x, mouse_y, X, Y + (item_y-10) - (item_height//2), WIDTH-12, item_height) and Gui._can_process()
                if onItem or selected == start_index + i:
                     if Input.mouse_down(0):
                        selected = start_index + i
                        isDown = True
                    
         
                
                Gui.text(X + 1, (Y + item_y)-(item_height//2), item_label)  # Ajuste do label dentro do item


            # Desenhar a barra de scroll se houver mais itens do que espaço
            if len(items) > visible_items:
                scrollbar_height = int((visible_items / len(items)) * HEIGHT)
                scrollbar_y = Y + (scroll_value / max_scroll) * (HEIGHT - scrollbar_height)
                
            
                onScroll = point_in_rect(mouse_x, mouse_y, X + w - 10, scrollbar_y, 20, scrollbar_height) and Gui._can_process()
                if onScroll:
                    Gui.fill.set_color(WHITE) 
                else:
                    Gui.fill.set_color(Gui.theme.backgroundColor)  


                Gui.fill.rectangle(X + w - 10, scrollbar_y, 10, scrollbar_height)


                if onScroll and Input.mouse_down(0):
                    new_scroll_value = ((mouse_y - Y) / HEIGHT) * max_scroll
                    scroll_value = max(0, min(new_scroll_value, max_scroll))

            return (selected, isDown, scroll_value)