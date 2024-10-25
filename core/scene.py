
import glm
import math
from core.render import *
from core.utils import BoundingBox, Plane3D, Ray3D, Frustum , UtilMath
from core.builder import *
from core.material import *
from core.shader import *

dtor = math.pi / 180.0  # Graus para radianos
rtod = 180.0 / math.pi  # Radianos para graus
PI = math.pi
TWOPI = 2 * math.pi

# Rotação com quaternions para pitch, yaw, roll
def rotationQuat(p, y, r):
    pitch = glm.angleAxis(p, glm.vec3(1, 0, 0))  
    yaw = glm.angleAxis(y, glm.vec3(0, 1, 0))   
    roll = glm.angleAxis(r, glm.vec3(0, 0, 1))   
    return pitch * yaw * roll

def lerp(a, b, t):
    return a * (1 - t) + b * t

# Extração de Yaw, Pitch e Roll de quaternions
def quatPitch(q):
    return glm.degrees(glm.pitch(q))

def quatYaw(q):
    return glm.degrees(glm.yaw(q))

def quatRoll(q):
    return glm.degrees(glm.roll(q))

class Transform:
    def __init__(self, position=glm.vec3(0.0), scale=glm.vec3(1.0), rotation=glm.quat()):
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.matrix = glm.mat4(1.0)

    def update_matrix(self):
        translation_matrix = glm.translate(glm.mat4(1.0), self.position)
        rotation_matrix = glm.mat4_cast(self.rotation)
        scale_matrix = glm.scale(glm.mat4(1.0), self.scale)
        self.matrix = translation_matrix * rotation_matrix * scale_matrix


