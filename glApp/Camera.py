import numpy as np
import pygame
from OpenGL.GL import *  # ← AGREGAR ESTA LÍNEA
from OpenGL.GLU import *
from math import *

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

class Uniform:
    def __init__(self, data_type, data):
        self.data_type = data_type
        self.data = data
        self.variable_id = None
    
    def find_variable(self, program_id, variable_name):
        self.variable_id = glGetUniformLocation(program_id, variable_name)
    
    def load(self):
        if self.data_type == "mat4":
            glUniformMatrix4fv(self.variable_id, 1, GL_TRUE, self.data)

class Camera:
    def __init__(self, program_id, w, h):
        self.transformation = identity_matrix()
        # 🎯 POSICIÓN INICIAL MÁS ATRÁS
        self.transformation = translate(self.transformation, 0, 0, -5)
        
        self.last_mouse = pygame.math.Vector2(0, 0)
        self.mouse_sensitivityX = 0.1
        self.mouse_sensitivityY = 0.1
        self.key_sensitivity = 0.008
        self.projection_mat = self.perspective_mat(60, w / h, 0.01, 10000)
        self.projection = Uniform("mat4", self.projection_mat)
        self.projection.find_variable(program_id, "projection_mat")
        self.screen_width = w
        self.screen_height = h
        self.program_id = program_id

    def get_position(self):
        """Extrae la posición de la cámara desde la matriz de transformación"""
        return pygame.Vector3(
            self.transformation[0, 3],
            self.transformation[1, 3], 
            self.transformation[2, 3]
        )

    def perspective_mat(self, angle_of_view, aspect_ratio, near_plane, far_plane):
        a = radians(angle_of_view)
        d = 1.0 / tan(a / 2.0)
        r = aspect_ratio
        b = (far_plane + near_plane) / ( near_plane - far_plane)
        c = far_plane * near_plane / ( near_plane - far_plane)
        return np.array([[d/r, 0,  0, 0],
                         [0  , d,  0, 0],
                         [0  , 0,  b, c],
                         [0  , 0, -1, 0]], np.float32)

    def rotate(self, yaw, pitch):
        forward = pygame.Vector3(self.transformation[0,2], self.transformation[1,2], self.transformation[2,2])
        up = pygame.Vector3(0.0, 1.0, 0.0)
        angle = forward.angle_to(up)

        self.transformation = rotate(self.transformation, yaw, "y", False)
        if angle < 170.0 and pitch > 0.0 or angle > 30.0 and pitch < 0.0:
            self.transformation = rotate(self.transformation, pitch, "x", True)

    def update(self):
        if pygame.mouse.get_visible():
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_change = self.last_mouse - pygame.math.Vector2(mouse_pos)
        pygame.mouse.set_pos(self.screen_width / 2, self.screen_height / 2)
        self.last_mouse = pygame.mouse.get_pos()
        self.rotate(mouse_change.x * self.mouse_sensitivityX, mouse_change.y * self.mouse_sensitivityY)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.transformation = translate(self.transformation, 0, 0, self.key_sensitivity)
        if keys[pygame.K_UP]:
            self.transformation = translate(self.transformation, 0, 0, -self.key_sensitivity)
        if keys[pygame.K_RIGHT]:
            self.transformation = translate(self.transformation, self.key_sensitivity, 0, 0)
        if keys[pygame.K_LEFT]:
            self.transformation = translate(self.transformation, -self.key_sensitivity, 0, 0)

        self.projection.load()
        lookat_mat = self.transformation
        lookat = Uniform("mat4", lookat_mat)
        lookat.find_variable(self.program_id, "view_mat")
        lookat.load()