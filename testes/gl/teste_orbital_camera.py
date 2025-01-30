import glm
from OpenGL.GL import *
import glfw



class Mesh:
    def __init__(self, vertices, indices):
        self.vertices = vertices  # Lista de vértices (x, y, z, r, g, b, ...)
        self.indices = indices    # Lista de índices para desenho com glDrawElements

        # Buffers OpenGL
        self.vao = None
        self.vbo = None
        self.ebo = None

        # Inicializa os buffers
        self.setup_buffers()

    def setup_buffers(self):
        # Gera VAO, VBO e EBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        # Configura o VBO (dados dos vértices)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 
                     (GLfloat * len(self.vertices))(*self.vertices), 
                     GL_STATIC_DRAW)

        # Configura o EBO (índices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 
                     (GLuint * len(self.indices))(*self.indices), 
                     GL_STATIC_DRAW)

        # Define os atributos dos vértices (posição e cor)
        # Posição: atributo 0 (3 floats)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Cor: atributo 1 (3 floats)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def destroy(self):
        # Limpa os buffers quando não forem mais necessários
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])

import glm

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

    def update_transform(self):
        # Calcula a matriz de transformação local
        local_transform = glm.mat4(1.0)
        local_transform = glm.translate(local_transform, self.position)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))  # Rotação X (pitch)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))  # Rotação Y (yaw)
        local_transform = glm.rotate(local_transform, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))  # Rotação Z (roll)
        local_transform = glm.scale(local_transform, self.scale)

        # Atualiza a transformação global
        if self.parent:
            self.transform = self.parent.transform * local_transform
        else:
            self.transform = local_transform

        # Atualiza os filhos recursivamente
        for child in self.children:
            child.update_transform()

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
    

import glfw

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
        """Movimentação restrita ao plano XZ."""
        velocity = self.speed * delta_time
        front = self.get_front_vector()
        right = self.get_right_vector()

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
        self.update_position()

    def update_position(self):
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

        # Atualiza a matriz de transformação
        self.update_transform()

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

class MeshNode(Node3D):
    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh          # Referência à Mesh
        self.shader = None        # Shader para renderização

    def draw(self, view_matrix, projection_matrix):
        if not self.shader:
            return

        # Ativa o shader
        glUseProgram(self.shader)

        # Obtém a matriz de modelo (transformação global do nó)
        model_matrix = self.transform

        # Envia as matrizes para o shader
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "model"),
            1, GL_FALSE, glm.value_ptr(model_matrix)
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "view"),
            1, GL_FALSE, glm.value_ptr(view_matrix)
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, glm.value_ptr(projection_matrix)
        )

        # Renderiza a Mesh
        glBindVertexArray(self.mesh.vao)
        glDrawElements(GL_TRIANGLES, len(self.mesh.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)



def compile_shader(vertex_path, fragment_path):
    # Implemente uma função para compilar os shaders (exemplo simplificado)
    vertex_code = open(vertex_path).read()
    fragment_code = open(fragment_path).read()

    # Cria e compila os shaders
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_code)
    glCompileShader(vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_code)
    glCompileShader(fragment_shader)

    # Cria o programa do shader
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    # Limpa os shaders
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program



# Inicializa o GLFW
if not glfw.init():
    raise Exception("GLFW não pôde ser inicializado")

window = glfw.create_window(1280, 720, "Node3D e Camera", None, None)
glfw.make_context_current(window)

# Configuração básica do OpenGL
glEnable(GL_DEPTH_TEST)

# Cria os nós
root = Node3D()


glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

camera = FPSCamera(position=glm.vec3(0.0, 1.6, 0.0))


last_time = glfw.get_time()
last_x, last_y = 640, 360
root.add_child(camera)
camera.position = glm.vec3(0, 5, 5)    # Posiciona a câmera
camera.rotation = glm.vec3(-45, 0, 0)  # Aponta para baixo (pitch de -45 graus)

root.update_transform()



# Vértices do cubo (posição x, y, z + cor r, g, b)
vertices = [
    # Frente (vermelho)
    -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
     0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
     0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
    -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,

    # Trás (verde)
    -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
     0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
     0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
    -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
]

# Índices (triângulos)
indices = [
    # Frente
    0, 1, 2, 2, 3, 0,
    # Trás
    4, 5, 6, 6, 7, 4,
    # Esquerda
    4, 0, 3, 3, 7, 4,
    # Direita
    1, 5, 6, 6, 2, 1,
    # Topo
    3, 2, 6, 6, 7, 3,
    # Base
    4, 5, 1, 1, 0, 4
]

# Cria a Mesh do cubo
cube_mesh = Mesh(vertices, indices)

cube_node = MeshNode(cube_mesh)
cube_node.position = glm.vec3(0, 0, 0)
cube_node.scale = glm.vec3(1, 1, 1)

# Adiciona à hierarquia
root.add_child(cube_node)

shader = compile_shader("assets/shader.vert", "assets/shader.frag")
cube_node.shader = shader

while not glfw.window_should_close(window):

    current_time = glfw.get_time()
    delta_time = current_time - last_time
    last_time = current_time

    # Movimentação com teclado
    camera.process_keyboard(window, delta_time)

    camera.process_keyboard(window, delta_time)

    # Processa movimento do mouse
    xpos, ypos = glfw.get_cursor_pos(window)
    xoffset = xpos - last_x
    yoffset = last_y - ypos  # Eixo Y invertido
    last_x, last_y = xpos, ypos
    camera.process_mouse_movement(xoffset, yoffset)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Atualiza as transformações da hierarquia
    root.update_transform()

    # Obtém as matrizes da câmera
    view = camera.get_view_matrix()
    projection = camera.get_projection_matrix()

    # Renderiza todos os MeshNodes
    def render_node(node):
        if isinstance(node, MeshNode):
            node.draw(view, projection)
        for child in node.children:
            render_node(child)

    render_node(root)

    glfw.swap_buffers(window)
    glfw.poll_events()
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
     

glfw.terminate()