class Entity:
    INVALID_LOCALTFORM = 1
    INVALID_WORLDTFORM = 2

    def __init__(self):
        self.local_pos = glm.vec3(0.0)
        self.local_scl = glm.vec3(1.0)
        self.local_rot = glm.quat()

        self.local_tform = Transform(self.local_pos, self.local_scl, self.local_rot)
        self.world_tform = Transform()
        self.world_scl = glm.vec3(1.0)
        self.world_rot = glm.quat()

        self.invalid = self.INVALID_LOCALTFORM | self.INVALID_WORLDTFORM

        self._parent = None
        self._children = []
        self.visible = True
        self.active = True

    def render(self):
        pass

    def update(self):
        pass

    def animate(self,time):
        pass

    # Métodos para definir transformações locais
    def set_local_position(self, v):
        self.local_pos = v
        self.invalidate_local()

    def set_local_scale(self, v):
        self.local_scl = v
        self.invalidate_local()

    def set_local_rotation(self, q):
        self.local_rot = glm.normalize(q)
        self.invalidate_local()

    def set_local_tform(self, t):
        self.local_pos = t.position
        self.local_scl = t.scale
        self.local_rot = t.rotation
        self.invalidate_local()

    # Métodos para definir transformações globais
    def set_world_position(self, v):
        if self._parent:
            inverse_world = glm.inverse(self._parent.get_world_tform().matrix)
            local_pos = glm.vec3(inverse_world * glm.vec4(v, 1.0))
            self.set_local_position(local_pos)
        else:
            self.set_local_position(v)

    def set_world_scale(self, v):
        if self._parent:
            parent_scale = self._parent.get_world_scale()
            local_scale = v / parent_scale
            self.set_local_scale(local_scale)
        else:
            self.set_local_scale(v)

    def set_world_rotation(self, q):
        if self._parent:
            parent_rotation = glm.inverse(self._parent.get_world_rotation())
            local_rotation = parent_rotation * q
            self.set_local_rotation(local_rotation)
        else:
            self.set_local_rotation(q)

    def set_world_tform(self, t):
        if self._parent:
            parent_transform = glm.inverse(self._parent.get_world_tform().matrix)
            local_transform = parent_transform * t.matrix
            self.set_local_tform(Transform(local_transform))
        else:
            self.set_local_tform(t)

    # Métodos para obter transformações locais
    def get_local_rotation_vector(self):
        euler_angles = glm.eulerAngles(self.local_rot)
        euler_angles_degrees = glm.degrees(euler_angles)
        return euler_angles

    def get_local_x(self):
        return self.local_pos.x
    def get_local_y(self):
        return self.local_pos.y
    def get_local_z(self):
        return self.local_pos.z
    
    def set_local_x(self, x):
        self.local_pos.x = x
        self.invalidate_local()
    def set_local_y(self, y):
        self.local_pos.y = y
        self.invalidate_local()
    def set_local_z(self, z):
        self.local_pos.z = z
        self.invalidate_local()

    def get_local_position(self):
        return self.local_pos

    def get_local_scale(self):
        return self.local_scl

    def get_local_rotation(self):
        return self.local_rot

    def get_local_tform(self):
        if self.invalid & self.INVALID_LOCALTFORM:
            self.local_tform.position = self.local_pos
            self.local_tform.scale = self.local_scl
            self.local_tform.rotation = self.local_rot
            self.local_tform.update_matrix()
            self.invalid &= ~self.INVALID_LOCALTFORM
        return self.local_tform

    # Métodos para obter transformações globais
    def get_world_position(self):
        return self.get_world_tform().position

    def get_world_scale(self):
        if self._parent:
            return self._parent.get_world_scale() * self.local_scl
        return self.local_scl

    def get_world_rotation(self):
        if self._parent:
            return self._parent.get_world_rotation() * self.local_rot
        return self.local_rot
    

    def get_world_tform(self):
        if self.invalid & self.INVALID_WORLDTFORM:
            if self._parent:
                parent_tform = self._parent.get_world_tform()
                self.world_tform.matrix = parent_tform.matrix * self.get_local_tform().matrix
            else:
                self.world_tform = self.get_local_tform()
            self.invalid &= ~self.INVALID_WORLDTFORM
        return self.world_tform
    
    def get_front(self):
        return self.get_world_rotation() * glm.vec3(0.0, 0.0, -1.0)
    
    def get_right(self):
        return self.get_world_rotation() * glm.vec3(1.0, 0.0, 0.0)

    # Invalida transformações
    def invalidate_local(self):
        self.invalid |= self.INVALID_LOCALTFORM
        self.invalidate_world()

    def invalidate_world(self):
        self.invalid |= self.INVALID_WORLDTFORM
        for child in self._children:
            child.invalidate_world()

    # Métodos de hierarquia
    def set_parent(self, parent):
        if self._parent == parent:
            return
        if self._parent:
            self._parent._children.remove(self)
        self._parent = parent
        if self._parent:
            self._parent._children.append(self)
        self.invalidate_world()

    # Visibilidade e habilitação
    def set_visible(self, visible):
        self._visible = visible

    def set_enabled(self, enabled):
        self._enabled = enabled

    def enum_visible(self, out):
        if not self._visible:
            return
        out.append(self)
        for child in self._children:
            child.enum_visible(out)

    def enum_enabled(self, out):
        if not self._enabled:
            return
        out.append(self)
        for child in self._children:
            child.enum_enabled(out)

    ### MÉTODOS DE TRANSFORMAÇÃO  ###
    def move(self, x, y, z):
        self.set_local_position(self.get_local_position() + self.get_local_rotation() * glm.vec3(x, y, z))


    def turn(self, p, y, r, global_space=False):
        quat_rotation = glm.quat(glm.vec3(glm.radians( p), glm.radians(y),  glm.radians(r)))
        if global_space:
            self.set_world_rotation(quat_rotation * self.get_world_rotation())
        else:
            self.set_local_rotation(self.get_local_rotation() * quat_rotation)

    def rotate(self, p, y, r, global_space=False):
        quat_rotation = glm.quat(glm.vec3(glm.radians( p), glm.radians(y),  glm.radians(r)))
        if global_space:
            self.set_world_rotation(quat_rotation)
        else:
            self.set_local_rotation(quat_rotation)

    def translate(self, x, y, z, global_space=False):
        if global_space:
            self.set_world_position(self.get_world_position() + glm.vec3(x, y, z))
        else:
            self.set_local_position(self.get_local_position() + glm.vec3(x, y, z))


    def position(self, x, y, z, global_space=False):
        if global_space:
            self.set_world_position(glm.vec3(x, y, z))
        else:
            self.set_local_position(glm.vec3(x, y, z))


    def scale(self, x, y, z, global_space=False):
        if global_space:
            self.set_world_scale(glm.vec3(x, y, z))
        else:
            self.set_local_scale(glm.vec3(x, y, z))




    def point(self, target, roll=0):
        v = target.get_world_tform().position - self.get_world_tform().position
        pitch = glm.atan(v.y, glm.length(glm.vec2(v.x, v.z)))  # Inclinação (pitch)
        yaw = glm.atan(v.x, v.z)  # Direção (yaw)
        roll = glm.radians(roll)
        quat_rotation = glm.quat(glm.vec3(pitch, yaw, roll))
        self.set_world_rotation(quat_rotation)


    def look_at(self, target_position):
        direction = glm.normalize(target_position - self.get_world_position())
        rotation = glm.quatLookAt(direction, glm.vec3(0, 1, 0))  # Assume o eixo Y como 'up'
        self.set_world_rotation(rotation)

    def orbit(self, target_position, radius, speed, axis=glm.vec3(0, 1, 0)):
        angle = speed * glm.radians(1)  
        rotation = glm.angleAxis(angle, axis)
        direction_to_target = glm.normalize(self.get_world_position() - target_position)
        new_position = target_position + (rotation * direction_to_target) * radius
        
        self.set_world_position(new_position)


    def lerp_position(self, target_position, t):
        new_position = lerp(self.get_local_position(), target_position, t)
        self.set_local_position(new_position)

    def lerp_rotation(self, target_rotation, t):
        new_rotation = glm.slerp(self.get_local_rotation(), target_rotation, t)
        self.set_local_rotation(new_rotation)
    ### MÉTODOS PARA PROPRIEDADES GLOBAIS E LOCAIS ###

    def x(self, global_space=False):
        return self.get_world_position().x if global_space else self.get_local_position().x

    def y(self, global_space=False):
        return self.get_world_position().y if global_space else self.get_local_position().y

    def z(self, global_space=False):
        return self.get_world_position().z if global_space else self.get_local_position().z

    def pitch(self, global_space=False):
        rotation = self.get_world_rotation() if global_space else self.get_local_rotation()
        return quatPitch(rotation)

    def yaw(self, global_space=False):
        rotation = self.get_world_rotation() if global_space else self.get_local_rotation()
        return quatYaw(rotation)

    def roll(self, global_space=False):
        rotation = self.get_world_rotation() if global_space else self.get_local_rotation()
        return quatRoll(rotation)

  
    ### TRANSFORMAÇÃO DE PONTOS, VETORES E NORMAIS ###

    def transform_point(self, x, y, z, src, dest):
        tformed = glm.vec3(x, y, z)
        if src:
            tformed = src.get_world_tform().matrix * glm.vec4(tformed, 1.0)
        if dest:
            tformed = glm.inverse(dest.get_world_tform().matrix) * glm.vec4(tformed, 1.0)
        return tformed

    def transform_vector(self, x, y, z, src, dest):
        tformed = glm.vec3(x, y, z)
        if src:
            tformed = src.get_world_tform().matrix * glm.vec4(tformed, 0.0)
        if dest:
            tformed = glm.inverse(dest.get_world_tform().matrix) * glm.vec4(tformed, 0.0)
        return tformed

    def transform_normal(self, x, y, z, src, dest):
        tformed = glm.vec3(x, y, z)
        if src:
            tformed = glm.transpose(glm.inverse(src.get_world_tform().matrix)) * glm.vec4(tformed, 0.0)
        if dest:
            tformed = glm.transpose(glm.inverse(dest.get_world_tform().matrix)) * glm.vec4(tformed, 0.0)
        return glm.normalize(tformed)

    ### DIFERENÇAS ENTRE ENTIDADES ###

    def delta_angle(self, target):
        return glm.angle(self.get_world_rotation(), target.get_world_rotation())

    def delta_distance(self, target):
        return glm.length(target.get_world_tform().position - self.get_world_tform().position)

    def delta_yaw(self, target):
        current_yaw = glm.degrees(glm.atan(self.get_world_tform().matrix[2].x, self.get_world_tform().matrix[2].z))
        target_yaw = glm.degrees(glm.atan((target.get_world_position().x - self.get_world_position().x),
                                          (target.get_world_position().z - self.get_world_position().z)))
        delta = target_yaw - current_yaw
        if delta < -PI:
            delta += TWOPI
        elif delta >= PI:
            delta -= TWOPI
        return delta

    def delta_pitch(self, target):

        current_pitch = glm.degrees(glm.atan(self.get_world_tform().matrix[2].y, glm.length(glm.vec2(self.get_world_tform().matrix[2].x, self.get_world_tform().matrix[2].z))))
        target_pitch = glm.degrees(glm.atan((target.get_world_position().y - self.get_world_position().y),
                                            glm.length(glm.vec2(target.get_world_position().x - self.get_world_position().x, target.get_world_position().z - self.get_world_position().z))))
        delta = target_pitch - current_pitch
        if delta < -PI:
            delta += TWOPI
        elif delta >= PI:
            delta -= TWOPI
        return delta
    

