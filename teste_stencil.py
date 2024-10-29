import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *


import numpy as np
import glm

# Função para inicializar o contexto OpenGL
def initialize_context():
    if not glfw.init():
        return None
    glutInit()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    
    window = glfw.create_window(800, 600, "Stencil Shadow Example", None, None)
    if not window:
        glfw.terminate()
        return None

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    return window

# Função para desenhar um plano
def draw_plane():
    glColor3f(0.8, 0.8, 0.8)  # Cor cinza claro para o plano
    glBegin(GL_QUADS)
    glVertex3f(-5.0, 0.0, -5.0)
    glVertex3f(5.0, 0.0, -5.0)
    glVertex3f(5.0, 0.0, 5.0)
    glVertex3f(-5.0, 0.0, 5.0)
    glEnd()

# Função para desenhar um cubo
def draw_cube():
    glColor3f(0.0, 0.0, 1.0)  # Cor azul para o cubo
    glutSolidCube(1.0)

# Função para definir a sombra usando stencil
def draw_shadow():
    glEnable(GL_STENCIL_TEST)
    glClear(GL_STENCIL_BUFFER_BIT)
    glStencilFunc(GL_ALWAYS, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    
    # Desenha o cubo sobre o stencil para marcar a área de sombra
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    draw_cube()
    glPopMatrix()

    # Configura stencil para desenhar apenas onde o valor é 1 (onde o cubo estava)
    glStencilFunc(GL_EQUAL, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    # Desenha a sombra no plano onde o stencil foi marcado
    glColor4f(0.0, 0.0, 0.0, 0.5)  # Cor de sombra semi-transparente
    glBegin(GL_QUADS)
    glVertex3f(-0.5, 0.01, -0.5)
    glVertex3f(0.5, 0.01, -0.5)
    glVertex3f(0.5, 0.01, 0.5)
    glVertex3f(-0.5, 0.01, 0.5)
    glEnd()

    glDisable(GL_STENCIL_TEST)

# Função principal de renderização
def render_scene():
    # Limpa os buffers de cor, profundidade e stencil
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    # Define uma transformação de câmera
    glLoadIdentity()
    gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)

    # Desenha o plano e o cubo
    draw_plane()
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)  # Levanta o cubo acima do plano
    draw_cube()
    glPopMatrix()

    # Desenha a sombra do cubo no plano usando stencil
    draw_shadow()

# Função principal
def main():
    window = initialize_context()
    if not window:
        print("Falha ao inicializar o contexto OpenGL.")
        return

    # Configura parâmetros do OpenGL
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Loop principal
    while not glfw.window_should_close(window):
        render_scene()
        
        # Atualiza a tela
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
