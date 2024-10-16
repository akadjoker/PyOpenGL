from OpenGL.GL import *


class Shader:
    def __init__(self):
        self.program = glCreateProgram()
        self.uniforms = {}

    def use(self):
        glUseProgram(self.program)


    def create_shader(self, vertString, fragString):
        vert = self.loadShaderFromString(vertString, GL_VERTEX_SHADER)
        frag = self.loadShaderFromString(fragString, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, vert)
        glAttachShader(self.program, frag)
        glLinkProgram(self.program)
        result = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not result:
            log = glGetProgramInfoLog(self.program)
            print(f"Erro na compilação do shader: {log.decode()}")
            return
        glDeleteShader(vert)
        glDeleteShader(frag)
        glUseProgram(self.program)
        self.load_uniforms()

    def load_shader(self, vertName, fragName):
        vert = self.loadShaderFromFile(vertName, GL_VERTEX_SHADER)
        frag = self.loadShaderFromFile(fragName, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, vert)
        glAttachShader(self.program, frag)
        glLinkProgram(self.program)
        result = glGetProgramiv(self.program, GL_LINK_STATUS) 
        if not result:
            log = glGetProgramInfoLog(self.program)
            print(f"Erro na compilação do shader: {log.decode()}")
            return

        glDeleteShader(vert)
        glDeleteShader(frag)

        glUseProgram(self.program)
        self.load_uniforms()



    def loadShaderFromString(self, source, shaderType):
        shader = glCreateShader(shaderType)
        glShaderSource(shader, source)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not result:
            log = glGetShaderInfoLog(shader)
            print(f"Erro na compilação do shader: {log.decode()}")
            return None
        return shader

    def loadShaderFromFile(self, fileName, shaderType):
        with open(fileName, 'r') as file:
            source = file.read()
        shader = glCreateShader(shaderType)
        glShaderSource(shader, source)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not result:
            log = glGetShaderInfoLog(shader)
            print(f"Erro na compilação do shader: {log.decode()}")
            return None
        return shader

    def load_uniforms(self):
            program = self.program
            num_uniforms = glGetProgramiv(program, GL_ACTIVE_UNIFORMS)
            for i in range(num_uniforms):
                uniform_name, uniform_type = glGetActiveUniform(program, i)[:2]
                name = uniform_name.decode()
                uniform_location = glGetUniformLocation(program, uniform_name)
                self.uniforms[name] = uniform_location
            print(self.uniforms)

    def set_matrix4fv(self, name, matrix):
        location = self.uniforms.get(name)
        if location is not None:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)
        #else:
        #    print(f"Uniform '{name}' not found.")

    def set_float(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform1f(location, value)
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_int(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform1i(location, value)
        else:
            print(f"Uniform '{name}' not found.")


    def set_vector2f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform2f(location, value[0], value[1])
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_vector3f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform3f(location, value[0], value[1], value[2])
        else:
            print(f"Uniform '{name}' not found.")
    
    def set_vector4f(self, name, value):
        location = self.uniforms.get(name)
        if location is not None:
            glUniform4f(location, value[0], value[1], value[2], value[3])
        else:
            print(f"Uniform '{name}' not found.")