class Model (Entity):
    def __init__(self,name="Model"):
        super().__init__()    
        self.meshes = []
        self.name = name
        self.box = BoundingBox()
        self.boxTransform = BoundingBox()
        
        self.materials=[]
        self.numMaterials = 0
    
    def ray_intersects(self, ray):
        matrix = self.get_world_tform().matrix
        self.boxTransform = self.box.transform( matrix )
        if not ray.intersects_box(self.boxTransform) :
            return False
        for mesh in self.meshes:
            box = mesh.box.transform(matrix)
            if ray.intersects_box(box):
                #Render.linesBatch.draw_bounding_box(box, RED)
                if mesh.ray_intersects(ray, matrix):
                    return True
        return False
    

    def add_material(self, material):
        self.materials.append(material)
        self.numMaterials += 1
        
    def add_mesh(self, mesh):
        if self.numMaterials == 0:
            print("Model has no materials")
            return
        self.meshes.append(mesh)
        mesh.update()
        self.box.add(mesh.box)

    
    def get_bounding_box(self):
        return self.boxTransform
    
    def sort_by_material(self):
        self.meshes.sort(key=lambda mesh: mesh.material)
        

    def update(self):
        self.boxTransform = self.box.transform(self.get_world_tform().matrix)
    
    # def render(self):

    #     if self.numMaterials == 0:
    #         print("Model has no materials")
    #         return

    #     Render.set_shader(self.shader)
    #     self.shader.apply()
    #     if self.shader.contains(MAT_MODEL):
    #         self.shader.set_matrix4fv("uModel", glm.value_ptr(self.get_world_tform().matrix))

    #     if self.shader.contains(MAT_VIEW) and self.shader.contains(MAT_PROJECTION): 
    #         self.shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    #         self.shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))

    #     for mesh in self.meshes:
    #         box = mesh.box.transform(self.get_world_tform().matrix)
    #         if not Render.is_box_in_frustum(box):
    #             continue
    #         material_index = mesh.material
    #         if material_index >= self.numMaterials:
    #             print("Invalid material index")
    #             return
    #         material = self.materials[material_index]
    #         Render.render_mesh(mesh, material)

    def render(self,shader,useMaterials=True):

        if self.numMaterials == 0:
            print("Model has no materials")
            return

        if shader.contains(UNIFORM_MODEL) :
            shader.set_matrix4fv("uModel", glm.value_ptr(self.get_world_tform().matrix))
            

        for mesh in self.meshes:
            box = mesh.box.transform(self.get_world_tform().matrix)
            if not Render.is_box_in_frustum(box) and useMaterials:
                continue
            material_index = mesh.material
            if material_index >= self.numMaterials:
                print("Invalid material index")
                return
            if useMaterials:
                material = self.materials[material_index]
                Render.render_mesh(mesh, material)            
            else:
                material = self.materials[material_index]
                if material.castShadow:
                    Render.render_mesh_no_material(mesh)



    def debug(self,batch):
        for mesh in self.meshes:
            box = mesh.get_bounding_box()
            batch.draw_transform_bounding_box(box,GREEN,self.get_world_tform().matrix)
            batch.draw_bounding_box(self.box,RED)


