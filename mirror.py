import core 
from core.core import *
from core.mesh import *
from core.builder import *
from core.render import *
from core.scene import Entity,Camera,CameraFPS,Scene
from core.batch import *
from core.font import Font
from core.sprite import SpriteBatch
from core.gui import Gui
from core.input import Input
from core.material import *
import sys
import glm
import math   



def unproject(vector, proj,view):
    ndc_vector = glm.vec4(vector.x, vector.y, vector.z, 1.0)
    inv_view_proj = glm.inverse( proj * view)
    world_vector = inv_view_proj * ndc_vector
    if world_vector.w != 0.0:
        world_vector /= world_vector.w
    return glm.vec3(world_vector)

def create_camera_frustum(fov, aspect, zNear, zFar, position, direction, up):
    # Cálculos dos planos near e far
    vSideNear = math.tan(math.radians(fov / 2)) * zNear
    hSideNear = vSideNear * aspect

    vSideFar = math.tan(math.radians(fov / 2)) * zFar
    hSideFar = vSideFar * aspect

    # Coordenadas locais (Right, Up, Forward)
    forward = glm.normalize(direction)
    right = glm.normalize(glm.cross(forward, up))
    up = glm.normalize(glm.cross(right, forward))

    # Centros dos planos near e far
    nearCenter = position + forward * zNear
    farCenter = position + forward * zFar

    # Vértices do plano near
    nearTopLeft = nearCenter + (up * vSideNear) - (right * hSideNear)
    nearTopRight = nearCenter + (up * vSideNear) + (right * hSideNear)
    nearBottomLeft = nearCenter - (up * vSideNear) - (right * hSideNear)
    nearBottomRight = nearCenter - (up * vSideNear) + (right * hSideNear)

    # Vértices do plano far
    farTopLeft = farCenter + (up * vSideFar) - (right * hSideFar)
    farTopRight = farCenter + (up * vSideFar) + (right * hSideFar)
    farBottomLeft = farCenter - (up * vSideFar) - (right * hSideFar)
    farBottomRight = farCenter - (up * vSideFar) + (right * hSideFar)

    # Conexões entre vértices (linhas do frustum)
    lines = [
        # Near Plane
        (nearTopLeft, nearTopRight),
        (nearTopRight, nearBottomRight),
        (nearBottomRight, nearBottomLeft),
        (nearBottomLeft, nearTopLeft),

        # Far Plane
        (farTopLeft, farTopRight),
        (farTopRight, farBottomRight),
        (farBottomRight, farBottomLeft),
        (farBottomLeft, farTopLeft),

        # Conexões Near -> Far
        (nearTopLeft, farTopLeft),
        (nearTopRight, farTopRight),
        (nearBottomLeft, farBottomLeft),
        (nearBottomRight, farBottomRight),
    ]

    return lines


def send_lines_to_batch(batch, lines):
    for start, end in lines:
        batch.line3d(start.x, start.y, start.z, end.x, end.y, end.z)

def send_lines_to_batch_transform(batch, lines,trasform):
    for start, end in lines:
        s = trasform * glm.vec4(start.x, start.y, start.z, 1.0)
        e = trasform * glm.vec4(end.x, end.y, end.z, 1.0)
        batch.line3d(s.x, s.y, s.z, e.x, e.y, e.z)
        #batch.line3d(start.x, start.y, start.z, end.x, end.y, end.z)

    
class MirrorShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL] 
        vertex="""#version 330

        layout (location = 0) in vec3 aPos;       
        layout (location = 1) in vec2 aTexCoords; 
        layout (location = 2) in vec3 aNormal;    

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        out vec3 FragPos;    
        out vec3 Normal;     
        out vec2 TexCoords;  

        void main() 
        {
            vec4 worldPosition = model * vec4(aPos, 1.0);
            FragPos = vec3(worldPosition);  
            Normal = normalize(mat3(transpose(inverse(model))) * aNormal);  
            TexCoords = aTexCoords;  
            gl_Position = projection * view * worldPosition; 
        }

      
        """

        fragment="""#version 330

        out vec4 FragColor;

        in vec3 FragPos;     
        in vec3 Normal;      
        in vec2 TexCoords;   

        uniform sampler2D baseTexture;         
        uniform sampler2D reflectionTexture;  
        uniform vec3 viewPos;             

        void main() 
        {
            // Vetor de visão (da câmera para o fragmento)
            vec3 viewDir = normalize(viewPos - FragPos);

            // Calcular o vetor refletido com base na normal
            vec3 reflectedDir = reflect(-viewDir, normalize(Normal));

            // Mapear para coordenadas de textura de reflexão
            //vec2 reflectTexCoords = TexCoords + reflectedDir.xy * 0.5; // Ajuste básico para reflexões

           vec2 reflectTexCoords = vec2(1.0 -TexCoords.x, TexCoords.y); 

            // Amostrar a textura base e a textura de reflexão
            vec4 baseColor = texture(baseTexture, TexCoords); // Detalhes do espelho
            vec4 reflectionColor = texture(reflectionTexture, reflectTexCoords); // Reflexão dinâmica

            // Combinar a textura base e a reflexão
            FragColor = mix(baseColor, reflectionColor, 0.6); // 60% reflexão, 40% textura base
        }

        """
        self.create_shader(vertex,fragment)


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920

yaw = 0.0  # Inicializa a câmera olhando para frente (Y negativa)
pitch = 0.0  # Inicializa sem inclinação

core = Core(1024, 920, "OpenGL Demo")


Render.load_texture("assets/brickwall_diffuse.jpg","brickwall")
textureMirror =Render.load_texture("assets/mirror.jpg","mirror")



plane = Builder.create_plane(4, 4)
plane.rotate(0,0,-90)
mesh = Builder.load_obj("assets/room.obj")
mesh.rotate(0,90,0)

plane.set_attributes([Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL])
mesh.set_attributes([Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL])

plane.update()
mesh.update()


frustum = Frustum()
Render.set_blend(False)
Render.set_depth_test(True)
Render.set_blend_mode(BlendMode.Normal)


Render.set_clear_color(0.2,0.2,0.6)
Render.set_clear_mode(True)


shader = Render.get_shader("texture")
mirroShader = MirrorShader()
material = Material(Render.get_texture("brickwall"))
materialMirror = Material(Render.get_texture("mirror"))


camera = Camera(45.0,core.width / core.height)
camera.set_perspective(45.0, 16.0 / 9.0, 0.25, 4000.0)
camera.translate(0.0, 10.5, 25.0)
camera.rotate(pitch, yaw, 0.0)




mouseSensitivity = 90



Gui.init()
lines = LinesBatch(1024*8)
position = glm.vec3(0.0, 5.0, 0.0)

depth = DepthBuffer()
depth.init(1024, 1024)


