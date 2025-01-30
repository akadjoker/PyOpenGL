import glm
from OpenGL.GL import *
import glfw
import numpy as np
import ctypes
import math


class Shader:
    def __init__(self):
        self.program = None

    def use(self):
        glUseProgram(self.program)

    def set_uniform(self, name, value):
        location = glGetUniformLocation(self.program, name)
        if location != -1:
            glUniform1f(location, value)
        else:
            print(f"Warning: Uniform '{name}' not found.")

    def set_vec3(self, name, value):
        location = glGetUniformLocation(self.program, name)
        if location != -1:
            glUniform3fv(location, 1, glm.value_ptr(value))
        else:
            print(f"Warning: Uniform '{name}' not found.")

    def set_mat4(self, name, value):
        location = glGetUniformLocation(self.program, name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(value))
        else:
            print(f"Warning: Uniform '{name}' not found.")

    def create(self, vertex_code, fragment_code):
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_code)
        glCompileShader(vertex_shader)
        self._check_compile_errors(vertex_shader, "VERTEX")

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_code)
        glCompileShader(fragment_shader)
        self._check_compile_errors(fragment_shader, "FRAGMENT")

        self.program = glCreateProgram()
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)
        self._check_link_errors(self.program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def load(self, vertex_path, fragment_path):
        with open(vertex_path, 'r') as vertex_file:
            vertex_code = vertex_file.read()
        with open(fragment_path, 'r') as fragment_file:
            fragment_code = fragment_file.read()
        self.create(vertex_code, fragment_code)

    def _check_compile_errors(self, shader, shader_type):
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(f"ERROR::SHADER::{shader_type}::COMPILATION_FAILED\n{error}")

    def _check_link_errors(self, program):
        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program).decode()
            print(f"ERROR::SHADER::PROGRAM::LINKING_FAILED\n{error}")
        






