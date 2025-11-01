import pygame
from OpenGL.GL import *
import numpy as np

def identity_matrix():
    return np.identity(4, dtype=np.float32)

def translate(matrix, x, y, z):
    translation = np.identity(4, dtype=np.float32)
    translation[0, 3] = x
    translation[1, 3] = y
    translation[2, 3] = z
    return np.dot(matrix, translation)

def rotate(matrix, angle, axis, local=True):
    angle_rad = np.radians(angle)
    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)
    
    rotation = np.identity(4, dtype=np.float32)
    
    if axis == "x" or axis == 0:
        rotation[1, 1] = cos_angle
        rotation[1, 2] = -sin_angle
        rotation[2, 1] = sin_angle
        rotation[2, 2] = cos_angle
    elif axis == "y" or axis == 1:
        rotation[0, 0] = cos_angle
        rotation[0, 2] = sin_angle
        rotation[2, 0] = -sin_angle
        rotation[2, 2] = cos_angle
    elif axis == "z" or axis == 2:
        rotation[0, 0] = cos_angle
        rotation[0, 1] = -sin_angle
        rotation[1, 0] = sin_angle
        rotation[1, 1] = cos_angle
    
    if local:
        return np.dot(matrix, rotation)
    else:
        return np.dot(rotation, matrix)

class Rotation:
    def __init__(self, angle, axis):
        self.angle = angle
        self.axis = axis

class WaterSphere:
    def __init__(self, program_id, radius=1.0, slices=128, stacks=64, 
                 location=pygame.Vector3(0, 0, 0), 
                 move_rotation=None, move_translate=None):
        self.program_id = program_id
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        self.location = location
        self.move_rotation = move_rotation
        self.move_translate = move_translate
        
        # 🌊 PROPIEDADES VISUALES
        self.water_color = pygame.Vector3(0.2, 0.4, 0.8)
        
        self.vertex_data = None
        self.index_data = None
        self.vertex_count = 0
        
        self.create_geometry()
        self.setup_buffers()
        
        print(f"🌊 Esfera de agua creada: {self.slices}x{self.stacks} resolución")

    def create_geometry(self):
        vertices = []
        normals = []
        texcoords = []
        indices = []
        
        # Generar geometría
        for i in range(self.stacks + 1):
            v = i / self.stacks  # 0 a 1
            phi = v * np.pi      # 0 a π
            
            for j in range(self.slices + 1):
                u = j / self.slices  # 0 a 1
                theta = u * 2 * np.pi  # 0 a 2π
                
                # Coordenadas esféricas
                x = self.radius * np.sin(phi) * np.cos(theta)
                y = self.radius * np.cos(phi)
                z = self.radius * np.sin(phi) * np.sin(theta)
                
                # Normal
                normal = pygame.Vector3(x, y, z).normalize()
                
                # Coordenadas UV
                uv_x = u
                uv_y = 1.0 - v  # Invertir V para mapping correcto
                
                vertices.extend([x, y, z])
                normals.extend([normal.x, normal.y, normal.z])
                texcoords.extend([uv_x, uv_y])
        
        # Generar índices
        for i in range(self.stacks):
            for j in range(self.slices):
                first = i * (self.slices + 1) + j
                second = first + self.slices + 1
                
                # Dos triángulos por cuadrilátero
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        
        # Intercalar datos: posición(3) + normal(3) + uv(2)
        interleaved = []
        vertex_count = len(vertices) // 3
        
        for i in range(vertex_count):
            # Posición
            interleaved.extend(vertices[i*3 : i*3+3])
            # Normal
            interleaved.extend(normals[i*3 : i*3+3])
            # UV
            interleaved.extend(texcoords[i*2 : i*2+2])
        
        self.vertex_data = np.array(interleaved, dtype=np.float32)
        self.index_data = np.array(indices, dtype=np.uint32)
        self.vertex_count = len(indices)

    def setup_buffers(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_STATIC_DRAW)
        
        # EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_data.nbytes, self.index_data, GL_STATIC_DRAW)
        
        # Atributos
        stride = 8 * 4  # 3pos + 3normal + 2uv = 8 floats * 4 bytes
        
        # Posición (location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Normal (location = 1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        
        # UV (location = 2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)
        
        glBindVertexArray(0)

    def draw(self):
        glUseProgram(self.program_id)
        
        # Matriz de modelo
        model_mat = identity_matrix()
        
        if self.move_rotation is not None:
            model_mat = rotate(model_mat, self.move_rotation.angle, 
                             self.move_rotation.axis, True)
        
        model_mat = translate(model_mat, self.location.x, self.location.y, self.location.z)
        
        model_mat_loc = glGetUniformLocation(self.program_id, "model_mat")
        glUniformMatrix4fv(model_mat_loc, 1, GL_TRUE, model_mat)
        
        # Dibujar
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.vertex_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)