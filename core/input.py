from enum import Enum
from enum import Enum

class Mouse:
    x = 0
    y = 0
    dx = 0
    dy = 0
    wheel = 0
    wheel_delta = 0

class Input:
    current_key_state = [False] * 512
    previous_key_state = [False] * 512
    current_button_state = [False] * 8
    previous_button_state = [False] * 8
    last_char = 0
    last_key = 0
    mouse = Mouse()
    last_x = 0
    last_y = 0
    last_z = 0
    is_any_key_down = False

    @staticmethod
    def set_key_state(key, state,chars):
        Input.current_key_state[key] = state
        Input.last_key = key
        Input.last_char = chars
        Input.is_any_key_down = (state == True)

    @staticmethod
    def set_mouse_state(button, state):
        Input.current_button_state[button] = state

    @staticmethod
    def set_mouse_wheel(x, y):
        Input.mouse.wheel = y
        Input.mouse.wheel_delta = y - Input.last_z
        Input.last_z = y
        
    @staticmethod
    def set_mouse_cursor(x, y, w, h):
        Input.mouse.x = x
        Input.mouse.y = y
        Input.mouse.dx = (x - Input.last_x) / w  
        Input.mouse.dy = (y - Input.last_y) / h
        

        Input.mouse.dx = max(-1, min(1, Input.mouse.dx))
        Input.mouse.dy = max(-1, min(1, Input.mouse.dy))
        Input.last_x = x
        Input.last_y = y 

    @staticmethod
    def update():
        Input.previous_button_state = Input.current_button_state[:]
        Input.previous_key_state = Input.current_key_state[:]
        Input.mouse.dx = 0
        Input.mouse.dy = 0
        Input.mouse.wheel_delta = 0
        Input.is_any_key_down = False
        Input.last_key = 0

    @staticmethod
    def keyboard_check(key):
        return Input.current_key_state[key] and not Input.previous_key_state[key]
        
    @staticmethod
    def keyboard_down(key):
        return 1 if Input.current_key_state[key] else 0

    @staticmethod
    def keyboard_up(key):
        return not Input.current_key_state[key]
    
    @staticmethod
    def keyboard_pressed(key):
        return not Input.previous_key_state[key] and Input.current_key_state[key]

    @staticmethod
    def keyboard_released(key):
        return Input.previous_key_state[key] and not Input.current_key_state[key]
    
    @staticmethod
    def keyboard_last_char():
        return Input.last_char
    
    @staticmethod
    def keyboard_last_key():
        return Input.last_key


    @staticmethod
    def keyboard_any():
        return Input.is_any_key_down


    @staticmethod
    def mouse_check(button):
        return Input.current_button_state[button] and not Input.previous_button_state[button]
      
    @staticmethod
    def mouse_down(button):
        return 1 if Input.current_button_state[button] else 0

    @staticmethod
    def mouse_up(button):
        return not Input.current_button_state[button]

    @staticmethod
    def mouse_pressed(button):
        return not Input.previous_button_state[button] and Input.current_button_state[button]

    @staticmethod
    def mouse_released(button):
        return Input.previous_button_state[button] and not Input.current_button_state[button]
    
    @staticmethod
    def get_mouse_delta_x():
        return Input.mouse.dx

    @staticmethod
    def get_mouse_delta_y():
        return Input.mouse.dy
    
    @staticmethod
    def get_mouse_x():
        return Input.mouse.x
    
    @staticmethod
    def get_mouse_y():
        return Input.mouse.y