class Mesh:
    def __init__(self):
        # posição (3), cor (4), textura (2), normal (3)
        self.stride = 3 + 4 + 2 + 3
        self.vertices = []  
        self.indices = []    
        self.vtx = 0
        self.idx = 0

        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.update_vertex = False
        self.update_faces = False

    def add_vertex(self, x, y, z, r, g, b, a=1.0, u=0.0, v=0.0, nx=0.0, ny=0.0, nz=0.0):
        self.vertices.extend([x, y, z, r, g, b, a, u, v, nx, ny, nz])
        self.update_vertex = True
        self.vtx += 1
        return self.vtx - 1

    def add_face(self, a, b, c):
        self.indices.extend([a, b, c])
        self.update_faces = True
        self.idx += 3
        return self.idx - 3

    def _update_vertex(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertex_array = np.array(self.vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, GL_STATIC_DRAW)

    def _update_faces(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        index_array = np.array(self.indices, dtype=np.uint32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array.nbytes, index_array, GL_STATIC_DRAW)

    def render(self):
        if self.vao == 0:
            self.setup()
            return

        if self.update_vertex:
            self.update_vertex = False
            self._update_vertex()

        if self.update_faces:
            self.update_faces = False
            self._update_faces()

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.idx, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def setup(self):
        if not self.vertices or not self.indices or self.vao != 0:
            return

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertex_array = np.array(self.vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        index_array = np.array(self.indices, dtype=np.uint32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array.nbytes, index_array, GL_STATIC_DRAW)
 
        offset = 0
        stride_bytes = self.stride * ctypes.sizeof(ctypes.c_float)

        # Posição: atributo 0 (3 floats)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(0)
        offset += 3 * ctypes.sizeof(ctypes.c_float)

        # Cor: atributo 1 (4 floats)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(1)
        offset += 4 * ctypes.sizeof(ctypes.c_float)

        # Textura: atributo 2 (2 floats)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(2)
        offset += 2 * ctypes.sizeof(ctypes.c_float)

        # Normal: atributo 3 (3 floats)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(3)

        glBindVertexArray(0)

    def destroy(self):
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.ebo:
            glDeleteBuffers(1, [self.ebo])
    
    def translate(self, x, y, z):
        for i in range(0, len(self.vertices), self.stride):
            self.vertices[i] += x
            self.vertices[i + 1] += y
            self.vertices[i + 2] += z

        self.update_vertex = True
    def set_color(self, r, g, b, a=1.0):
        for i in range(3, len(self.vertices), self.stride):
            self.vertices[i] = r
            self.vertices[i + 1] = g
            self.vertices[i + 2] = b
            self.vertices[i + 3] = a

        self.update_vertex = True


class MeshBuilder:
    @staticmethod
    def create_cube(size=1.0):
        mesh = Mesh()

        s = size / 2.0
        vertices = [
            # Face frontal
            [-s, -s,  s, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # Vértice 0
            [ s, -s,  s, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0],  # Vértice 1
            [ s,  s,  s, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0],  # Vértice 2
            [-s,  s,  s, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0],  # Vértice 3

            # Face traseira
            [-s, -s, -s, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0],  # Vértice 4
            [ s, -s, -s, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, -1.0],  # Vértice 5
            [ s,  s, -s, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, -1.0],  # Vértice 6
            [-s,  s, -s, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, -1.0],  # Vértice 7
        ]

 
        vertices = np.array(vertices, dtype=np.float32)  

 
        indices = [
            # Face frontal
            0, 1, 2, 2, 3, 0,
            # Face direita
            1, 5, 6, 6, 2, 1,
            # Face traseira
            5, 4, 7, 7, 6, 5,
            # Face esquerda
            4, 0, 3, 3, 7, 4,
            # Face superior
            3, 2, 6, 6, 7, 3,
            # Face inferior
            4, 5, 1, 1, 0, 4,
        ]

 
        for vertex in vertices:
            mesh.add_vertex(*vertex)
        for i in range(0, len(indices), 3):
            mesh.add_face(indices[i], indices[i + 1], indices[i + 2])

   
        return mesh

    @staticmethod
    def create_plane(size=1.0, resolution=10):
        mesh = Mesh()
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = (i / resolution - 0.5) * size
                y = 0.0
                z = (j / resolution - 0.5) * size

                mesh.add_vertex(
                    x, y, z,  # Posição
                    1.0, 1.0, 1.0, 1.0,  # Cor (branco)
                    i / resolution, j / resolution,  # Coordenadas de textura
                    0.0, 1.0, 0.0  # Normal (apontando para cima)
                )

        for i in range(resolution):
            for j in range(resolution):
                top_left = i * (resolution + 1) + j
                top_right = top_left + 1
                bottom_left = (i + 1) * (resolution + 1) + j
                bottom_right = bottom_left + 1

                mesh.add_face(top_left, bottom_left, top_right)
                mesh.add_face(top_right, bottom_left, bottom_right)

        return mesh
    @staticmethod
    def create_quad(size=1.0):
        mesh = Mesh()
        s = size / 2.0

        vertices = [
            (-s, 0, -s, 1, 0, 0, 1, 0, 0, 0, 1, 0),
            (s, 0, -s, 0, 1, 0, 1, 1, 0, 0, 1, 0),
            (s, 0, s, 0, 0, 1, 1, 1, 0, 0, 1, 0),
            (-s, 0, s, 1, 1, 1, 1, 0, 0, 0, 1, 0),
        ]

        indices = [
            0, 1, 2, 2, 3, 0
        ]

        for v in vertices:
            mesh.add_vertex(*v)
        for i in range(0, len(indices), 3):
            mesh.add_face(indices[i], indices[i + 1], indices[i + 2])

        mesh.setup()
        return mesh
    @staticmethod
    def create_sphere(radius=1.0, sectors=32, stacks=16):
        mesh = Mesh()

        # Gerar vértices
        for i in range(stacks + 1):
            stack_angle = math.pi / 2 - i * (math.pi / stacks)
            xy = radius * math.cos(stack_angle)
            z = radius * math.sin(stack_angle)

            for j in range(sectors + 1):
                sector_angle = j * (2 * math.pi / sectors)

                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)

  
                normal = np.array([x, y, z])
                normal /= np.linalg.norm(normal)

 
                mesh.add_vertex(
                    x, y, z,  # Posição
                    1.0, 1.0, 1.0, 1.0,  
                    j / sectors, i / stacks,  # Coordenadas de textura
                    *normal  # Normal
                )

 
        for i in range(stacks):
            for j in range(sectors):
                first = i * (sectors + 1) + j
                second = first + sectors + 1

                mesh.add_face(first, second, first + 1)
                mesh.add_face(second, second + 1, first + 1)

        return mesh
 
    @staticmethod
    def create_cylinder(radius=1.0, height=2.0, segments=32):
  
        mesh = Mesh()
        vertices = []
        indices = []
        half_height = height / 2.0

    
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

 
            vertices.append((x, -half_height, z, 1, 1, 1, 1, x, z, 0, -1, 0))
            vertices.append((x, half_height, z, 1, 1, 1, 1, x, z, 0, 1, 0))

   
        bottom_center = len(vertices)
        vertices.append((0, -half_height, 0, 1, 1, 1, 1, 0.5, 0.5, 0, -1, 0))
        top_center = len(vertices)
        vertices.append((0, half_height, 0, 1, 1, 1, 1, 0.5, 0.5, 0, 1, 0))

 
        for i in range(segments):
            a = i * 2
            b = a + 1
            c = (a + 2) % (segments * 2)
            d = (b + 2) % (segments * 2)

            indices.extend([a, b, c])
            indices.extend([b, d, c])

 
        for i in range(segments):
            a = i * 2
            b = (a + 2) % (segments * 2)

 
            indices.extend([a, bottom_center, b])
  
            indices.extend([top_center, b + 1, a + 1])

 
        for v in vertices:
            mesh.add_vertex(*v)
        for i in range(0, len(indices), 3):
            mesh.add_face(indices[i], indices[i + 1], indices[i + 2])

        mesh.setup()
        return mesh
 
    @staticmethod
    def create_capsule(radius=1.0, height=2.0, stacks=16, slices=16):
        mesh = Mesh()
        vertices = []
        indices = []

        cylinder_height = height - 2 * radius  
        cylinder_half_height = cylinder_height / 2.0


        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            nx = x / radius 
            nz = z / radius
            u = i / slices

            #  inferior  
            vertices.append((x, -cylinder_half_height,z,1,1,1,1,  u, 0,  nx, 0, nz))
            #  superior  
            vertices.append((x, cylinder_half_height, z,1,1,1,1,  u, 1,   nx, 0, nz))

 
        for hemisphere in [-1, 1]:  # -1 para inferior, 1 para superior
            start_y = cylinder_half_height * hemisphere
            for i in range(stacks // 2 + 1):
                phi = (math.pi / 2) * i / (stacks / 2)  # 0 a PI/2
                
                for j in range(slices + 1):
                    theta = 2.0 * math.pi * j / slices
                    
                    if hemisphere == -1:
                        #   inferior,  PI/2 até PI
                        actual_phi = math.pi/2 + phi
                    else:
                        #  superior,   de PI/2 até 0
                        actual_phi = math.pi/2 - phi
                    
                    x = radius * math.sin(actual_phi) * math.cos(theta)
                    y = radius * math.cos(actual_phi) + start_y
                    z = radius * math.sin(actual_phi) * math.sin(theta)
                    
                    nx = x / radius
                    ny = math.cos(actual_phi)   
                    nz = z / radius
                    
                    u = j / slices
                    v = i / (stacks / 2) if hemisphere == 1 else 1 - i / (stacks / 2)
                    
                    vertices.append((x, y, z,1,1,1,1,u, v, nx, ny, nz))

     
        for v in vertices:
            mesh.add_vertex(*v)

    
        for i in range(slices):
            curr = i * 2
            next = (i + 1) * 2
            if i == slices - 1:
                next = 0


            indices.extend([curr, curr + 1, next])
            indices.extend([next, curr + 1, next + 1])

        vertices_per_ring = slices + 1
        cylinder_vertex_count = (slices + 1) * 2

     
        for hemisphere in [0, 1]:  # 0 para inferior, 1 para superior
            start_index = cylinder_vertex_count + hemisphere * (vertices_per_ring * (stacks // 2 + 1))
            
            for i in range(stacks // 2):
                for j in range(slices):
                    current_ring = start_index + i * vertices_per_ring
                    next_ring = current_ring + vertices_per_ring
                    
                    curr = current_ring + j
                    next = current_ring + j + 1
                    next_curr = next_ring + j
                    next_next = next_ring + j + 1
                    
                    if hemisphere == 0:  # Hemisfério inferior
                        indices.extend([curr, next, next_curr])
                        indices.extend([next, next_next, next_curr])
                    else:  # Hemisfério superior
                        indices.extend([curr, next_curr, next])
                        indices.extend([next, next_next, next_curr])

  
        for i in range(0, len(indices), 3):
            mesh.add_face(indices[i], indices[i + 1], indices[i + 2])

        mesh.setup()
        return mesh

    @staticmethod
    def create_torus(radius=1.0, tube_radius=0.4, radial_segments=32, tubular_segments=32):
        mesh = Mesh()

        for i in range(radial_segments):
            theta = (2.0 * math.pi * i) / radial_segments
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)

            for j in range(tubular_segments):
                phi = (2.0 * math.pi * j) / tubular_segments
                cos_phi = math.cos(phi)
                sin_phi = math.sin(phi)

                x = (radius + tube_radius * cos_phi) * cos_theta
                y = tube_radius * sin_phi
                z = (radius + tube_radius * cos_phi) * sin_theta

                u = i / radial_segments
                v = j / tubular_segments

                nx = cos_phi * cos_theta
                ny = sin_phi
                nz = cos_phi * sin_theta

                mesh.add_vertex(x, y, z, 1, 1, 1, 1, u, v, nx, ny, nz)

        # Criar faces do toro
        for i in range(radial_segments):
            for j in range(tubular_segments):
                a = i * tubular_segments + j
                b = ((i + 1) % radial_segments) * tubular_segments + j
                c = a + 1
                d = b + 1

                if j == tubular_segments - 1:
                    c -= tubular_segments
                    d -= tubular_segments

                mesh.add_face(a, b, c)
                mesh.add_face(b, d, c)

        mesh.setup()
        return mesh

    @staticmethod
    def create_cone(radius=1.0, height=2.0, segments=32):
        mesh = Mesh()
        half_height = height / 2.0

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

            u = (x / radius) * 0.5 + 0.5
            v = (z / radius) * 0.5 + 0.5

            mesh.add_vertex(x, -half_height, z, 1, 0, 0, 1, u, v, 0, -1, 0)

        center_index = len(mesh.vertices) // mesh.stride
        mesh.add_vertex(0, -half_height, 0, 1, 1, 1, 1, 0.5, 0.5, 0, -1, 0)

        # Topo do cone
        top_index = len(mesh.vertices) // mesh.stride
        mesh.add_vertex(0, half_height, 0, 0, 1, 0, 1, 0.5, 0.5, 0, 1, 0)


        for i in range(segments):
            next_i = (i + 1) % segments
            mesh.add_face(i, next_i, center_index)


        for i in range(segments):
            next_i = (i + 1) % segments
            mesh.add_face(i, next_i, top_index)

        mesh.setup()
        return mesh

class Node3D:
    def __init__(self):
        self.position = glm.vec3(0.0)     # Posição (x, y, z)
        self.rotation = glm.vec3(0.0)     # Rotação (Euler: pitch, yaw, roll)
        self.scale = glm.vec3(1.0)        # Escala
        self.parent = None                
        self.children = []               
        self.transform = glm.mat4(1.0)    # Transformação global

    def add_child(self, child):
        if child.parent:
            child.parent.remove_child(child)
        self.children.append(child)
        child.parent = self

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def update(self,dt=1.0):
        self.update_transform()
        for child in self.children:
            child.update(dt)


    def update_transform(self):

        local_transform = glm.mat4(1.0)
        local_transform = glm.translate(local_transform, self.position)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))  # Rotação X (pitch)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))  # Rotação Y (yaw)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))  # Rotação Z (roll)
        local_transform = glm.scale(local_transform, self.scale)

    
        if self.parent:
            self.transform = self.parent.transform * local_transform
        else:
            self.transform = local_transform


    
    def render(self):
        for child in self.children:
            child.render()

class Camera(Node3D):
    def __init__(self, fov=60.0, aspect_ratio=16/9, near=0.1, far=100.0):
        super().__init__()
        self.fov = fov                    # Campo de visão (graus)
        self.aspect_ratio = aspect_ratio  
        self.near = near                  
        self.far = far                  

    def get_view_matrix(self):
         return glm.inverse(self.transform)

    def get_projection_matrix(self):
          return glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)
    



class FreeCamera(Camera):
    def __init__(self, position=glm.vec3(0.0, 0.0, 5.0), yaw=-90.0, pitch=0.0):
        super().__init__()
        self.position = position
        self.rotation = glm.vec3(pitch, yaw, 0.0)  # (pitch, yaw, roll)
        self.speed = 5.0          
        self.sensitivity = 0.1    
        self.update_transform()    

    def get_front_vector(self):
        """Vetor para frente (local -Z)."""
        return -glm.vec3(self.transform[0][2], self.transform[1][2], self.transform[2][2])

    def get_right_vector(self):
        """Vetor para a direita (local +X)."""
        return glm.vec3(self.transform[0][0], self.transform[1][0], self.transform[2][0])

    def process_keyboard(self, window, delta_time):
  
        velocity = self.speed * delta_time
        front = self.get_front_vector()
        right = self.get_right_vector()

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position += front * velocity
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position -= front * velocity
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position -= right * velocity
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position += right * velocity
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            self.position.y -= velocity
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            self.position.y += velocity

        self.update_transform()

    def process_mouse_movement(self, xoffset, yoffset):
 
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.rotation.y += xoffset  # Yaw
        self.rotation.x -= yoffset  # Pitch
        self.rotation.x = glm.clamp(self.rotation.x, -89.0, 89.0)

        self.update_transform()




class OrbitalCamera(Camera):
    def __init__(self, target=glm.vec3(0.0), distance=5.0, azimuth=0.0, elevation=30.0):
        super().__init__()
        self.target = target          # Ponto de foco (alvo)
        self.distance = distance      # Distância do alvo
        self.azimuth = azimuth        # Ângulo horizontal (em graus)
        self.elevation = elevation    # Ângulo vertical (em graus)
        self.sensitivity = 0.5        # Sensibilidade do mouse
        self.zoom_speed = 2.0         # Velocidade do zoom
        self.min_distance = 1.0       # Distância mínima
        self.max_distance = 20.0      # Distância máxima
        
        self.update_transform()        

    def update_transform(self):
        # Converte ângulos para radianos
        azimuth_rad = glm.radians(self.azimuth)
        elevation_rad = glm.radians(self.elevation)

        self.position.x = self.target.x + self.distance * glm.cos(azimuth_rad) * glm.cos(elevation_rad)
        self.position.y = self.target.y + self.distance * glm.sin(elevation_rad)
        self.position.z = self.target.z + self.distance * glm.sin(azimuth_rad) * glm.cos(elevation_rad)

        super().update_transform()

    def process_mouse_drag(self, xoffset, yoffset):
        self.azimuth -= xoffset * self.sensitivity
        self.elevation += yoffset * self.sensitivity
        self.elevation = glm.clamp(self.elevation, -89.0, 89.0)  # Limita a elevação
        self.update_transform()

    def process_mouse_scroll(self, yoffset):
        self.distance -= yoffset * self.zoom_speed
        self.distance = glm.clamp(self.distance, self.min_distance, self.max_distance)
        self.update_transform()

    def get_view_matrix(self):
        """Matriz de visualização (olhando para o alvo)."""
        return glm.lookAt(self.position, self.target, glm.vec3(0.0, 1.0, 0.0))


class FPSCamera(Camera):
    def __init__(self, position=glm.vec3(0.0, 1.6, 0.0), yaw=-90.0, pitch=0.0):
        super().__init__()
        self.position = position      # Posição inicial (ex: altura de 1.6m para um personagem)
        self.rotation = glm.vec3(pitch, yaw, 0.0)  # (pitch, yaw, roll)
        self.speed = 5.0              # Velocidade de movimento
        self.sensitivity = 0.1        # Sensibilidade do mouse
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.velocity_y = 0.0
        self.gravity = -9.81  # m/s²
        self.update_transform()

    def get_front_vector(self):
        """Vetor de direção para frente (horizontal no plano XZ)."""
        front = glm.vec3(
            glm.cos(glm.radians(self.rotation.y)) * glm.cos(glm.radians(self.rotation.x)),
            glm.sin(glm.radians(self.rotation.x)),
            glm.sin(glm.radians(self.rotation.y)) * glm.cos(glm.radians(self.rotation.x))
        )
        return glm.normalize(front)

    def get_right_vector(self):
        """Vetor de direção para a direita (no plano XZ)."""
        front = self.get_front_vector()
        right = glm.normalize(glm.cross(front, self.world_up))
        return right

    def process_keyboard(self, window, delta_time):
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS and self.on_ground:
            self.velocity_y = 5.0  

        # Aplica gravidade
        self.velocity_y += self.gravity * delta_time
        self.position.y += self.velocity_y * delta_time
        velocity = self.speed * delta_time
        front = self.get_front_vector()
        right = self.get_right_vector()

 
        if self.position.y < 1.6:
            self.position.y = 1.6
            self.velocity_y = 0.0
            self.on_ground = True

        # Movimento horizontal (ignora o componente Y do vetor front)
        front_y_zero = glm.normalize(glm.vec3(front.x, 0.0, front.z))

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position += front_y_zero * velocity
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position -= front_y_zero * velocity
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position -= right * velocity
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position += right * velocity

        self.update_transform()

    def process_mouse_movement(self, xoffset, yoffset):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.rotation.y += xoffset  # Yaw
        self.rotation.x -= yoffset  # Pitch
        self.rotation.x = glm.clamp(self.rotation.x, -89.0, 89.0)  # Limita o pitch

        self.update_transform()

    def get_view_matrix(self):
        return glm.lookAt(
            self.position,
            self.position + self.get_front_vector(),
            self.world_up
        )
    

class ThirdPersonCamera(Camera):
    def __init__(self, target=glm.vec3(0.0), distance=5.0, azimuth=0.0, elevation=30.0):
        super().__init__()
        self.target = target              # Alvo que a câmera segue
        self.desired_distance = distance  # Distância desejada do alvo
        self.current_distance = distance  # Distância atual (para suavização)
        self.desired_azimuth = azimuth    # Ângulo horizontal desejado
        self.current_azimuth = azimuth    # Ângulo horizontal atual
        self.desired_elevation = elevation  # Ângulo vertical desejado
        self.current_elevation = elevation  # Ângulo vertical atual
        self.smoothness = 5.0             # Fator de suavização (quanto maior, mais lento)
        self.sensitivity = 0.5            # Sensibilidade do mouse
        self.zoom_speed = 2.0             # Velocidade do zoom
        self.min_distance = 1.0           # Distância mínima
        self.max_distance = 20.0          # Distância máxima
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.update()

    def update(self):
        self.current_azimuth = glm.lerp(self.current_azimuth, self.desired_azimuth, self.smoothness * 0.016)
        self.current_elevation = glm.lerp(self.current_elevation, self.desired_elevation, self.smoothness * 0.016)
        self.current_distance = glm.lerp(self.current_distance, self.desired_distance, self.smoothness * 0.016)

        # Converte ângulos para radianos
        azimuth_rad = glm.radians(self.current_azimuth)
        elevation_rad = glm.radians(self.current_elevation)

        # Calcula a posição da câmera em coordenadas esféricas
        self.position.x = self.target.x + self.current_distance * glm.cos(azimuth_rad) * glm.cos(elevation_rad)
        self.position.y = self.target.y + self.current_distance * glm.sin(elevation_rad)
        self.position.z = self.target.z + self.current_distance * glm.sin(azimuth_rad) * glm.cos(elevation_rad)



    def process_mouse_drag(self, xoffset, yoffset):
        self.desired_azimuth -= xoffset * self.sensitivity
        self.desired_elevation += yoffset * self.sensitivity
        self.desired_elevation = glm.clamp(self.desired_elevation, -89.0, 89.0)

    def process_mouse_scroll(self, yoffset):
        self.desired_distance -= yoffset * self.zoom_speed
        self.desired_distance = glm.clamp(self.desired_distance, self.min_distance, self.max_distance)

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.world_up)

    def update_target_position(self, new_target):
        self.target = new_target

class Model(Node3D):
    def __init__(self):
        super().__init__()
        self.meshes = []

    
    def add_mesh(self, mesh):
        mesh.setup()
        self.meshes.append(mesh)
    
    def render(self):
        if len(self.meshes) < 0:
            return
        for mesh in self.meshes:
            mesh.render()
        for child in self.children:
            child.render()



def RenderNodes(node, shader,dt):
    node.update(dt)
    model_matrix = node.transform
    glUniformMatrix4fv(glGetUniformLocation(shader.program, "model"),1, GL_FALSE, glm.value_ptr(model_matrix))
    node.render()



if not glfw.init():
    raise Exception("GLFW não pôde ser inicializado")



window = glfw.create_window(1280, 720, "Node3D e Camera", None, None)
glfw.make_context_current(window)


def mouse_scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)

glfw.set_scroll_callback(window, mouse_scroll_callback)

glEnable(GL_DEPTH_TEST)



glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)



