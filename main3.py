from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Sphere import *
from glApp.MatteSphere import * 
import pygame

vertex_shader_matte = r'''
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vertex_normal;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

out vec3 frag_normal;
out vec3 frag_pos;

void main()
{
    gl_Position = projection_mat * view_mat * model_mat * vec4(position, 1.0);
    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
}
'''

fragment_shader_matte = r'''
#version 330 core
in vec3 frag_normal;
in vec3 frag_pos;

out vec4 final_color;

uniform vec3 view_pos;
uniform vec3 light_pos;
uniform vec3 matte_color;

void main()
{
    // 🎨 CONFIGURACIÓN MATERIAL MATE (SIN BRILLO)
    vec3 light_color = vec3(1.0, 1.0, 1.0);
    float ambient_strength = 0.4;  // Ambiente más alto para superficie mate
    
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);

    // 💡 COMPONENTE AMBIENTAL (alta para mate)
    vec3 ambient = ambient_strength * matte_color;

    // 💡 COMPONENTE DIFUSA (principal para mate)
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color * matte_color;

    // ❌ SIN COMPONENTE ESPECULAR (sin brillo)
    // vec3 specular = vec3(0.0);  // Cero brillo

    // 🎨 MEZCLA FINAL - SOLO AMBIENTE + DIFUSA
    vec3 result = ambient + diffuse;
    
    // 🔵 APLICAR COLOR MATE
    result = result * matte_color;
    
    final_color = vec4(result, 1.0);  // 💯 OPACO COMPLETO
}
'''

class MatteSphereApp(PyOGApp):
    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.matte_sphere = None

    def initialise(self):
        self.program_id = create_program(vertex_shader_matte, fragment_shader_matte)
        print(f"✅ Programa shader mate creado: {self.program_id}")
        
        # 🎨 CREAR ESFERA MATE
        self.matte_sphere = MatteSphere(self.program_id, 
                                      location=pygame.Vector3(0, 0, 0),
                                      move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
        
        print("✅ Esfera mate creada")
        
        # Configurar cámara
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        self.camera.transformation = translate(identity_matrix(), 0, 0, -5)
        
        # ⚙️ CONFIGURACIÓN OPENGL PARA MATERIAL MATE
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)  # 🔴 DESHABILITAR transparencia
        glEnable(GL_MULTISAMPLE)
        
        # 🎨 Fondo neutro para mejor visualización
        glClearColor(0.3, 0.3, 0.35, 1.0)  # Gris neutro

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        
        # Obtener posición de la cámara
        transformation = self.camera.transformation
        cam_pos = pygame.Vector3(transformation[0, 3], transformation[1, 3], transformation[2, 3])
        
        # Pasar uniformes al shader
        view_pos_loc = glGetUniformLocation(self.program_id, "view_pos")
        light_pos_loc = glGetUniformLocation(self.program_id, "light_pos")
        
        glUniform3f(view_pos_loc, cam_pos.x, cam_pos.y, cam_pos.z)
        glUniform3f(light_pos_loc, 3.0, 5.0, 3.0)  # Luz desde arriba
        
        # 🎨 Dibujar esfera mate
        self.matte_sphere.draw()

if __name__ == "__main__":
    MatteSphereApp().mainloop()