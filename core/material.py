import glm

import numpy as np
from OpenGL.GL import *
from .core  import *
from .shader import Shader, Attribute
from .render import Render




class Material:
    def __init__(self,texture=None):
        self.textures = []
        if texture:
            self.set_texture(0,texture)
  
    def set_texture(self,layer,texture):
        while len(self.textures) <= layer:
            self.textures.append(None)
        self.textures[layer] = texture

    def apply(self):
        for layer in range(len(self.textures)):
            if self.textures[layer]:
                Render.set_texture(self.textures[layer].id, layer)


class PointShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        void main()
        {
            gl_Position = vec4(aPos, 1.0);
        }
        """

        fragment="""#version 330
        out vec4 fragColor;
        uniform sampler2D texture0;
        void main()
        {
            fragColor =   vec4(1.0,1.0,1.0,1.0);
        }
        """
        self.create_shader(vertex,fragment)
        print("Created Shader")





class SolidShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.COLOR4] 
        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec4 aColor;
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;

        out vec4 vColor;
        void main()
        {
            vColor = aColor;
            gl_Position =   uProjection * uView * uModel *  vec4(aPos, 1.0);
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
        self.create_shader(vertex,fragment)
        print("Created Shader")

class DefaultShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.COLOR4] 

        vertex="""#version 330

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec4 aColor;

        
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;

        out vec2 vTexCoord;
        out vec4 vColor;
        void main()
        {

            vColor = aColor;
            vTexCoord = aTexCoord;
            gl_Position =  uProjection * uView * uModel *  vec4(aPos, 1.0);
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
        self.create_shader(vertex,fragment)



class TextureShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0] 


        

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
        self.create_shader(vertex,fragment)

    



class AmbientShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL] 

        vertex="""#version 330 core

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec3 aNormal;

        
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;

        out vec2 vTexCoord;
        out vec3 vNormal;
        out vec3 FragPos;
        void main()
        {
            FragPos = vec3(uModel * vec4(aPos, 1.0));
            vTexCoord = aTexCoord;
            vNormal = mat3(transpose(inverse(uModel))) * aNormal;  
            gl_Position =  uProjection * uView  *  vec4(FragPos, 1.0);
        }
        """

        fragment="""#version 330 core
        out vec4 fragColor;

        in vec2 vTexCoord;
        in vec3 vNormal;
        in vec3 FragPos;
        uniform sampler2D texture0;
        uniform vec3 viewPos; 
        uniform vec3 lightPos;
        uniform vec3 lightColor;
        uniform vec3 objectColor;
        uniform float ambientStrength;
        uniform float specularStrength;
        void main()
        {
            //ambient
            vec3 ambient = ambientStrength * lightColor;
            
            // diffuse 
            vec3 norm = normalize(vNormal);
            vec3 lightDir = normalize(lightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor;
            
            // specular
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 reflectDir = reflect(-lightDir, norm);  
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 128);
            vec3 specular = specularStrength * spec * lightColor;  
            
            vec3 result = (ambient + diffuse + specular) * objectColor;

            vec3 normalizedNormal = normalize(vNormal);
            vec3 color = normalizedNormal * 0.5 + 0.5;

            fragColor =   texture(texture0, vTexCoord)  * vec4(result, 1.0) ;
            //fragColor =  vec4(color, 1.0);
        }
        """
        self.create_shader(vertex,fragment)
       

       

    def apply(self):
        light = Render.get_light(0)

        self.set_vector3f("viewPos",light.camera)
        self.set_vector3f("lightPos", light.position)
        self.set_vector3f("lightColor", light.color)
        self.set_vector3f("objectColor", light.object_color)
        self.set_float("ambientStrength", light.ambient_strength)
        self.set_float("specularStrength", light.specular_strength)
        