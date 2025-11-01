import pygame
from OpenGL.GL import *
import numpy as np

class Rotation:
    def __init__(self, angle, axis):
        self.angle = angle
        self.axis = axis

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

class Sphere:
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
        
        # 🎯 COLOR METÁLICO ÚNICO
        self.metal_color = pygame.Vector3(0.7, 0.7, 0.8)  # Plateado
        self.shininess = 256
        self.specular_strength = 1.2
        
        self.vertex_attributes = []
        self.index_data = []
        
        self.create_geometry()
        self.setup_buffers()
        
        print(f"🎯 Esfera metálica creada - Color: ({self.metal_color.x}, {self.metal_color.y}, {self.metal_color.z})")

    def create_geometry(self):
        vertices = []
        normals = []
        indices = []
        
        # SOLO vértices y normales - SIN colores por vértice
        for i in range(self.stacks + 1):
            phi = np.pi * i / self.stacks
            
            for j in range(self.slices + 1):
                theta = 2 * np.pi * j / self.slices
                
                x = self.radius * np.sin(phi) * np.cos(theta)
                y = self.radius * np.cos(phi)
                z = self.radius * np.sin(phi) * np.sin(theta)
                
                normal = pygame.Vector3(x, y, z).normalize()
                
                vertices.extend([x, y, z])
                normals.extend([normal.x, normal.y, normal.z])
        
        # Generar índices
        for i in range(self.stacks):
            for j in range(self.slices):
                first = i * (self.slices + 1) + j
                second = first + self.slices + 1
                
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        
        self.vertex_attributes = vertices + normals
        self.index_data = indices
        self.vertex_count = len(indices)

    def setup_buffers(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # VBO - solo posiciones y normales
        vertex_data = np.array(self.vertex_attributes, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
        
        # EBO
        index_data = np.array(self.index_data, dtype=np.uint32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)
        
        # Atributos - SOLO 2: posición y normal
        stride = 6 * 4  # 6 floats * 4 bytes (3 pos + 3 normal)
        
        # Posición (location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Normal (location = 1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)

    def draw(self):
        glUseProgram(self.program_id)
        
        # 🎯 PASAR COLOR METÁLICO COMO UNIFORM
        metal_color_loc = glGetUniformLocation(self.program_id, "metal_color")
        shininess_loc = glGetUniformLocation(self.program_id, "material_shininess")
        specular_loc = glGetUniformLocation(self.program_id, "material_specular_strength")
        
        glUniform3f(metal_color_loc, self.metal_color.x, self.metal_color.y, self.metal_color.z)
        glUniform1f(shininess_loc, self.shininess)
        glUniform1f(specular_loc, self.specular_strength)
        
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