class Camera(Entity):
    def __init__(self, fov=45.0, aspect_ratio=16/9, near_plane=0.1, far_plane=100.0):
        super().__init__()
        self.fov = fov  
        self.aspect_ratio = aspect_ratio 
        self.near_plane = near_plane  
        self.far_plane = far_plane 


        self.projection_matrix = glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near_plane, self.far_plane)


    def get_view_matrix(self):
        world_tform = self.get_world_tform().matrix
        return glm.inverse(world_tform)

    def set_perspective(self, fov, aspect_ratio, near_plane, far_plane):
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_plane = near_plane
        self.far_plane = far_plane
        self.projection_matrix = glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near_plane, self.far_plane)

    def set_orthographic(self, left, right, bottom, top, near_plane, far_plane):
        self.projection_matrix = glm.ortho(left, right, bottom, top, near_plane, far_plane)

    def get_projection_matrix(self):
        return self.projection_matrix
    
    def get_projection_view_matrix(self):
        return self.get_projection_matrix() * self.get_view_matrix()


class CameraFPS(Camera):
    def __init__(self, fov=45.0, aspect_ratio=16/9, near_plane=0.1, far_plane=100.0):
        super().__init__(fov, aspect_ratio, near_plane, far_plane)
        self.y = 0
        self.speed_x = 0
        self.speed_z = 0

    def move_forward(self, delta):
        self.speed_z -= delta

    def move_backward(self, delta):
        self.speed_z += delta

    def strafe_right(self, delta):
        self.speed_x += delta 

    def strafe_left(self, delta):
        self.speed_x -= delta

    def update(self,dt):

        self.y = self.get_local_y()
        self.speed_x *= 0.9
        self.speed_z *= 0.9
        self.move(self.speed_x, 0, self.speed_z)
        self.set_local_y(self.y)