last_time = glfw.get_time()
last_x, last_y = 640, 360
target_position = glm.vec3(0.0, 0.0, 0.0)  # Posição do personagem/alvo
camera = ThirdPersonCamera(target=target_position, distance=5.0)



last_x, last_y = 640, 360
dragging = False

root = Node3D()
root.update()





cube_node = Model()
cube_node.position = glm.vec3(0, 0, 0)
cube_node.scale = glm.vec3(2, 0.5, 2)



cube = MeshBuilder.create_cube(1.0)
cube.translate(0, 1, 0)
cube.set_color(1.0, 0.0, 0.0)

plane = MeshBuilder.create_plane(size=5.0)
plane.set_color(0.0, 1.0, 0.0)

sphere = MeshBuilder.create_sphere()
sphere.translate(0, 1, 1)
sphere.set_color(0.0, 0.0, 1.0)

cylinder = MeshBuilder.create_cylinder(radius=1.0, height=2.0, segments=32)

capsule = MeshBuilder.create_capsule(radius=0.5, height=2.0, stacks=16, slices=16)

torus = MeshBuilder.create_torus(radius=1.0, tube_radius=0.4, radial_segments=32, tubular_segments=32)
torus.translate(-4, 2, 5)

cone = MeshBuilder.create_cone(radius=1.0, height=2.0, segments=32)
cone.translate(4, 2, -5)

