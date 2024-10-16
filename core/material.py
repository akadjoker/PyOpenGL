from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core  import *
from .shader import Shader
import glm
class Attribute(Enum):
    POSITION3D = 0
    POSITION2D = 1
    TEXCOORD0 = 2
    TEXCOORD1 = 3
    COLOR3 = 10
    COLOR4 = 11
    NORMAL = 12
    TANGENT = 13
    BITANGENT = 14


class Material:
    def __init__(self,name):
        self.shader = Shader()
        self.name = name
        self.attributes=[]
        self.textures = []
  
    

    def apply(self,core):
        pass

class ColorMaterial(Material):
    def __init__(self):
        super().__init__("Color")
        self.attributes=[Attribute.POSITION3D,Attribute.COLOR3] 
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec3 aColor;
        out vec3 vColor;
        void main()
        {
            vColor = aColor;
            gl_Position = vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        in vec3 vColor;
        out vec4 fragColor;
        void main()
        {
            fragColor = vec4(vColor, 1.0);
        }
        """
        self.shader.create_shader(vertex,fragment)

class TextureColorMaterial(Material):
    def __init__(self,texture):
        super().__init__("TextureColor")
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.COLOR4] 
        self.textures.append(texture) 

        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec4 aColor;
        out vec4 vColor;
        out vec2 vTexCoord;
        void main()
        {
            vColor = aColor;
            vTexCoord = aTexCoord;
            gl_Position = vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        out vec4 fragColor;
        in vec4 vColor;
        in vec2 vTexCoord;
        uniform sampler2D texture0;
        void main()
        {
            fragColor =   texture(texture0, vTexCoord) * vColor;
        }
        """
        self.shader.create_shader(vertex,fragment)
        self.shader.set_int("texture0",0)



class TextureMaterial(Material):
    def __init__(self,texture):
        super().__init__("Texture")
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0] 
        self.textures.append(texture) 

        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;

        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;

        out vec2 vTexCoord;
        void main()
        {

            vTexCoord = aTexCoord;
            gl_Position = uProjection * uView * uModel *  vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        out vec4 fragColor;

        in vec2 vTexCoord;
        uniform sampler2D texture0;
        void main()
        {
            fragColor =   texture(texture0, vTexCoord) ;
        }
        """
        self.shader.create_shader(vertex,fragment)
        self.shader.set_int("texture0",0)
    

class SolidMaterial(Material):
    def __init__(self):
        super().__init__("Solid")
        self.attributes=[Attribute.POSITION3D,Attribute.COLOR4] 
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec4 aColor;
        uniform mat4 uProjection;
        uniform mat4 uView;
      
        out vec4 vColor;
        void main()
        {
            vColor = aColor;
            gl_Position =  uProjection * uView * vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        in vec4 vColor;
        out vec4 fragColor;
        void main()
        {
            fragColor = vColor;
        }
        """
        self.shader.create_shader(vertex,fragment)


class SpriteMaterial(Material):
    def __init__(self):
        super().__init__("Sprite")
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.COLOR4] 

        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec4 aColor;

        
        uniform mat4 uProjection;
        uniform mat4 uView;

        out vec2 vTexCoord;
        out vec4 vColor;
        void main()
        {

            vColor = aColor;
            vTexCoord = aTexCoord;
            gl_Position = uProjection * uView *   vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        out vec4 fragColor;

        in vec2 vTexCoord;
        in vec4 vColor;
        uniform sampler2D texture0;
        void main()
        {
            fragColor =   texture(texture0, vTexCoord)  * vColor;
        }
        """
        self.shader.create_shader(vertex,fragment)
        self.shader.set_int("texture0",0)