class Camera2D:
    def __init__(self, width, height):
        self.position = glm.vec2(0.0, 0.0)  # Posição da câmera
        self.pivot = glm.vec2(0.0, 0.0)     # Pivô da câmera
        self.rotation = 0.0                 # Rotação da câmera (em rad)
        self.scale = glm.vec2(1.0, 1.0)   
        self.width = width                 
        self.height = height               
        self.view_matrix = glm.mat4(1.0)    # Matriz de visualização
        self.projection_matrix = glm.ortho(0.0, width, height, 0.0)  # Matriz ortográfica

    def update(self):
        m_origin = glm.translate(glm.mat4(1.0), glm.vec3(-self.position.x, -self.position.y, 0.0))
        m_rotation = glm.rotate(glm.mat4(1.0), self.rotation, glm.vec3(0.0, 0.0, 1.0))
        m_scale = glm.scale(glm.mat4(1.0), glm.vec3(self.scale.x, self.scale.y, 1.0))
        m_translation = glm.translate(glm.mat4(1.0), glm.vec3(self.pivot.x, self.pivot.y, 0.0))
        self.view_matrix = m_translation * m_rotation * m_scale * m_origin

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.projection_matrix = glm.ortho(0.0, width, height, 0.0)

    def get_view_matrix(self):
        return self.view_matrix
    
    def get_projection_matrix(self):
        return self.projection_matrix

    def get_combined_matrix(self):
        return self.projection_matrix * self.view_matrix

    def set_position(self, x, y):
        self.position = glm.vec2(x, y)

    def set_rotation(self, angle_degrees):
        self.rotation = glm.radians(angle_degrees)

    def set_scale(self, scale_x, scale_y):
        self.scale = glm.vec2(scale_x, scale_y)



