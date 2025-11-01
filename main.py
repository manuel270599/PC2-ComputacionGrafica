from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Sphere import *
import pygame

vertex_shader = r'''
#version 330 core
in vec3 position;
in vec3 vertex_normal;  // 🎯 Cambiado de vertex_normal

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

fragment_shader = r'''
#version 330 core
in vec3 frag_normal;
in vec3 frag_pos;

out vec4 final_color;

uniform vec3 view_pos;
uniform vec3 light_pos;
uniform float material_shininess;
uniform float material_specular_strength;
uniform vec3 metal_color;  // 🎯 COLOR UNIFORME

void main()
{
    // Configuración de luz
    vec3 light_color = vec3(1.0, 1.0, 1.0);
    float ambient_strength = 0.08;
    
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);
    vec3 view_dir = normalize(view_pos - frag_pos);

    // Componentes de iluminación
    vec3 ambient = ambient_strength * metal_color;
    
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * metal_color * 0.15;

    // Especular
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), material_shininess);
    vec3 specular = material_specular_strength * spec * light_color;

    // Color final
    vec3 result = ambient + diffuse + specular;
    final_color = vec4(result, 1.0);
}
'''

class ShaderObjects(PyOGApp):
    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.metal_sphere = None

    def initialise(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        print(f"✅ Programa shader creado: {self.program_id}")
        
        # 🎯 CREAR ESFERA METÁLICA DE ALTA CALIDAD
        self.metal_sphere = Sphere(self.program_id, 
                                 location=pygame.Vector3(0, 0, 0),
                                 slices=128,      # 🎯 ALTA RESOLUCIÓN
                                 stacks=64,       # 🎯 ALTA RESOLUCIÓN
                                 move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
        
        print("✅ Esfera metálica creada")
        
        # Configurar cámara
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        self.camera.transformation = translate(identity_matrix(), 0, 0, -5)
        
        # Configurar OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.05, 0.05, 0.1, 1.0)  # Fondo azul oscuro

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
        glUniform3f(light_pos_loc, 3.0, 5.0, 3.0)  # Luz arriba y al frente
        
        # Dibujar esfera metálica
        self.metal_sphere.draw()

if __name__ == "__main__":
    ShaderObjects().mainloop()