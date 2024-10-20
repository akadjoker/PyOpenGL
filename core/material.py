import glm

import numpy as np
from OpenGL.GL import *
from .core  import *
from .shader import Shader, Attribute
from .render import Render




class Material:
    def __init__(self,diffuse=None,spacular=None):
        self.textures = []
        if diffuse is not None:
            self.set_texture(0,diffuse)
        if spacular is not None:
            self.set_texture(1,spacular)
  
    def set_texture(self,layer,texture):
        while len(self.textures) <= layer:
            self.textures.append(None)
        self.textures[layer] = texture

    def apply(self):
        for layer in range(len(self.textures)):
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

    



class SunShader(Shader):
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

            //vec3 color = norm * 0.5 + 0.5;

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
        





class DirectionalShader(Shader):
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

        out vec2 TexCoords;
        out vec3 Normal;
        out vec3 FragPos;
        void main()
        {
            FragPos = vec3(uModel * vec4(aPos, 1.0));
            TexCoords = aTexCoord;
            Normal = mat3(transpose(inverse(uModel))) * aNormal;  
            gl_Position =  uProjection * uView  *  vec4(FragPos, 1.0);
        }
        """

        fragment="""#version 330 core
        out vec4 FragColor;

        struct DirLight {
            vec3 direction;
            vec3 ambient;
            vec3 diffuse;
            vec3 specular;
        };
        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;
        uniform sampler2D diffuseMap;
        uniform sampler2D specularMap;
        uniform DirLight directional;
        uniform float shininess;
        uniform vec3 viewPos;
        
        vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor);


        void main()
        {
            vec3 diffuseColor = texture(diffuseMap, TexCoords).rgb;
            vec3 specularColor = texture(specularMap, TexCoords).rgb;
            vec3 norm = normalize(Normal);
            vec3 viewDir = normalize(viewPos - FragPos);

            vec3 result = vec3(0.0);

            result = CalcDirLight(directional, norm, viewDir, diffuseColor, specularColor);


            FragColor = vec4(result, 1.0);
        }

           vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor)
        {
            vec3 lightDir = normalize(-light.direction);
            vec3 diffuse = vec3(0.0);
            vec3 specular = vec3(0.0);
            vec3 ambient = light.ambient * diffuseColor;

            float diff = dot(normal, lightDir);
            if (diff > 0.0)   
            {

                // Diffuse shading
                diff = max(diff, 0.0);

                // Specular shading
                vec3 halfwayDir = normalize(lightDir + viewDir);
                float spec = pow(max(dot(normal, halfwayDir), 0.0), shininess);
                if (spec > 0.0)
                {
                    specular = light.specular * spec * specularColor;
                }

                // Combine results
                diffuse = light.diffuse * diff * diffuseColor;
                
            }

            return (ambient + diffuse + specular);
        }
     
        """
        self.create_shader(vertex,fragment)
       

       

    def apply(self):
        light = Render.get_light(0)

        self.set_vector3f("viewPos",light.camera)
        self.set_vector3f("directional.direction", light.direction)
        self.set_vector3f("directional.ambient", light.ambient)
        self.set_vector3f("directional.diffuse", light.diffuse)
        self.set_vector3f("directional.specular", light.specular)

        self.set_float("shininess", light.shininess)
            



class PointShader(Shader):
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

        out vec2 TexCoords;
        out vec3 Normal;
        out vec3 FragPos;
        void main()
        {
            FragPos = vec3(uModel * vec4(aPos, 1.0));
            TexCoords = aTexCoord;
            Normal = mat3(transpose(inverse(uModel))) * aNormal;  
            gl_Position =  uProjection * uView  *  vec4(FragPos, 1.0);
        }
        """

        fragment="""#version 330 core
        out vec4 FragColor;

        struct PointLight 
        {
            vec3 position;
            float constant;
            float linear;
            float quadratic;
            float range ;
            vec3 ambient;
            vec3 diffuse;
            vec3 specular;
        };

        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;
        uniform sampler2D diffuseMap;
        uniform sampler2D specularMap;
        uniform PointLight point;
        uniform float shininess;
        uniform vec3 viewPos;
        
        vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 diffuseColor, vec3 specularColor);
        vec3 CalcColor(PointLight light,vec3 direction, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor);

        void main()
        {
            vec3 diffuseColor = texture(diffuseMap, TexCoords).rgb;
            vec3 specularColor = texture(specularMap, TexCoords).rgb;
            vec3 norm = normalize(Normal);
            vec3 viewDir = normalize(viewPos - FragPos);

            vec3 result = vec3(0.0);


            result = CalcPointLight(point, norm, FragPos, viewDir, diffuseColor, specularColor);


            FragColor = vec4(result, 1.0);
        }

    

        vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 diffuseColor, vec3 specularColor)
        {
            // Direção da luz (da luz até o fragmento)
            vec3 lightDirection =  light.position - fragPos;
            float distanceToPoint = length(lightDirection);

              // Suavizar a transição quando o fragmento estiver fora do alcance da luz
            //float falloff = smoothstep(light.range, light.range * 1.2, distanceToPoint);
            float falloff = smoothstep(light.range * 0.6, light.range, distanceToPoint);



            if (distanceToPoint > light.range) return vec3(0.0);
            lightDirection = normalize(lightDirection);

            vec3 color = CalcColor(light, lightDirection, normal, viewDir, diffuseColor, specularColor);
            //if (color == vec3(0.0)) return vec3(0.0);



            // Aplicar o falloff (suavização) diretamente à intensidade da luz
            color *= (1.0 - falloff);

            float attenuation =  light.constant + 
                                 (light.linear * distanceToPoint) +
                                 light.quadratic * (distanceToPoint * distanceToPoint) ;
            
            attenuation = max(attenuation, 0.0001); 
            

            return color / attenuation;
        }

         vec3 CalcColor(PointLight light,vec3 direction, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor)
        {
            vec3 lightDir = normalize(direction);
            vec3 diffuse = vec3(0.0);
            vec3 specular = vec3(0.0);
            vec3 ambient = light.ambient * diffuseColor;

            float diff = dot(normal, lightDir);
            if (diff > 0.0)   
            {

                // Diffuse shading
                diff = max(diff, 0.0);

                // Specular shading
                vec3 halfwayDir = normalize(lightDir + viewDir);
                float spec = pow(max(dot(normal, halfwayDir), 0.0), shininess);
                if (spec > 0.0)
                {
                    specular = light.specular * spec * specularColor;
                }

                // Combine results
                diffuse = light.diffuse * diff * diffuseColor;
                
            }

            return (ambient + diffuse + specular);
        }

        """
        self.create_shader(vertex,fragment)
       

       

    def apply(self):    
        light = Render.get_light(0)

        self.set_vector3f("viewPos",light.camera)


        self.set_vector3f("point.position", light.position)
        self.set_float("point.constant", light.constant)
        self.set_float("point.linear", light.linear)
        self.set_float("point.quadratic", light.quadratic)
        self.set_vector3f("point.ambient", light.ambient)
        self.set_vector3f("point.diffuse", light.diffuse)
        self.set_vector3f("point.specular", light.specular)
        self.set_float("point.range", light.range)



            