class Scene:
    def __init__(self):
        self.nodes = []
        self.mainCamera = None
        self.lights = []

  
    def ray_intersects(self, ray):
        for node in self.nodes:
            if node.ray_intersects(ray):
                return True

        return False
  

    def create_ambient_light(self,color):
        light = AmbientLightData()
        light.ambient = color
        self.lights.append(light)
        return light

    def create_directional_light(self, color, direction):
        light = DirectionalLightData()
        light.specular = color
        light.direction = direction
        self.lights.append(light)
        return light

    def create_point_light(self, color, position):
        light = PointLightData()
        light.specular = color
        light.position = position
        self.lights.append(light)
        return light

    def create_spot_light(self, color, position, direction):
        light = SpotLightData()
        light.color = color
        light.position = position
        light.direction = direction
        self.lights.append(light)
        return light

    def get_light(self, index):
        return self.lights[index]

    
    def set_camera(self, camera):
        self.mainCamera = camera


    def get_model(self, index):
        return self.nodes[index]

    def create_model(self, name="Model"):
        model = Model(name)
        self.nodes.append(model)
        return model
    
    def create_terrain_block(self,texture_image_path, heightmap_image_path, stretch_size, max_height, max_vtx_block_size, debug_borders=False, name="Terrain"):
        model = Model(name)
        mesh = Builder.create_terrain_mesh(model,texture_image_path, heightmap_image_path, stretch_size, max_height, max_vtx_block_size, debug_borders)
        model.add_mesh(mesh)
        self.nodes.append(model)  
        return model




    def render(self,shader,material=True):
        Render.set_matrix(VIEW_MATRIX, self.mainCamera.get_view_matrix())
        Render.set_matrix(PROJECTION_MATRIX, self.mainCamera.get_projection_matrix())
        if shader.contains(UNIFORM_CAMERA):
            shader.set_vector3f("viewPos", self.mainCamera.get_local_position())
        if shader.contains(UNIFORM_VIEW) or shader.contains(UNIFORM_PROJECTION):
            shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
            shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
        for node in self.nodes:
            if node.visible:
                box = node.get_bounding_box()
                if not material:#in shadow still need to render
                    node.render(shader,False)
                elif Render.is_box_in_frustum(box):
                    node.render(shader,True)

    def render_light(self,light,material=True):
        Render.set_matrix(VIEW_MATRIX, self.mainCamera.get_view_matrix())
        Render.set_matrix(PROJECTION_MATRIX, self.mainCamera.get_projection_matrix())
       
        shader = light.shader
        Render.set_shader(shader)
        light.update()
        if shader.contains(UNIFORM_CAMERA):
            shader.set_vector3f("viewPos", self.mainCamera.get_local_position())

        if shader.contains(UNIFORM_VIEW) or shader.contains(UNIFORM_PROJECTION):
            shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
            shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
        for node in self.nodes:
            if node.visible:
                box = node.get_bounding_box()
                if Render.is_box_in_frustum(box):
                    node.render(shader,material)

    def render_forward(self):
        Render.set_matrix(VIEW_MATRIX, self.mainCamera.get_view_matrix())
        Render.set_matrix(PROJECTION_MATRIX, self.mainCamera.get_projection_matrix())
        light = self.get_light(0)
        self.render_light(light,True)
        Render.set_blend(True)
        Render.set_blend_mode(BlendMode.One)
        glDepthMask(False)
        glDepthFunc(GL_EQUAL)

        for i in range(1,len(self.lights)):
            light = self.get_light(i)
            if not light.enable:
                continue
            light.camera = self.mainCamera.get_world_position()
            self.render_light(light,True)

        glDepthFunc(GL_LESS)
        glDepthMask(True)
        Render.set_blend_mode(BlendMode.NONE)
        Render.set_blend(False)


    def unproject(self,x,y):
        return Ray3D.create_from_2d(x, y, Render.width, Render.height, self.mainCamera.get_view_matrix(), self.mainCamera.get_projection_matrix())
    
    def camera_ray(self, mouse_x, mouse_y):
        x = (2.0 * mouse_x) /  Render.width - 1.0
        y = 1.0 - (2.0 * mouse_y) / Render.height
        ray_clip = glm.vec4(x, y, -1.0, 1.0)
        ray_eye = glm.inverse(self.mainCamera.get_projection_matrix()) * ray_clip
        ray_eye = glm.vec4(ray_eye.x, ray_eye.y, -1.0, 0.0)
        
        ray_world = glm.inverse(self.mainCamera.get_view_matrix()) * ray_eye
        ray_direction = glm.normalize(glm.vec3(ray_world))

        return Ray3D(self.mainCamera.local_pos, ray_direction)
        
    
    
    def update(self):
        if self.mainCamera is not None:
            self.mainCamera.update()
            Render.frustum.update(self.mainCamera.get_projection_view_matrix())
        for node in self.nodes:
            node.update()

    
    def debug(self, batch):
        for node in self.nodes:
           node.debug(batch) 



