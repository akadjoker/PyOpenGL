from PIL import Image, ImageOps
import numpy as np

# Função para calcular o normal map a partir de uma imagem em tons de cinza
def generate_normal_map(image, strength=1.0):
    # Converte a imagem para grayscale
    gray_image = ImageOps.grayscale(image)

    # Converte a imagem para um array numpy
    pixels = np.asarray(gray_image, dtype=np.float32)

    # Normaliza os pixels para a faixa [0, 1]
    pixels /= 255.0

    # Gradientes (simples aproximação)
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

    grad_x = np.zeros_like(pixels)
    grad_y = np.zeros_like(pixels)

    # Aplica os filtros de Sobel para gradientes
    for y in range(1, pixels.shape[0] - 1):
        for x in range(1, pixels.shape[1] - 1):
            region = pixels[y-1:y+2, x-1:x+2]
            grad_x[y, x] = np.sum(sobel_x * region)
            grad_y[y, x] = np.sum(sobel_y * region)

    # Normaliza os gradientes
    grad_x *= strength
    grad_y *= strength

    # Cria um normal map
    normals = np.zeros((pixels.shape[0], pixels.shape[1], 3), dtype=np.float32)

    normals[..., 0] = grad_x  # Componente X
    normals[..., 1] = grad_y  # Componente Y
    normals[..., 2] = 1.0     # Componente Z (fixa, simula altura)

    # Normaliza as normais para [0, 1]
    norm = np.sqrt(normals[..., 0] ** 2 + normals[..., 1] ** 2 + normals[..., 2] ** 2)
    normals[..., 0] /= norm
    normals[..., 1] /= norm
    normals[..., 2] /= norm

    # Converte para o intervalo [0, 255] e salva como imagem
    normals = ((normals + 1.0) * 0.5 * 255.0).astype(np.uint8)

    normal_map = Image.fromarray(normals, mode='RGB')
    return normal_map

# Função para gerar specular map
def generate_specular_map(image):
    # Converte a imagem para grayscale (para usar como specular map)
    specular_map = ImageOps.grayscale(image)

    # Ajustar o contraste para gerar um mapa especular
    specular_map = ImageOps.autocontrast(specular_map, cutoff=5)

    return specular_map

filename = 'assets/defaultTexture.png'
image = Image.open(filename)

name = filename.split(".")[0]
directory = ''

# Gerar o normal map
normal_map = generate_normal_map(image, strength=1.0)
normal_map.save(f"{directory}{name}_normal.png")

# Gerar o specular map
specular_map = generate_specular_map(image)
specular_map.save(f"{directory}{name}_specular.png")

print("Normal map and Specular map generated successfully!")
