import glm
import math
from enum import Enum
import numpy as np
from OpenGL.GL import *
from .core  import *
from .shader import Shader, Attribute
from .render import Render


class LightType(Enum):
    NONE = 0
    AMBIENT = 1
    DIRECTIONAL = 2
    POINT = 3
    SPOT = 4

class Material:
    def __init__(self,diffuse=None,spacular=None):
        self.textures = []
        self.castShadow = True
        if diffuse is not None:
            self.set_texture(0,diffuse)
        if spacular is not None:
            self.set_texture(1,spacular)

    def add_texture(self,texture):
        self.textures.append(texture)
  
    def set_texture(self,layer,texture):
        while len(self.textures) <= layer:
            self.textures.append(None)
        self.textures[layer] = texture

    def apply(self):
        for layer in range(len(self.textures)):
            Render.set_texture(self.textures[layer].id, layer)
        

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


class SkyboxShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 

        vertex="""#version 330

        layout(location = 0) in vec3 aPosition;


        
        uniform mat4 uProjection;
        uniform mat4 uView;


        out vec2 vTexCoord;
       
        void main()
        {

       
            vTexCoord = aPosition;
            mat4 view =mat4(mat3(uView));
            vec4 pos = uProjection * view * vec4(aPosition, 1.0);
            gl_Position = pos.xyww;
        }
        """

        fragment="""#version 330
        out vec4 fragColor;

        in vec2 vTexCoord;

        uniform samplerCube cubeTexture;
        void main()
        {
            fragColor =   texture(cubeTexture, vTexCoord) ;
        }
        """
        self.create_shader(vertex,fragment)




class InstanceShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.POSITION3D] 

        vertex="""#version 330

    layout (location = 0) in vec3 aPosition;
    layout (location = 1) in vec2 aTexCoord;
    layout (location = 2) in vec3 aInstancePosition;

    uniform mat4 uProjection;
    uniform mat4 uView;
    uniform mat4 uModel;
    out vec2 TexCoord;



    void main()
    {
        TexCoord = aTexCoord;
        

        gl_Position =  uProjection * uView * uModel * vec4(aPosition + aInstancePosition, 1.0);
    }
        """

        fragment="""#version 330

        in vec2 TexCoord;            
        out vec4 FragColor;
        uniform sampler2D uTexture0;

        void main()
        {
            
            vec4 texColor =  texture(uTexture0, TexCoord) ;
            FragColor =texColor;

        }
        """
        self.create_shader(vertex,fragment)


class StencilShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION2D] 

        vertex="""#version 330

            layout (location = 0) in vec2 aPos;



            void main() {
                gl_Position = vec4(aPos, 0.0, 1.0);

            }
        """

        fragment="""#version 330

  

        
        out vec4 FragColor;

        void main() 
        {
            FragColor = vec4(0.0, 0.0, 0.0, 0.5);
        }
        """
        self.create_shader(vertex,fragment)

class ScreenShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION2D] 

        vertex="""#version 330

            layout (location = 0) in vec2 aPosition;
            out vec2 TexCoord;

            void main() 
            {
                gl_Position = vec4(aPosition, 0.0, 1.0);
                TexCoord = (aPosition + 1.0) / 2.0;
            }
        """

        fragment="""#version 330

            uniform sampler2D uTexture;
            in vec2 TexCoord;
            out vec4 FragColor;
            void main() 
            {
                //float depthValue = texture(uTexture, TexCoord).r; 
                //FragColor = vec4(vec3(depthValue), 1.0); 
                FragColor = texture(uTexture, TexCoord);
            }
        """
        self.create_shader(vertex,fragment)

class DepthShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 

        vertex="""#version 330
             layout (location = 0) in vec3 aPosition;
            uniform mat4 uLightSpaceMatrix;
            uniform mat4 uModel;
    
            void main()
            {
                
                gl_Position  =  uLightSpaceMatrix *  uModel* vec4(aPosition, 1.0);

            }

        """

        fragment="""#version 330
           
        //out float fragDepth;
       out vec4 FragColor;

        void main() 
        {
       ///     fragDepth = gl_FragCoord.z;


                // FragColor = vec4(vec3(gl_FragCoord.z), 1.0);
        
            }
        """
        self.create_shader(vertex,fragment)


class VolumeDepthShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 

        vertex="""#version 330

            layout (location = 0) in vec3 aPosition;

            uniform mat4 uProjection;
            uniform mat4 uView;
   
          
     
            void main() 
            {

              
                gl_Position =    uProjection * uView  * vec4(aPosition, 1.0);
            }


        """

        fragment="""#version 330
           

       out vec4 FragColor;

        void main() 
        {
      
             gl_FragColor = vec4(0.04, 0.28, 0.26, 1.0);
          

        }

        """

   


        self.create_shader(vertex,fragment)

class PointDepthShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 

        vertex="""#version 330
             layout (location = 0) in vec3 aPosition;
           
            uniform mat4 uModel;      
            uniform mat4 lightSpaceMatrix;

            void main() {
                gl_Position = lightSpaceMatrix * uModel * vec4(aPosition, 1.0);
            }

        """

        fragment="""#version 330
           
           in vec4 FragPos;

        uniform vec3 lightPos;
        uniform float far_plane;

        void main() 
        {
        
            float lightDistance = length(FragPos.xyz - lightPos);
            
    
            
            lightDistance = lightDistance / far_plane;
            
      
           // gl_FragDepth = lightDistance;
        }

        """
        self.create_shader(vertex,fragment)
        self.set_float("far_plane", 10.0)



class PointGeoDepthShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D] 

        vertex="""#version 330
             layout (location = 0) in vec3 aPosition;
           
            uniform mat4 uModel;      
          

            void main() 
            {
                gl_Position =  uModel * vec4(aPosition, 1.0);
            }

        """

        fragment="""#version 330
           
           in vec4 FragPos;

        uniform vec3 lightPos;
        uniform float far_plane;

        void main() 
        {
        
            float lightDistance = length(FragPos.xyz - lightPos);
            
    
            
            lightDistance = lightDistance / far_plane;
            
      
            gl_FragDepth = lightDistance;
        }

        """
        geometry = """#version 330
        layout (triangles) in;
        layout (triangle_strip, max_vertices=18) out;

            uniform mat4 shadowMatrices[6];

            out vec4 FragPos; // FragPos from GS (output per emitvertex)

            void main()
            {
                for(int face = 0; face < 6; ++face)
                {
                    gl_Layer = face; // built-in variable that specifies to which face we render.
                    for(int i = 0; i < 3; ++i) // for each triangle's vertices
                    {
                        FragPos = gl_in[i].gl_Position;
                        gl_Position = shadowMatrices[face] * FragPos;
                        EmitVertex();
                    }    
                    EndPrimitive();
                }
            } 

        """

        self.create_shader_with_geometry(vertex,fragment,geometry)
        
        self.set_float("far_plane", 20.0)

class DebugDepthShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION2D] 

        vertex="""#version 330

        layout (location = 0) in vec2 aPosition;
        out vec2 TexCoord;

        void main() 
        {
            gl_Position = vec4(aPosition, 0.0, 1.0);
            TexCoord = (aPosition + 1.0) / 2.0;
        }
        """

        fragment="""#version 330
            uniform sampler2D uTexture;
            in vec2 TexCoord;
            out vec4 FragColor;
            void main() 
            {
                    float depthValue = texture(uTexture, TexCoord).r;

                    FragColor =  vec4(vec3(depthValue), 1.0);
            }
        """
        self.create_shader(vertex,fragment)




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
        self.set_vector3f("lightColor", glm.vec3(1.0, 1.0, 1.0))
        self.set_vector3f("objectColor",  glm.vec3(1.0, 1.0, 1.0))
        self.set_float("ambientStrength",   0.5)
        self.set_float("specularStrength",   0.8)
       

       

    def apply(self):
        # light = Render.get_light(0)

        pass





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

      
        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;
        uniform sampler2D diffuseMap;

        

        uniform vec3 ambient;

        
      

        void main()
        {
            vec3 diffuseColor = texture(diffuseMap, TexCoords).rgb;

           
            vec3 result = diffuseColor * ambient;



            //result = CalcColor( norm, viewDir, diffuseColor);


            FragColor = vec4(result, 1.0);
        }

      
     
        """
        self.create_shader(vertex,fragment)
       
       

       

        
        

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
           float shininess;
        };

        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;
        
        uniform sampler2D diffuseMap;
        uniform sampler2D specularMap;
        
        uniform PointLight point;
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
                float spec = pow(max(dot(normal, halfwayDir), 0.0), light.shininess);
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
       

       







class SpotShader(Shader):
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

        struct SpotLight 
        {
            vec3 position;
            vec3 direction;

            float cutOff;
            float outerCutOff;

            float constant;
            float linear;
            float quadratic;

            vec3 ambient;
            vec3 diffuse;
            vec3 specular;
           float shininess;
        };

        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;
        uniform sampler2D diffuseMap;
        uniform sampler2D specularMap;
        
        uniform SpotLight spot;
        uniform vec3 viewPos;
        
        vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 diffuseColor, vec3 specularColor);
        vec3 CalcColor(SpotLight light, vec3 direction, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor);

        void main()
        {
            vec3 diffuseColor = texture(diffuseMap, TexCoords).rgb;
            vec3 specularColor = texture(specularMap, TexCoords).rgb;
            vec3 norm = normalize(Normal);
            vec3 viewDir = normalize(viewPos - FragPos);

            vec3 result = vec3(0.0);


            result = CalcSpotLight(spot, norm, FragPos, viewDir, diffuseColor, specularColor);


            FragColor = vec4(result, 1.0);
        }

    

        vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 diffuseColor, vec3 specularColor)
        {
            
            vec3 lightDirection =  light.position - fragPos;
            float distanceToPoint = length(lightDirection);
            lightDirection = normalize(lightDirection);

            float theta = dot(lightDirection, normalize(-light.direction));
            //if (theta <= light.outerCutOff) return vec3(0.0); //??

            
            vec3 color = CalcColor(light, lightDirection, normal, viewDir, diffuseColor, specularColor);
            //if (color == vec3(0.0)) return vec3(0.0); //??



            float attenuation =  light.constant + 
                                 (light.linear * distanceToPoint) +
                                 light.quadratic * (distanceToPoint * distanceToPoint) ;
            
             attenuation = max(attenuation, 0.0001); 

             float epsilon = light.cutOff - light.outerCutOff;
             //float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

            float minIntensity = 0.4;  // Intensidade mínima da luz??
            float intensity = clamp((theta - light.outerCutOff) / (light.cutOff - light.outerCutOff), minIntensity, 1.0);

   
            

            return (color / attenuation) * intensity;
        }

         vec3 CalcColor(SpotLight light,vec3 direction, vec3 normal, vec3 viewDir, vec3 diffuseColor, vec3 specularColor)
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
                float spec = pow(max(dot(normal, halfwayDir), 0.0), light.shininess);
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
       





class SingleShadowShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL] 

  
        vertex="""#version 330 core

        layout(location = 0) in vec3 aPosition;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec3 aNormal;

        
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;
        uniform mat4 uLightSpaceMatrix;

        out vec2 TexCoords;
        out vec3 Normal;
        out vec3 FragPos;
        out vec4 lightSpace ;

        void main()
        {
            FragPos = (uModel * vec4(aPosition, 1.0)).xyz;
            gl_Position = uProjection * uView *  vec4(FragPos, 1.0);
            lightSpace = uLightSpaceMatrix *  vec4(FragPos, 1.0);
            TexCoords = aTexCoord;
            Normal = mat3(transpose(inverse(uModel))) * aNormal;  
        }
        """

        fragment="""#version 330 core


        out vec4 FragColor;

        in vec4 lightSpace;
        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;

        uniform sampler2D diffuseMap;
        uniform sampler2D shadowMap;
        uniform vec3 lightPos;
        uniform vec3 viewPos;


    
        float CalculateShadowPCF(vec3 lightDir, vec3 normal,float cosTheta,float splitDistance);
        float PCF(const vec4 projShadow);
        float CalculateShadowPoissonDisk(vec3 lightDir, vec3 normal,float cosTheta, float splitDistance);
        float CalculateShadowRotatedPCF(vec3 lightDir, vec3 normal, float splitDistance);

        void main()
        {

            vec3 color = texture(diffuseMap, TexCoords).rgb;
            vec3 normal = normalize(Normal);
            vec3 lightColor = vec3(0.8);
            
            // Ambient
            vec3 ambient = 0.2 * lightColor;
            
            // Direção da luz
            vec3 lightDir = normalize(lightPos - FragPos);
            
            // Diffuse
            float cosTheta = max(dot(lightDir, normal), 0.0);
            vec3 diffuse = cosTheta * lightColor;
            
            // Specular
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 reflectDir = reflect(-lightDir, normal);
            
            float spec = 0.0;
            vec3 halfwayDir = normalize(lightDir + viewDir);  
            spec = pow(max(dot(normal, halfwayDir), 0.0), 256.0);
            vec3 specular = spec * lightColor;
                    



           //float shadow = CalculateShadowPCF( lightDir,normal, cosTheta, 0.1);
           // float shadow =CalculateShadowPoissonDisk(lightDir,normal, cosTheta, 0.1);
            float shadow = CalculateShadowRotatedPCF(lightDir,normal, 0.1);
            

            // Amostra a sombra com PCF
            //float shadow = PCF(projShadow);
            
            vec3 lighting = (ambient + (1.0 - shadow) * (diffuse + specular)) * color; 

            //vec3 lighting = (ambient + diffuse + specular) * color;

 
            FragColor = vec4(lighting, 1.0);
        }

 
        float dynamicBias(vec3 normal, vec3 lightDir, float cascadeSplitDistance, float baseBias) 
        {
            // Calcula o ângulo entre a direção da luz e a superfície
            float bias = max(baseBias * (1.0 - dot(normal, lightDir)), baseBias);

            // Reduz o bias com base na distância da cascata (splitDistance)
            bias *= 1.0 / (cascadeSplitDistance * 0.5);

            // Limitar o bias para evitar que se torne muito pequeno ou muito grande
            bias = clamp(bias, baseBias, baseBias * 10.0);

            return bias;
        }
        float CalculateShadowRotatedPCF(vec3 lightDir, vec3 normal, float splitDistance)
        {
            vec2 texelSize = 1.0 / textureSize(shadowMap, 0).xy;  // Obter o tamanho da shadow map
            vec3 projCoords = (lightSpace.xyz / lightSpace.w) * 0.5 + 0.5;  // Normaliza as coordenadas de sombra

            float currentDepth = projCoords.z;

            // Se estiver fora do frustum da shadow map, não calcular sombra
            if (currentDepth > 1.0)
            {
                return 0.0;
            }

            // Aplicar dynamic bias para evitar acne de sombras
            float bias = dynamicBias(normal, lightDir, splitDistance, 0.005);

            // Aplicar a técnica de PCF com grid rotacionada a 30°
            float shadow = texture(shadowMap, projCoords.xy).r;
            shadow += texture(shadowMap, projCoords.xy + vec2(-0.866 * texelSize.x,  0.5 * texelSize.y)).r;
            shadow += texture(shadowMap, projCoords.xy + vec2(-0.866 * texelSize.x, -0.5 * texelSize.y)).r;
            shadow += texture(shadowMap, projCoords.xy + vec2( 0.866 * texelSize.x, -0.5 * texelSize.y)).r;
            shadow += texture(shadowMap, projCoords.xy + vec2( 0.866 * texelSize.x,  0.5 * texelSize.y)).r;

            shadow /= 5.0;  // Normaliza para as 5 amostras

            // Compara a profundidade para determinar a sombra final
            return currentDepth - bias > shadow ? 1.0 : 0.0;
        }


       float CalculateShadowPCF(vec3 lightDir,vec3 normal,float cosTheta,float splitDistance)
       {
            vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
            
            vec3 projCoords = (lightSpace.xyz / lightSpace.w) * 0.5 + 0.5;
            

            float currentDepth = projCoords.z;

            // keep the shadow at 0.0 when outside the far_plane region of the light's frustum.
            if (currentDepth > 1.0)
            {
                return 0.0;
            }

            float bias = dynamicBias(normal, lightDir, splitDistance, 0.001);
            // float bias = max(0.05 * (1.0 - cosTheta), 0.005); 
//            float bias = max(0.05 * (1.0 - dot(normal, lightDir)), 0.005);
    //        float bias = max(0.05 * (1.0 - dot(normal, lightDir)), 0.01);  // ou 0.02

    //        const float biasModifier = 0.5f;
  //          bias *= 1 / (0.9 * biasModifier);
    

            float shadow = 0.0;
            for (int x = -2; x <= 2; ++x)
            {
                for (int y = -2; y <= 2; ++y)
                {
                    vec2 texel = projCoords.xy + vec2(x, y) * texelSize;
                    float pcfDepth = texture(shadowMap, texel).r;
                    shadow += (currentDepth - bias) > pcfDepth ? 1.0 : 0.0;
                }
            }
            shadow /= 25.0;  // Normaliza para 5x5 amostras

            return shadow;
       }

        float CalculateShadowPoissonDisk(vec3 lightDir, vec3 normal, float cosTheta, float splitDistance)
        {
    
            vec2 texelSize = 1.0 / textureSize(shadowMap, 0);

            // Projeção das coordenadas no espaço de luz
            vec3 projCoords = (lightSpace.xyz / lightSpace.w) * 0.5 + 0.5;

            // Profundidade atual do fragmento no espaço de luz
            float currentDepth = projCoords.z;

            // Se a profundidade for maior que 1.0, está fora  da luz
            if (currentDepth > 1.0)
            {
                return 0.0;
            }


            float bias = dynamicBias(normal, lightDir, splitDistance, 0.005);




            float shadow = 0.0;

            const int samples = 16;
            const vec2 poissonDisk[16] = vec2[](
                vec2(-0.94201624, -0.39906216), vec2(0.94558609, -0.76890725),                vec2(-0.094184101, -0.92938870), vec2(0.34495938, 0.29387760),
                vec2(-0.91588581, 0.45771432), vec2(-0.81544232, -0.87912464),                vec2(-0.38277543, 0.27676845), vec2(0.97484398, 0.75648379),
                vec2(0.44323325, -0.97511554), vec2(0.53742981, -0.47373420),                vec2(-0.26496911, -0.41893023), vec2(0.79197514, 0.19090188),
                vec2(-0.24188840, 0.99706507), vec2(-0.81409955, 0.91437590),                vec2(0.19984126, 0.78641367), vec2(0.14383161, -0.14100790)
            );

            for (int i = 0; i < samples; ++i)
            {
                vec2 offset = poissonDisk[i] * texelSize;
                float pcfDepth = texture(shadowMap, projCoords.xy + offset).r;
                shadow += (currentDepth - bias) > pcfDepth ? 1.0 : 0.0;
            }

        
            shadow /= float(samples);

            return shadow;
        }


    float PCF(const vec4 projShadow)
    {
        vec2 shadowMapSize = 1.0 / textureSize(shadowMap, 0).xy;
    
        // 5-tap PCF com grid rotacionado a 30° (reduzido)
        float offset = 0.5 * shadowMapSize.x;  // Reduz o offset para evitar sombras muito grandes


        float shadow = texture(shadowMap, projShadow.xy).r;
        shadow += texture(shadowMap, projShadow.xy + vec2(-0.866 * offset,  0.5 * offset)).r;
        shadow += texture(shadowMap, projShadow.xy + vec2(-0.866 * offset, -0.5 * offset)).r;
        shadow += texture(shadowMap, projShadow.xy + vec2( 0.866 * offset, -0.5 * offset)).r;
        shadow += texture(shadowMap, projShadow.xy + vec2( 0.866 * offset,  0.5 * offset)).r;

        return shadow / 5.0;
    }
     
        """
        self.create_shader(vertex,fragment)
    
       
       


class PointShadowShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL] 

  
        vertex="""#version 330 core

        layout(location = 0) in vec3 aPosition;
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
            FragPos = (uModel * vec4(aPosition, 1.0)).xyz;
            gl_Position = uProjection * uView *  vec4(FragPos, 1.0);
            TexCoords = aTexCoord;
            Normal = mat3(transpose(inverse(uModel))) * aNormal;  
        }
        """

        fragment="""#version 330 core


        out vec4 FragColor;


        in vec2 TexCoords;
        in vec3 Normal;
        in vec3 FragPos;

        uniform sampler2D diffuseMap;
        uniform samplerCube shadowMap;
        uniform vec3 lightPos;
        uniform vec3 viewPos;
        uniform float far_plane;          
     

        float ShadowCalculation(vec3 fragPos) ;

        void main()
        {
            
            vec3 color = texture(diffuseMap, TexCoords).rgb;
            vec3 normal = normalize(Normal);
            vec3 lightColor = vec3(0.8);
            
        // ambient
        vec3 ambient = 0.3 * lightColor;
        
        // diffuse
        vec3 lightDir = normalize(lightPos - FragPos);
        float diff = max(dot(lightDir, normal), 0.0);
        vec3 diffuse = diff * lightColor;
        
        // specular
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, normal);
        float spec = 0.0;
        vec3 halfwayDir = normalize(lightDir + viewDir);  
        spec = pow(max(dot(normal, halfwayDir), 0.0), 128.0);
        vec3 specular = spec * lightColor;    
        
        // calculate shadow
        float shadow =  ShadowCalculation(FragPos) ;                      
        vec3 lighting = (ambient + (1.0 - shadow) * (diffuse + specular)) * color;    
        
        //    vec3 lighting = (ambient + diffuse + specular) * color;
        
            
            FragColor = vec4(lighting, 1.0);
            
        }


        float ShadowCalculation(vec3 fragPos) 
        {
            const vec3 gridSamplingDisk[20] = vec3[]
            (
            vec3(1, 1,  1), vec3( 1, -1,  1), vec3(-1, -1,  1), vec3(-1, 1,  1), 
            vec3(1, 1, -1), vec3( 1, -1, -1), vec3(-1, -1, -1), vec3(-1, 1, -1),
            vec3(1, 1,  0), vec3( 1, -1,  0), vec3(-1, -1,  0), vec3(-1, 1,  0),
            vec3(1, 0,  1), vec3(-1,  0,  1), vec3( 1,  0, -1), vec3(-1, 0, -1),
            vec3(0, 1,  1), vec3( 0, -1,  1), vec3( 0, -1, -1), vec3( 0, 1, -1)
            );
            vec3 fragToLight = fragPos - lightPos;
            float currentDepth = length(fragToLight);
            float shadow = 0.0;
            float bias = 0.05;
            int samples = 20;
            float viewDistance = length(lightPos - fragPos);
            float diskRadius = (1.0 + (viewDistance / far_plane)) / 25.0;
            for(int i = 0; i < samples; ++i)
            {
                float closestDepth = texture(shadowMap, fragToLight + gridSamplingDisk[i] * diskRadius).r;
                closestDepth *= far_plane;   // undo mapping [0;1]
                //FragColor = vec4(vec3(closestDepth / far_plane), 1.0);  // debug
                if(currentDepth - bias > closestDepth)
                    shadow += 1.0;
            }
            shadow /= float(samples);
       

              

            return shadow;
        }
     
        """
        self.create_shader(vertex,fragment)
        self.set_float("far_plane", 10.0)

            



class LightData:
    def __init__(self):
        self.camera = glm.vec3(0,0,0)
        self.type   = LightType.NONE
        self.enable = True
        self.shader = None
    
    def update(self):
        pass

class AmbientLightData(LightData):
    def __init__(self):
        super().__init__()
        self.ambient=glm.vec3(0.2,0.2,0.2)
        self.type = LightType.AMBIENT
        self.enable = True
        self.shader = AmbientShader()
        self.update()
    def update(self):
        self.shader.set_vector3f("ambient", self.ambient)



class DirectionalLightData(LightData):
    def __init__(self):
        super().__init__()
        self.shader = DirectionalShader()
        self.direction=glm.vec3(1,1,1)
        self.type = LightType.DIRECTIONAL
        self.shininess = 32.0
        self.ambient=glm.vec3(0.2,0.2,0.2)
        self.diffuse=glm.vec3(0.2,0.2,0.2)
        self.specular=glm.vec3(1.0,1.0,1.0)
        self.update()

    def update(self):
        self.shader.set_vector3f("viewPos",self.camera)
        self.shader.set_vector3f("directional.direction", self.direction)
        self.shader.set_vector3f("directional.ambient", self.ambient)
        self.shader.set_vector3f("directional.diffuse", self.diffuse)
        self.shader.set_vector3f("directional.specular", self.specular)
        self.shader.set_float("shininess", self.shininess)


class PointLightData(LightData):
    def __init__(self):
        super().__init__()
        self.shader = PointShader()
        self.position =glm.vec3(0,0,0)
        self.ambient =glm.vec3(0.2,0.2,0.2)
        self.diffuse =glm.vec3(0.8,0.8,0.8)
        self.specular=glm.vec3(1.0,1.0,1.0)
        
        self.type = LightType.POINT
        self.shininess = 32.0
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032
        self.range = 100.0
        self.update()

    def update(self):
        self.shader.set_vector3f("viewPos",self.camera)
        self.shader.set_vector3f("point.position", self.position)
        self.shader.set_vector3f("point.ambient", self.ambient)
        self.shader.set_vector3f("point.diffuse", self.diffuse)
        self.shader.set_vector3f("point.specular", self.specular)

        self.shader.set_float("point.shininess", self.shininess)
        self.shader.set_float("point.constant", self.constant)
        self.shader.set_float("point.linear", self.linear)
        self.shader.set_float("point.quadratic", self.quadratic)
        self.shader.set_float("point.range", self.range)



class SpotLightData(LightData):
    def __init__(self):
        super().__init__()
        self.shader = SpotShader()
        self.position=glm.vec3(0,0,0)
        self.direction=glm.vec3(0,0,0)
        self.ambient=glm.vec3(0.2,0.2,0.2)
        self.diffuse=glm.vec3(0.8,0.8,0.8)
        self.specular=glm.vec3(1.0,1.0,1.0)
        self.cutOff = math.cos(math.radians(12.5))
        self.outerCutOff= math.cos(math.radians(17.5))
        self.type = LightType.SPOT
        self.shininess = 32.0
        self.constant = 1.0
        self.linear = 0.009
        self.quadratic = 0.032  
        self.update() 

    def update(self):
        self.shader.set_vector3f("viewPos",self.camera)
        self.shader.set_vector3f("spot.position", self.position)
        self.shader.set_vector3f("spot.direction", self.direction)
        self.shader.set_vector3f("spot.ambient", self.ambient)
        self.shader.set_vector3f("spot.diffuse", self.diffuse)
        self.shader.set_vector3f("spot.specular", self.specular)
        self.shader.set_float("spot.shininess", self.shininess)
        self.shader.set_float("spot.constant", self.constant)
        self.shader.set_float("spot.linear", self.linear)
        self.shader.set_float("spot.quadratic", self.quadratic)
        self.shader.set_float("spot.cutOff", self.cutOff)
        self.shader.set_float("spot.outerCutOff", self.outerCutOff)



#**********************************************************************************************************************************
#                                               PBR



        
        

class DirectionalPbrShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL,Attribute.TANGENT] 

        vertex="""#version 330 core

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec3 aNormal;
        layout(location = 3) in vec3 aTangent;

        
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;

        out vec2 TexCoords;
        out vec3 FragPos;
        out vec3 Normal;
        out mat3 TBN;

        void main()
        {
            TexCoords = aTexCoord;
            
                vec3 T = normalize(mat3(transpose(inverse(uModel))) * aTangent);
                vec3 N = normalize(mat3(transpose(inverse(uModel))) * aNormal);
                vec3 B = cross(N, T);

                TBN = mat3(T, B, N);
                
                Normal = N;
            


            FragPos = vec3(uModel * vec4(aPos, 1.0));
            gl_Position =  uProjection * uView  *  vec4(FragPos, 1.0);
        }
        """

        fragment="""#version 330 core
        out vec4 FragColor;

        in vec2 TexCoords;
        in mat3 TBN;
        in vec3 FragPos;
        in vec3 Normal;
        uniform sampler2D albedoMap;
        uniform sampler2D normalMap;

        uniform vec3 viewPos;
        uniform vec3 lightDir;  
        uniform vec3 lightColor;  
        uniform float normalStrength;
        uniform float fixedMetalness;
        uniform float fixedRoughness;
        uniform float lightIntensity; 

        const float PI = 3.14159265359;
  
        vec3 GetNormalFromMap()
        {
            vec3 tangentNormal = texture(normalMap, TexCoords).xyz * 2.0 - 1.0;
            tangentNormal = mix(vec3(0.0, 0.0, 1.0), tangentNormal, normalStrength); 
            return normalize(TBN * tangentNormal);
        }
    vec3 FresnelSchlick(float cosTheta, vec3 F0)
    {
        return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
    }

    
    float DistributionGGX(vec3 N, vec3 H, float roughness)
    {
        float a = roughness * roughness;
        float a2 = a * a;
        float NdotH = max(dot(N, H), 0.0);
        float NdotH2 = NdotH * NdotH;

        float num = a2;
        float denom = (NdotH2 * (a2 - 1.0) + 1.0);
        denom = PI * denom * denom;

        return num / denom;
    }

    
    float GeometrySchlickGGX(float NdotV, float roughness)
    {
        float r = roughness + 1.0;
        float k = (r * r) / 8.0;

        float num = NdotV;
        float denom = NdotV * (1.0 - k) + k;

        return num / denom;
    }


    float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
    {
        float NdotV = max(dot(N, V), 0.0);
        float NdotL = max(dot(N, L), 0.0);
        float ggx2 = GeometrySchlickGGX(NdotV, roughness);
        float ggx1 = GeometrySchlickGGX(NdotL, roughness);

        return ggx1 * ggx2;
    }
        void main()
        {
           
            vec3 albedo = texture(albedoMap, TexCoords).rgb;
            vec3 normal = GetNormalFromMap();
            
            
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 lightDirNorm = normalize(-lightDir);

            // Calcular o termo de Fresnel
            vec3 F0 = vec3(0.04);  // Valor base para dielétricos
            F0 = mix(F0, albedo, fixedMetalness);  // Metais usam a cor do albedo como F0
            vec3 H = normalize(viewDir + lightDirNorm);
            float NDF = DistributionGGX(normal, H, fixedRoughness);
            float G = GeometrySmith(normal, viewDir, lightDirNorm, fixedRoughness);
            vec3 F = FresnelSchlick(max(dot(H, viewDir), 0.0), F0);

            // Specular do PBR
            vec3 nominator = NDF * G * F;
            float denominator = 4.0 * max(dot(normal, viewDir), 0.0) * max(dot(normal, lightDirNorm), 0.0) + 0.001;
            vec3 specular = nominator / denominator;

            // Difusa do PBR (Lambertian BRDF)
            vec3 kS = F;
            vec3 kD = vec3(1.0) - kS;
            kD *= 1.0 - fixedMetalness;  // Sem difusa em materiais metálicos

            float NdotL = max(dot(normal, lightDirNorm), 0.0);
            vec3 diffuse = (kD * albedo / PI) * NdotL;

            
            vec3 lighting = (diffuse + specular) * lightColor * lightIntensity;

            FragColor = vec4(lighting, 1.0);
        }

         
     
        """
        self.create_shader(vertex,fragment)
        self.set_vector3f("viewPos",glm.vec3(0.0,0.0,0.0))
        self.set_vector3f("lightDir",glm.vec3(0.0,-0.9,0.2))
        self.set_vector3f("lightColor",glm.vec3(1.0,1.0,1.0))
        self.set_float("normalStrength",0.2)
        self.set_float("fixedMetalness",0.0)
        self.set_float("fixedRoughness",0.5)
        self.set_float("lightIntensity",2.5)
        self.set_int("albedoMap",0)
        self.set_int("normalMap",1)
       

        

class DirectionalPbrShadowShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION3D,Attribute.TEXCOORD0,Attribute.NORMAL,Attribute.TANGENT] 

        vertex="""#version 330 core

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec2 aTexCoord;
        layout(location = 2) in vec3 aNormal;
        layout(location = 3) in vec3 aTangent;

        
        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform mat4 uModel;
        uniform mat4 uLightSpaceMatrix;

        out vec2 TexCoords;
        out vec3 FragPos;
        out vec3 Normal;
        out mat3 TBN;
        out vec4 lightSpace ;

        void main()
        {
            TexCoords = aTexCoord;
            
                vec3 T = normalize(mat3(transpose(inverse(uModel))) * aTangent);
                vec3 N = normalize(mat3(transpose(inverse(uModel))) * aNormal);
                vec3 B = cross(N, T);

                TBN = mat3(T, B, N);
                
                Normal = N;
            
                FragPos = vec3(uModel * vec4(aPos, 1.0));
                lightSpace = uLightSpaceMatrix *  vec4(FragPos, 1.0);

                gl_Position =  uProjection * uView  *  vec4(FragPos, 1.0);
        }
        """

        fragment="""#version 330 core
        out vec4 FragColor;

        in vec2 TexCoords;
        in mat3 TBN;
        in vec3 FragPos;
        in vec3 Normal;
        in vec4 lightSpace;
        
        uniform sampler2D albedoMap;
        uniform sampler2D normalMap;
        uniform sampler2D shadowMap;

        uniform vec3 viewPos;
        uniform vec3 lightPos;
        uniform vec3 lightColor;  
        uniform float normalStrength;
        uniform float fixedMetalness;
        uniform float fixedRoughness;
        uniform float lightIntensity; 
        const float PI = 3.14159265359;

        float CalculateShadowPCF(vec3 lightDir, vec3 normal,float cosTheta,float splitDistance);

        float CalculateShadowPoissonDisk(vec3 lightDir, vec3 normal,float cosTheta, float splitDistance);

  
        vec3 GetNormalFromMap()
        {
            vec3 tangentNormal = texture(normalMap, TexCoords).xyz * 2.0 - 1.0;
            tangentNormal = mix(vec3(0.0, 0.0, 1.0), tangentNormal, normalStrength); 
            return normalize(TBN * tangentNormal);
        }
    vec3 FresnelSchlick(float cosTheta, vec3 F0)
    {
        return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
    }

    
    float DistributionGGX(vec3 N, vec3 H, float roughness)
    {
        float a = roughness * roughness;
        float a2 = a * a;
        float NdotH = max(dot(N, H), 0.0);
        float NdotH2 = NdotH * NdotH;

        float num = a2;
        float denom = (NdotH2 * (a2 - 1.0) + 1.0);
        denom = PI * denom * denom;

        return num / denom;
    }

    
    float GeometrySchlickGGX(float NdotV, float roughness)
    {
        float r = roughness + 1.0;
        float k = (r * r) / 8.0;

        float num = NdotV;
        float denom = NdotV * (1.0 - k) + k;

        return num / denom;
    }


    float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
    {
        float NdotV = max(dot(N, V), 0.0);
        float NdotL = max(dot(N, L), 0.0);
        float ggx2 = GeometrySchlickGGX(NdotV, roughness);
        float ggx1 = GeometrySchlickGGX(NdotL, roughness);

        return ggx1 * ggx2;
    }
        void main()
        {
           
            vec3 albedo = texture(albedoMap, TexCoords).rgb;
            vec3 normal = GetNormalFromMap();
            
            // Direção da luz
            vec3 lightDir = normalize(FragPos-lightPos);
            
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 lightDirNorm = normalize(-lightDir);

            // Calcular o termo de Fresnel
            vec3 F0 = vec3(0.04);  // Valor base para dielétricos
            F0 = mix(F0, albedo, fixedMetalness);  // Metais usam a cor do albedo como F0
            vec3 H = normalize(viewDir + lightDirNorm);
            float NDF = DistributionGGX(normal, H, fixedRoughness);
            float G = GeometrySmith(normal, viewDir, lightDirNorm, fixedRoughness);
            vec3 F = FresnelSchlick(max(dot(H, viewDir), 0.0), F0);

            // Specular do PBR
            vec3 nominator = NDF * G * F;
            float denominator = 4.0 * max(dot(normal, viewDir), 0.0) * max(dot(normal, lightDirNorm), 0.0) + 0.001;
            vec3 specular = nominator / denominator;

            // Difusa do PBR (Lambertian BRDF)
            vec3 kS = F;
            vec3 kD = vec3(1.0) - kS;
            kD *= 1.0 - fixedMetalness;  // Sem difusa em materiais metálicos

            float NdotL = max(dot(normal, lightDirNorm), 0.0);
            vec3 diffuse = (kD * albedo / PI) * NdotL;

            //float shadow = CalculateShadowPCF( lightDir,normal, NdotL, 0.1);
            float shadow =CalculateShadowPoissonDisk(lightDir,normal, NdotL, 0.1);

              // Ambient
            //vec3 ambient =0.2 *  lightColor * lightIntensity;

            // vec3 lighting = (1.0 - shadow) * (diffuse + specular) * lightColor * lightIntensity;

            // vec3 lighting = (ambient + shadow)  * (diffuse + specular)) ; 
            
            //vec3 lighting = (diffuse + specular) * lightColor * lightIntensity;

                        // Calcule a intensidade de luz com sombra
            vec3 shadowFactor = mix(vec3(1.0), vec3(1.0 - shadow), shadow); 

            // Iluminação com sombra aplicada
            vec3 lighting = (diffuse + specular) * lightColor * lightIntensity * shadowFactor;

            FragColor = vec4(lighting, 1.0);
        }

           float dynamicBias(vec3 normal, vec3 lightDir, float cascadeSplitDistance, float baseBias) 
        {
            // Calcula o ângulo entre a direção da luz e a superfície
            float bias = max(baseBias * (1.0 - dot(normal, lightDir)), baseBias);

            // Reduz o bias com base na distância da cascata (splitDistance)
            bias *= 1.0 / (cascadeSplitDistance * 0.5);

            // Limitar o bias para evitar que se torne muito pequeno ou muito grande
            bias = clamp(bias, baseBias, baseBias * 10.0);

            return bias;
        }

       float CalculateShadowPCF(vec3 lightDir,vec3 normal,float cosTheta,float splitDistance)
       {
            vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
            
            vec3 projCoords = (lightSpace.xyz / lightSpace.w) * 0.5 + 0.5;
            

            float currentDepth = projCoords.z;

            // keep the shadow at 0.0 when outside the far_plane region of the light's frustum.
            if (currentDepth > 1.0)
            {
                return 0.0;
            }

            float bias = dynamicBias(normal, lightDir, splitDistance, 0.005);


            float shadow = 0.0;
            for (int x = -2; x <= 2; ++x)
            {
                for (int y = -2; y <= 2; ++y)
                {
                    vec2 texel = projCoords.xy + vec2(x, y) * texelSize;
                    float pcfDepth = texture(shadowMap, texel).r;
                    shadow += (currentDepth - bias) > pcfDepth ? 1.0 : 0.0;
                }
            }
            shadow /= 25.0;  // Normaliza para 5x5 amostras

            return shadow;
       }

        float CalculateShadowPoissonDisk(vec3 lightDir, vec3 normal, float cosTheta, float splitDistance)
        {
    
            vec2 texelSize = 1.0 / textureSize(shadowMap, 0);

            // Projeção das coordenadas no espaço de luz
            vec3 projCoords = (lightSpace.xyz / lightSpace.w) * 0.5 + 0.5;

            // Profundidade atual do fragmento no espaço de luz
            float currentDepth = projCoords.z;

            // Se a profundidade for maior que 1.0, está fora  da luz
            if (currentDepth > 1.0)
            {
                return 0.0;
            }


            float bias = dynamicBias(normal, lightDir, splitDistance, 0.005);




            float shadow = 0.0;

            const int samples = 16;
            const vec2 poissonDisk[16] = vec2[](
                vec2(-0.94201624, -0.39906216), vec2(0.94558609, -0.76890725),                vec2(-0.094184101, -0.92938870), vec2(0.34495938, 0.29387760),
                vec2(-0.91588581, 0.45771432), vec2(-0.81544232, -0.87912464),                vec2(-0.38277543, 0.27676845), vec2(0.97484398, 0.75648379),
                vec2(0.44323325, -0.97511554), vec2(0.53742981, -0.47373420),                vec2(-0.26496911, -0.41893023), vec2(0.79197514, 0.19090188),
                vec2(-0.24188840, 0.99706507), vec2(-0.81409955, 0.91437590),                vec2(0.19984126, 0.78641367), vec2(0.14383161, -0.14100790)
            );

            for (int i = 0; i < samples; ++i)
            {
                vec2 offset = poissonDisk[i] * texelSize;
                float pcfDepth = texture(shadowMap, projCoords.xy + offset).r;
                shadow += (currentDepth - bias) > pcfDepth ? 1.0 : 0.0;
            }

        
            shadow /= float(samples);

            return shadow;
        }

         
     
        """
        self.create_shader(vertex,fragment)
        self.set_vector3f("viewPos",glm.vec3(0.0,0.0,0.0))
        self.set_vector3f("lightDir",glm.vec3(0.0,-0.9,0.2))
        self.set_vector3f("lightColor",glm.vec3(1.0,1.0,1.0))
        self.set_float("normalStrength",0.2)
        self.set_float("fixedMetalness",0.0)
        self.set_float("fixedRoughness",0.5)
        self.set_float("lightIntensity",2.5)
        self.set_int("albedoMap",0)
        self.set_int("normalMap",1)
        self.set_int("shadowMap",2)
       


class FlareShader(Shader):
    def __init__(self):
        super().__init__()
        self.attributes=[Attribute.POSITION2D,Attribute.TEXCOORD0] 

        vertex="""#version 330

        layout(location = 0) in vec2 aPos;  
        layout (location = 1) in vec2 aTexCoord;
        layout (location = 2) in vec4 aColor;
        uniform mat4 uOrthoMatrix;

        out vec2 TexCoords;
        out vec4 color;

        void main()
        {
          
            gl_Position = uOrthoMatrix * vec4(aPos, 0.0, 1.0);
            TexCoords = aTexCoord;
            color = aColor;
        }
        """

        fragment="""#version 330


            in vec2 TexCoords;
            in vec4 color;
            out vec4 FragColor;

            uniform sampler2D image;  
            

            void main()
            {
                vec4 texColor = texture(image, TexCoords);
                FragColor = texColor * color;
            }
        """
        self.create_shader(vertex,fragment)

  