class LensFlare:
    def __init__(self, texture):
        self.flares = 8
        self.texture = texture
        self.VBO =0
        self.VAO =0
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.stride = 2 + 2 + 4  # 2 para posição, 2 para textura , 4 para cor
        self.vertices = [0.0] * (100 * self.stride)
        self.total = 0
        self.count =0
        self.vertexIndex =0
        self.width_tex =texture.width
        self.height_tex=texture.height
        self.occluded = False 
        self.tu =0
        self.tv =0
        self.red =0
        self.green =0
        self.blue =0
        self.alpha =0
        self.viewAngle = 0.0
        self.borderLimit=0
        self.cameraForward = glm.vec3(0.0, 0.0, 1.0)
        self.cameraPosition = glm.vec3(0.0, 0.0, 0.0)
        self.position = glm.vec3(0.0, 0.0, 1.0)
        self.burnClip = Rectangle(185, 423, 4, 4)
        self.clips=[]
        self.clips.append(Rectangle(128, 236, 128, 128))#sun
        self.clips.append(Rectangle(256, 411, 64, 64))
        self.clips.append(Rectangle(256, 347, 64, 64))
        self.clips.append(Rectangle(256, 283, 64, 64))
        self.clips.append(Rectangle(256, 219, 64, 64))
        self.clips.append(Rectangle(238, 155, 64, 64))
        self.clips.append(Rectangle(238, 155, 64, 64))

        self.clips.append(Rectangle(284, 475, 28, 28))
        self.clips.append(Rectangle(302, 91, 27, 26))




        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * 4, None,  GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.stride * 4, None)
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.stride * 4, ctypes.c_void_p(8))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, self.stride * 4, ctypes.c_void_p(16))
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.flareShader = FlareShader()
        self.view_matrix = None
        self.projection_matrix = None

        

        self.offsets = [-0.8,-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8 , 1.0]
        self.scales = [0.2, 0.15, 0.25, 0.5,0.75,0.5, 0.3, 0.4, 0.2]
        self.indexes = [0,4,1, 2,2, 3, 1, 5, 3,2,4,1,2,3]
        self.colors = [
            glm.vec3(1.0, 1.0, 1.0), glm.vec3(1.0, 0.6, 0.6), glm.vec3(1.0, 0.7, 1.0),
            glm.vec3(1.0, 1.0, 1.0), glm.vec3(1.0, 0.8, 1.0), glm.vec3(0.7, 1.0, 0.6), glm.vec3(1.0, 0.9, 0.5),
            glm.vec3(1.0, 1.0, 1.0), glm.vec3(1.0, 0.6, 0.6),
        ]

    def vertex2f(self, x, y):
        self.vertices[self.count + 0] = x
        self.vertices[self.count + 1] = y
        self.vertices[self.count + 2] = self.tu
        self.vertices[self.count + 3] = self.tv
        self.vertices[self.count + 4] = self.red
        self.vertices[self.count + 5] = self.green
        self.vertices[self.count + 6] = self.blue
        self.vertices[self.count + 7] = self.alpha

        self.count += self.stride
        self.vertexIndex += 1
    def textCoords(self, x, y):
        self.tu = x
        self.tv = y



    def draw_quad(self, x, y, s, src_x, src_y, src_width, src_height):


        left = (2 * src_x + 1) / (2 * self.width_tex)
        right = left + (src_width * 2 - 2) / (2 * self.width_tex)
        top = (2 * src_y + 1) / (2 * self.height_tex)
        bottom = top + (src_height * 2 - 2) / (2 * self.height_tex)
        size = s*80

        x1, y1 = x - size, y - size  # Esquerda cima
        x2, y2 = x + size, y - size  # Direita cima
        x3, y3 = x - size, y + size  # Esquerda baixo
        x4, y4 = x + size, y + size  # Direita baixo

        # Triângulo 1
        self.textCoords(left, top)
        self.vertex2f(x1, y1)  # Vértice 1 (esquerda cima)
        
        self.textCoords(right, top)
        self.vertex2f(x2, y2)  # Vértice 2 (direita cima)

        self.textCoords(left, bottom)
        self.vertex2f(x3, y3)  # Vértice 3 (esquerda baixo)

        # Triângulo 2
        self.textCoords(right, top)
        self.vertex2f(x2, y2)  # Vértice 2 (direita cima)

        self.textCoords(right, bottom)
        self.vertex2f(x4, y4)  # Vértice 4 (direita baixo)

        self.textCoords(left, bottom)
        self.vertex2f(x3, y3)  # Vértice 3 (esquerda baixo) - repetido

        

    def is_light_visible(self):
        fov = 90.0
        angle_deg = UtilMath.angle_between_camera_and_point(self.cameraPosition,  self.cameraForward, self.light_pos_world)
        self.viewAngle =  angle_deg

        if angle_deg <= fov / 2 or angle_deg >= 360 - fov / 2:
            return True
        else:
            return False
    
    def calculate_burn_by_angle(self, angle_deg, min_angle, max_angle):
        if angle_deg > max_angle:
            return 0.0
        if angle_deg < min_angle:
            return 0.6
        burn_factor = glm.mix(0.0, 0.6, (max_angle - angle_deg) / (max_angle - min_angle))
        return burn_factor


    def calculate_screen_position(self, view_matrix, projection_matrix):
        light_pos_screen = glm.project(self.light_pos_world, view_matrix,projection_matrix, glm.vec4(0.0, 0.0, Render.width, Render.height))
        return light_pos_screen

    def update(self,scene,light_pos_world,cameraPosition,cameraForward):
        ray_direction = glm.normalize(cameraPosition - light_pos_world)
        ray = Ray3D(light_pos_world, ray_direction)
        self.occluded = scene.ray_intersects (ray)
        self.light_pos_world  = light_pos_world
        self.cameraForward = cameraForward
        self.cameraPosition = cameraPosition
        self.view_matrix = Render.matrix[VIEW_MATRIX]
        self.projection_matrix = Render.matrix[PROJECTION_MATRIX]

    def calculate_fade(self, light_pos_screen, screen_width, screen_height, border_limit):
        awayX = 0.0
        if light_pos_screen.x < border_limit:
            awayX = border_limit - light_pos_screen.x
        elif light_pos_screen.x > screen_width - border_limit:
            awayX = light_pos_screen.x - (screen_width - border_limit)
        else:
            awayX = 0.0
        
        # Calcular o afastamento no eixo Y
        awayY = 0.0
        if light_pos_screen.y < border_limit:
            awayY = border_limit - light_pos_screen.y
        elif light_pos_screen.y > screen_height - border_limit:
            awayY = light_pos_screen.y - (screen_height - border_limit)
        else:
            awayY = 0.0
        
        # Determinar a maior distância (X ou Y)
        away = max(awayX, awayY)
        
  
        if away > border_limit:
            away = border_limit

        # quanto mais afastado, menor a intensidade
        intensity = 1.0 - (away / border_limit)
        

        intensity = max(0.0, min(intensity, 1.0))
        
        return intensity
 

    def render(self):
        
        if self.occluded:
            return
        light_pos_screen_3d = self.calculate_screen_position(self.view_matrix, self.projection_matrix)
        
        if  light_pos_screen_3d[2] <0.0:
            return
        light_pos_screen = glm.vec2(light_pos_screen_3d[0], light_pos_screen_3d[1])
        screen_width  = Render.width
        screen_height = Render.height
        if light_pos_screen.x < 0.0 or light_pos_screen.x > screen_width or light_pos_screen.y < 0.0 or light_pos_screen.y > screen_height:
            return
        screen_center = glm.vec2(screen_width / 2.0,  screen_height / 2.0)
        flare_direction = screen_center - light_pos_screen
        self.count = 0
        self.vertexIndex = 0
        self.borderLimit=screen_width * 0.2  # Borda equivalente a 20% da largura do screen
        #screen_width//2
        fade_intensity = self.calculate_fade(light_pos_screen, screen_width, screen_height, self.borderLimit)



        Render.set_shader(self.flareShader)
        Render.set_blend(True)
        Render.set_blend_mode(BlendMode.One)
        ortho_matrix = glm.ortho(0.0, float(screen_width),0.0, float(screen_height), 0.0, 1.0)
        self.flareShader.set_matrix("uOrthoMatrix", ortho_matrix)


        Render.set_texture(self.texture.id,0)
        if  self.is_light_visible():
            burn_intensity = self.calculate_burn_by_angle(self.viewAngle, 0.0, 20.0) 
            if burn_intensity > 0:
                quad_size = 8
                
                quad_opacity = glm.mix(0.0, 1.0,  burn_intensity)
                quad_color = glm.vec3(0.8, 0.8, 0.8) * quad_opacity 
                self.set_alpha(quad_opacity)
                self.set_color(quad_color)
                self.draw_quad(screen_center.x,screen_center.y, quad_size, self.burnClip.x, self.burnClip.y, self.burnClip.width, self.burnClip.height)                                                                                                            

            clip = self.clips[0]
            color = self.colors[0]# * fade_intensity
            self.render_flare_element(light_pos_screen.x,light_pos_screen.y, self.scales[0],  color,fade_intensity, clip)

            for i in range(1,self.flares):
                x = light_pos_screen.x - (flare_direction.x * self.offsets[i]) * 2
                y = light_pos_screen.y - (flare_direction.y * self.offsets[i]) * 2
            
                
                element_size = self.scales[i]
                element_color = self.colors[i] * fade_intensity 
                index = self.indexes[i]
                clip = self.clips[index]
                self.render_flare_element(x,y, element_size, element_color,fade_intensity,clip)
   

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)        
        glBufferData(GL_ARRAY_BUFFER, self.vertexIndex * self.stride * 4, np.array(self.vertices, dtype=np.float32), GL_DYNAMIC_DRAW)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, self.vertexIndex)


    def set_color(self, color):
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
    
    def set_alpha(self, a):
        self.alpha = a

    def render_flare_element(self, x,y, size, color,fade,clip):
        self.red = color.x 
        self.green = color.y
        self.blue = color.z
        self.alpha = fade
        self.draw_quad(x,y,size,clip.x,clip.y,clip.width,clip.height)
   