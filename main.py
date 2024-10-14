import core 
from core import *
from mesh import *
import sys
    

core = Core(720, 480, "OpenGL Demo")
render = core.render



texture = Texture()
texture.load("assets/wabbit_alpha.png")

mesh = Mesh(TextureColorMaterial(texture))


mesh.vertices = [    -0.5, -0.5, 0.0, 
                      0.5, -0.5, 0.0, 
                      0.5,  0.5, 0.0, 
                     -0.5,  0.5, 0.0 ]

mesh.colors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0]

mesh.texcoord0 = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]

mesh.indices = [0, 1, 2, 2, 3, 0]



mesh.update()

render.set_blend(True)
render.set_blend_mode(BlendMode.Normal)

while core.run():
    render.set_viewport(0, 0, core.width, core.height)
    render.clear(0.0, 0.0, 0.4)
    mesh.render()
    core.flip()

core.close() 

