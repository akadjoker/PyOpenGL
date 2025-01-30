import glm
from OpenGL.GL import *
import glfw



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
        #x,y,z,r,g,b,u,v,nx,ny,nz
        self.stride = 3  + 4 + 2 + 3
        self.vertices = []  
        self.indices = []    
        self.vtx = 0
        self.idx = 0

        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.update_vertex = False
        self.update_faces = False

    def add_vertex(self, x, y, z, r, g, b,a=1.0,u=0.0,v=0.0,nx=0.0,ny=0.0,nz=0.0):
        #position
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)
        #color
        self.vertices.append(r)
        self.vertices.append(g)
        self.vertices.append(b)
        self.vertices.append(a)
        #texture
        self.vertices.append(u)
        self.vertices.append(v)
        #normal
        self.vertices.append(nx)
        self.vertices.append(ny)
        self.vertices.append(nz)
        self.update_vertex = True
        self.vtx += 1
        return self.vtx-1


    def add_face(self, a,b,c):
        self.indices.append(a)
        self.indices.append(b)
        self.indices.append(c)
        self.idx += 3
        return self.idx-3
                
    def _update_vertex(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 
                        (GLfloat * len(self.vertices))(*self.vertices), 
                        GL_STATIC_DRAW)
    def _update_faces(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 
                        (GLuint * len(self.indices))(*self.indices),
                        GL_STATIC_DRAW)
    def render(self):
        if self.vao == 0 or self.vbo == 0 or self.ebo == 0:
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
        if not self.vertices or not self.indices:
            return
        if self.vao != 0:
            return
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)


        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 
                     (GLfloat * len(self.vertices))(*self.vertices), 
                     GL_STATIC_DRAW)

   
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 
                     (GLuint * len(self.indices))(*self.indices), 
                     GL_STATIC_DRAW)

        # Posição: atributo 0 (3 floats)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.stride * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
   
        offset = 3

        # Cor: atributo 1 (4 floats)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.stride * sizeof(GLfloat), ctypes.c_void_p(offset * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)
        offset += 4

        # Textura: atributo 2 (2 floats)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, self.stride * sizeof(GLfloat), ctypes.c_void_p(offset * sizeof(GLfloat)))
        glEnableVertexAttribArray(2)
        offset += 2

        # Normal: atributo 3 (3 floats)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, self.stride * sizeof(GLfloat), ctypes.c_void_p(offset * sizeof(GLfloat)))
        glEnableVertexAttribArray(3)
        offset += 3


        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])



class Node3D:
    def __init__(self):
        self.position = glm.vec3(0.0)     # Posição (x, y, z)
        self.rotation = glm.vec3(0.0)     # Rotação (Euler: pitch, yaw, roll)
        self.scale = glm.vec3(1.0)        # Escala
        self.parent = None                # Nó pai
        self.children = []                # Nós filhos
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
        self.aspect_ratio = aspect_ratio  # Proporção da tela
        self.near = near                  # Plano próximo
        self.far = far                   # Plano distante

    def get_view_matrix(self):
        """Retorna a matriz de visualização (inversa da transformação global)."""
        return glm.inverse(self.transform)

    def get_projection_matrix(self):
        """Retorna a matriz de projeção (perspectiva)."""
        return glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)
    



