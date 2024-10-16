from enum import Enum
class Mouse:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.wheel = 0
        self.wheelDelta = 0

class Input:
    def __init__(self):
        self.currentKeyState = [False] * 512
        self.previousKeyState = [False] * 512
        self.currentButtonState = [False] * 8
        self.previousButtonState = [False] * 8
        self.lastChar = 0
        self.lastKey = 0
        self.mouse = Mouse()
        self.lastX = 0
        self.lastY = 0
        self.lastZ = 0
    
    def set_key_state(self, key, state):
        self.currentKeyState[key] = state
        self.lastKey = key
        self.lastChar = str(key)  

    def set_mouse_state(self, button, state):
        self.currentButtonState[button] = state

    def set_mouse_wheel(self, x, y):
        self.mouse.wheel = y
        self.mouse.wheelDelta = y - self.lastZ
        self.lastZ = y
        
    def set_mouse_cursor(self, x, y,w,h):
        self.mouse.x = x
        self.mouse.y = y
        self.mouse.dx = (x - self.lastX)  / w  
        self.mouse.dy = (y - self.lastY)  / h


        self.mouse.dx = max(-1, min(1, self.mouse.dx))
        self.mouse.dy = max(-1, min(1, self.mouse.dy))
        self.lastX = x
        self.lastY = y 

    def update(self):
        self.previousButtonState = self.currentButtonState[:]
        self.previousKeyState = self.currentKeyState[:]
        self.mouse.dx = 0
        self.mouse.dy = 0

    def keyboard_check(self, key):
       return self.currentKeyState[key] and not self.previousKeyState[key]
        

    def keyboard_down(self, key):
        value = self.currentKeyState[key]
        if value:
            return 1
        else:
            return 0

    def keyboard_up(self, key):
        return not self.currentKeyState[key]
    
    def keyboard_pressed(self, key):
        return not self.previousKeyState[key] and self.currentKeyState[key]

    def keyboard_released(self, key):
        return self.previousKeyState[key] and not self.currentKeyState[key]

    def mouse_check(self, button):
       return self.currentButtonState[button] and not self.previousButtonState[button]
      

    def mouse_down(self, button):
        value = self.currentButtonState[button]
        if value:
            return 1
        else:
            return 0
    def mouse_up(self, button):
        return not self.currentButtonState[button]

    def mouse_pressed(self, button):
        return not self.previousButtonState[button] and self.currentButtonState[button]

    def mouse_released(self, button):
        return self.previousButtonState[button] and not self.currentButtonState[button]
    
    def get_mouse_delta_x(self):
        return self.mouse.dx

    def get_mouse_delta_y(self):
        return self.mouse.dy
    
    def get_mouse_x(self):
        return self.mouse.x
    
    def get_mouse_y(self):
        return self.mouse.y


class Key(Enum):
     A = 65,
     B = 66,
     C = 67,  
     D = 68,
     E = 69,
     F = 70,
     G = 71,
     H = 72,
     I = 73,
     J = 74,
     K = 75,
     L = 76,
     M = 77,
     N = 78,
     O = 79,
     P = 80,
     Q = 81,
     R = 82,
     S = 83,
     T = 84,
     U = 85,
     V = 86,
     W = 87,
     X = 88,
     Y = 89,
     Z = 90,
     Num0 = 48,
     Num1 = 49,
     Num2 = 50,
     Num3 = 51,
     Num4 = 52,
     Num5 = 53,
     Num6 = 54,
     Num7 = 55,
     Num8 = 56,
     Num9 = 57,
     Space = 32,
     Enter = 13,
     Shift = 16,
     Control = 17,
     Alt = 18,
     CapsLock = 20,
     Tab = 9,
     Escape = 27,
     ArrowLeft = 37,
     ArrowUp = 38,
     ArrowRight = 39,
     ArrowDown = 40,
     F1 = 112,
     F2 = 113,
     F3 = 114,
     F4 = 115,
     F5 = 116,
     F6 = 117,
     F7 = 118,
     F8 = 119,
     F9 = 120,
     F10 = 121,
     F11 = 122,
     F12 = 123,
     Numpad0 = 96,
     Numpad1 = 97,
     Numpad2 = 98,
     Numpad3 = 99,
     Numpad4 = 100,
     Numpad5 = 101,
     Numpad6 = 102,
     Numpad7 = 103,
     Numpad8 = 104,
     Numpad9 = 105,
     NumpadAdd = 107,
     NumpadSubtract = 109,
     NumpadDivide = 111,
     NumpadMultiply = 106,
     NumpadDecimal = 110,
     NumpadEnter = 13,
     Backspace = 8,
     Delete = 46,
     Home = 36,
     End = 35,
     Insert = 45,
     PageUp = 33,
     PageDown = 34,
     PrintScreen = 44,
     ScrollLock = 145,
     Pause = 19,
     Meta = 91,
     ContextMenu = 93,
     NumLock = 144,
     AudioVolumeMute = 181,
     AudioVolumeDown = 182,
     AudioVolumeUp = 183,
     MediaTrackNext = 176,
     MediaTrackPrevious = 177,
     MediaStop = 178,
     MediaPlayPause = 179,
     BrowserHome = 172,