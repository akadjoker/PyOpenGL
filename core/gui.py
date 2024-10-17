
from core.input import Input
from core.core import *
from core.batch import *
from core.font import Font
from core.sprite import SpriteBatch
from core.color import Color



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
        self.fontOverSize = 20
        self.fontSize = 18

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

DEFAULT_COUNT = 1024

class Gui:
        count = 1024
        line   =  LinesBatch(DEFAULT_COUNT)
        fill    =  FillBatch(DEFAULT_COUNT)
        sprites =  SpriteBatch(DEFAULT_COUNT)
        font    =  Font(512)
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
        theme = Theme()
        window = Window()
    
        @staticmethod
        def init(font_path,texture):
            Gui.font.load(font_path,texture)
        
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
            background = options.get('background', False) 
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
            Gui.line.set_clip(X, Y, WIDTH, HEIGHT)
            Gui.fill.set_clip(X, Y, WIDTH, HEIGHT)
            Gui.font.set_clip(X, Y, WIDTH, HEIGHT)

        @staticmethod
        def end():
            Gui.isBegin = False