class FreeCamera(Camera):
    def __init__(self, position=glm.vec3(0.0, 0.0, 5.0), yaw=-90.0, pitch=0.0):
        super().__init__()
        self.position = position
        self.rotation = glm.vec3(pitch, yaw, 0.0)  # (pitch, yaw, roll)
        self.speed = 5.0          # Velocidade de movimento
        self.sensitivity = 0.1    # Sensibilidade do mouse
        self.update_transform()   # Atualiza a matriz de transformação

    def get_front_vector(self):
        """Vetor para frente (local -Z)."""
        return -glm.vec3(self.transform[0][2], self.transform[1][2], self.transform[2][2])

    def get_right_vector(self):
        """Vetor para a direita (local +X)."""
        return glm.vec3(self.transform[0][0], self.transform[1][0], self.transform[2][0])

    def process_keyboard(self, window, delta_time):
        """Movimentação com WASD/QE."""
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
        """Rotação com o mouse."""
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
        
        self.update_transform()       # Atualiza a posição inicial

    def update_transform(self):
        # Converte ângulos para radianos
        azimuth_rad = glm.radians(self.azimuth)
        elevation_rad = glm.radians(self.elevation)

        # Calcula a posição da câmera em coordenadas esféricas
        self.position.x = self.target.x + self.distance * glm.cos(azimuth_rad) * glm.cos(elevation_rad)
        self.position.y = self.target.y + self.distance * glm.sin(elevation_rad)
        self.position.z = self.target.z + self.distance * glm.sin(azimuth_rad) * glm.cos(elevation_rad)

        # Atualiza a matriz de transformação (herdado de Node3D)
        super().update_transform()

    def process_mouse_drag(self, xoffset, yoffset):
        """Atualiza os ângulos com o movimento do mouse."""
        self.azimuth -= xoffset * self.sensitivity
        self.elevation += yoffset * self.sensitivity
        self.elevation = glm.clamp(self.elevation, -89.0, 89.0)  # Limita a elevação
        self.update_transform()

    def process_mouse_scroll(self, yoffset):
        """Atualiza a distância com a roda do mouse."""
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
            self.velocity_y = 5.0  # Força do pulo

        # Aplica gravidade
        self.velocity_y += self.gravity * delta_time
        self.position.y += self.velocity_y * delta_time
        velocity = self.speed * delta_time
        front = self.get_front_vector()
        right = self.get_right_vector()

        # Verifica colisão com o chão (ex: y = 0.0)
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
        """Rotação livre (como em jogos FPS)."""
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.rotation.y += xoffset  # Yaw
        self.rotation.x -= yoffset  # Pitch
        self.rotation.x = glm.clamp(self.rotation.x, -89.0, 89.0)  # Limita o pitch

        self.update_transform()

    def get_view_matrix(self):
        """Matriz de visualização baseada na rotação e posição."""
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
        # Interpola os valores atuais em direção aos desejados (suavização)
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
        """Atualiza os ângulos com movimento do mouse."""
        self.desired_azimuth -= xoffset * self.sensitivity
        self.desired_elevation += yoffset * self.sensitivity
        self.desired_elevation = glm.clamp(self.desired_elevation, -89.0, 89.0)

    def process_mouse_scroll(self, yoffset):
        """Atualiza a distância com a roda do mouse."""
        self.desired_distance -= yoffset * self.zoom_speed
        self.desired_distance = glm.clamp(self.desired_distance, self.min_distance, self.max_distance)

    def get_view_matrix(self):
        """Matriz de visualização (sempre olhando para o alvo)."""
        return glm.lookAt(self.position, self.target, self.world_up)

    def update_target_position(self, new_target):
        """Atualiza a posição do alvo (ex: personagem se movendo)."""
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




cube_mesh = Mesh()
        # Frente (vermelho)
cube_mesh.add_vertex(-0.5, -0.5,  0.5, 1.0, 0.0, 0.0)
cube_mesh.add_vertex(0.5, -0.5,  0.5, 1.0, 0.0, 0.0)
cube_mesh.add_vertex(0.5,  0.5,  0.5, 1.0, 0.0, 0.0)
cube_mesh.add_vertex(-0.5,  0.5,  0.5, 1.0, 0.0, 0.0)

# Trás (verde)
cube_mesh.add_vertex(-0.5, -0.5, -0.5, 0.0, 1.0, 0.0)
cube_mesh.add_vertex(0.5, -0.5, -0.5, 0.0, 1.0, 0.0)
cube_mesh.add_vertex(0.5,  0.5, -0.5, 0.0, 1.0, 0.0)
cube_mesh.add_vertex(-0.5,  0.5, -0.5, 0.0, 1.0, 0.0)
# Frente
cube_mesh.add_face(0, 1, 2)
cube_mesh.add_face( 2, 3, 0)
# Trás
cube_mesh.add_face(4, 5, 6)
cube_mesh.add_face( 6, 7, 4)
# Esquerda
cube_mesh.add_face(4, 0, 3)
cube_mesh.add_face(3, 7, 4)
# Direita
cube_mesh.add_face(1, 5, 6) 
cube_mesh.add_face(6, 2, 1)
# Topo
cube_mesh.add_face(3, 2, 6) 
cube_mesh.add_face(6, 7, 3)
# Base
cube_mesh.add_face(4, 5, 1)
cube_mesh.add_face(1, 0, 4)

cube_node = Model()
cube_node.position = glm.vec3(0, 0, 0)
cube_node.scale = glm.vec3(2, 0.5, 2)
cube_node.add_mesh(cube_mesh)

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