while core.run():




    speed = core.get_delta_time() * 255

    if Input.mouse_down(0) and not Gui.has_focus():
        yaw   -= Input.get_mouse_delta_x()  *  mouseSensitivity
        pitch -= Input.get_mouse_delta_y()  *  mouseSensitivity
        pitch = max(-89.0, min(89.0, pitch))
        camera.rotate(pitch, yaw, 0.0)




    if Input.keyboard_down(glfw.KEY_W):
        camera.move(0, 0, -speed)
    if Input.keyboard_down(glfw.KEY_S):
        camera.move(0, 0, speed)

    if Input.keyboard_down(glfw.KEY_A):
        camera.move(-speed,0,0)
    if Input.keyboard_down(glfw.KEY_D):
        camera.move(speed,0,0)


    

    Render.set_blend(False)
    Render.set_depth_test(True)
    Render.set_clear_mode(True)

 
    


    #mirro

    position =  glm.vec3(-10.0, 5.0, 0.0)
    direction =  glm.vec3(0.0, 0.0, 0.0)
    up = glm.vec3(0.0, 1.0, 0.0)  # Vetor "para cima"
    target = position + direction
    view_matrix = glm.lookAt(position, target, up)


    # Parâmetros do frustum
    fov = glm.radians(45.0)  
    aspect = 16 / 12
    zNear = 0.1
    zFar = 200.0
    perspective_matrix = glm.perspective(fov, aspect, zNear, zFar)

    
    #frustum_lines = create_camera_frustum(fov, aspect, zNear, zFar, position, direction, up)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.0, 0.5, 0.0))
    Render.set_shader(shader)
    shader.set_matrix4fv("uModel", glm.value_ptr(model_mat))
    shader.set_matrix4fv("uView", glm.value_ptr(view_matrix))
    shader.set_matrix4fv("uProjection", glm.value_ptr(perspective_matrix))
    #shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    #shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))

    depth.begin()
    Render.render_mesh(mesh,material)
    depth.end()


    Render.set_viewport(0, 0, core.width, core.height)
    Render.clear()

    Render.set_matrix(VIEW_MATRIX, camera.get_view_matrix())
    Render.set_matrix(PROJECTION_MATRIX, camera.get_projection_matrix())
    
    Render.set_shader(shader)
    shader.set_matrix4fv("uView", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    shader.set_matrix4fv("uProjection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(0.0, 0.5, 0.0))
    shader.set_matrix4fv("uModel", glm.value_ptr(model_mat))
    Render.render_mesh(mesh,material)

    #viewMirror = glm.lookAt(camera.get_local_position(), glm.vec3(0.0, 0.5, 0.0), glm.vec3(0.0, 1.0, 0.0))

    Render.set_shader(mirroShader)
    mirroShader.set_matrix4fv("view", glm.value_ptr(Render.matrix[VIEW_MATRIX]))
    mirroShader.set_matrix4fv("projection", glm.value_ptr(Render.matrix[PROJECTION_MATRIX]))
    mirroShader.set_vector3f("viewPos", camera.get_local_position())
    mirroShader.set_int("baseTexture", 0)
    mirroShader.set_int("reflectionTexture", 1)

    model_mat = glm.mat4(1.0)
    model_mat = glm.translate(model_mat, glm.vec3(-5.0, 4.5, 0.0))
    model_mat = glm.scale(model_mat, glm.vec3(2.0, 1.0, 2.0))
    mirroShader.set_matrix4fv("model", glm.value_ptr(model_mat))
    Render.set_texture(textureMirror.id, 0)
    Render.set_texture(depth.color, 1)
    Render.render_mesh_no_material(plane)

    cproj = Render.matrix[PROJECTION_MATRIX]
    cview = Render.matrix[VIEW_MATRIX]




    Render.set_matrix(MODEL_MATRIX, glm.mat4(1.0))
    lines.grid(10, 10, True)


    # projection = glm.perspective(glm.radians(45.0), 16/9, 0.1, 100.0)
    # view = glm.lookAt(glm.vec3(2, 5, 0), glm.vec3(1, 0, 0), glm.vec3(0, 1, 0))





    
    #send_lines_to_batch(lines, frustum_lines)


    lines.render() 

    Render.set_depth_test(False)
    Render.set_blend(True)
    Render.set_blend_mode(BlendMode.NONE)
    Render.set_clear_mode(True)
    Gui.begin(0,10, core.height-80, 260, 80, options={"background": True,'dragging': False, "bar": True, "title": "Stats"})
    if Gui.is_window_visible(0):
        delta = "{:.6f}".format(core.get_delta_time()) 
        text = "FPS: " + str(core.get_fps())+ " | " + "Frame Time: " + delta
        Gui.label(2, 5, text)
        stats = "Triangles: " + str(Render.triangles) + " | " + "Vertices: " + str(Render.vertices)
        Gui.label(2, 25, stats)
    Gui.end()



    


    Gui.render(core.width , core.height)






    core.flip()

core.close() 