#cube_node.add_mesh(cylinder)
#cube_node.add_mesh(cube)
cube_node.add_mesh(plane)
#cube_node.add_mesh(sphere)
cube_node.add_mesh(capsule)
cube_node.add_mesh(torus)
cube_node.add_mesh(cone)


root.add_child(cube_node)



shader = Shader()
shader.load("assets/shader.vert", "assets/shader.frag")

dragging = False
while not glfw.window_should_close(window):

    current_time = glfw.get_time()
    delta_time = current_time - last_time
    last_time = current_time

    camera.update_target_position(target_position)


    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
        if not dragging:
            dragging = True
            last_x, last_y = glfw.get_cursor_pos(window)
        else:
            xpos, ypos = glfw.get_cursor_pos(window)
            xoffset = xpos - last_x
            yoffset = ypos - last_y
            last_x, last_y = xpos, ypos
            camera.process_mouse_drag(xoffset, yoffset)
    else:
        dragging = False



    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

   


    camera.update()
    view = camera.get_view_matrix()
    projection = camera.get_projection_matrix()

    shader.use()
    shader.set_mat4("view", view)
    shader.set_mat4("projection", projection)



    RenderNodes(root, shader, delta_time)



    glfw.swap_buffers(window)
    glfw.poll_events()
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
     

glfw.terminate()