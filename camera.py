import glm
import math

class Camera:
    def __init__(self, position=glm.vec3(0.0, 0.0, 3.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0):
        self.position = position
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.movement_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.zoom = 45.0

        self.update()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def mode_front(self,  delta_time):
        velocity = self.movement_speed * delta_time
        self.position += self.front * velocity

    def mode_back(self,  delta_time):
        velocity = self.movement_speed * delta_time
        self.position -= self.front * velocity
       
    def mode_left(self,  delta_time):
        velocity = self.movement_speed * delta_time
        self.position -= self.right * velocity

    def mode_right(self,  delta_time):    
        velocity = self.movement_speed * delta_time
        self.position += self.right * velocity

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update()

    def process_mouse_scroll(self, y_offset):
        if self.zoom >= 1.0 and self.zoom <= 45.0:
            self.zoom -= y_offset
        if self.zoom <= 1.0:
            self.zoom = 1.045
        if self.zoom >= 45.0:
            self.zoom = 45.0

    def update(self):
        front = glm.vec3()
        front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        front.y = math.sin(glm.radians(self.pitch))
        front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up)) 
        self.up = glm.normalize(glm.cross(self.right, self.front))

