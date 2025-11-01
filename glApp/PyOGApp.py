import pygame
from pygame.locals import *
from .Camera import *
import os
from OpenGL.GL import *
from OpenGL.GLU import *

class PyOGApp():
    def __init__(self, screen_posX, screen_posY, screen_width, screen_height):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (screen_posX, screen_posY)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        pygame.init()
        
        # Configuración OpenGL moderna
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('Esfera Metálica - Blinn-Phong')
        
        self.camera = None
        self.program_id = None
        self.clock = pygame.time.Clock()
        
        # Información del sistema
        print("=" * 50)
        print("✅ OpenGL version:", glGetString(GL_VERSION).decode())
        print("🧭 Renderer:", glGetString(GL_RENDERER).decode())
        print("🔧 GLSL version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("=" * 50)

    def initialise(self):
        pass

    def display(self):
        pass

    def camera_init(self):
        pass

    def mainloop(self):
        done = False
        self.initialise()
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                    if event.key == K_SPACE:
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
            self.camera_init()
            self.display()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()