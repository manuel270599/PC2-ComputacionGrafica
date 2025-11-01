from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.WaterSphere import * 
import pygame

vertex_shader_water = r'''
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vertex_normal;
layout (location = 2) in vec2 texcoord;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

out vec3 frag_normal;
out vec3 frag_pos;
out vec3 view_dir;
out vec2 uv;

void main()
{
    gl_Position = projection_mat * view_mat * model_mat * vec4(position, 1.0);
    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    view_dir = normalize(-frag_pos);
    uv = texcoord;
}
'''

fragment_shader_water = r'''
#version 330 core

in vec3 frag_normal;
in vec3 frag_pos;
in vec3 view_dir;
in vec2 uv;

out vec4 final_color;

uniform vec3 view_pos;
uniform vec3 light_pos;
uniform float time;

void main()
{
    // 🎨 COLOR BASE DEL AGUA
    vec3 water_color = vec3(0.2, 0.4, 0.8);
    float transparency = 0.7;
    
    // 🔦 CONFIGURACIÓN DE LUZ
    vec3 light_color = vec3(1.0, 1.0, 1.0);
    float ambient_strength = 0.3;
    
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);

    // 🌊 EFECTO DE ONDAS CON UVs Y TIEMPO
    vec2 animated_uv = uv;
    animated_uv.x += sin(time * 2.0 + uv.y * 8.0) * 0.02;
    animated_uv.y += cos(time * 1.5 + uv.x * 6.0) * 0.02;
    
    // 🎭 PATRÓN DE ONDAS
    float wave_pattern = sin(animated_uv.x * 20.0 + time * 3.0) * 
                        cos(animated_uv.y * 15.0 + time * 2.0) * 0.1;
    
    // Aplicar patrón de ondas a la normal
    vec3 distorted_norm = normalize(norm + vec3(wave_pattern, 0.0, wave_pattern) * 0.3);

    // 💧 EFECTO FRESNEL
    float fresnel = pow(1.0 - max(dot(distorted_norm, view_dir), 0.0), 2.0);
    fresnel = mix(0.1, 0.6, fresnel);

    // 💡 COMPONENTES DE ILUMINACIÓN
    vec3 ambient = ambient_strength * water_color;
    
    float diff = max(dot(distorted_norm, light_dir), 0.0);
    vec3 diffuse = diff * water_color * 0.8;

    // ✨ REFLEJOS ESPECULARES
    vec3 reflect_dir = reflect(-light_dir, distorted_norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 64.0);
    vec3 specular = spec * light_color * 1.5;

    // 🌈 VARIACIÓN DE COLOR CON PROFUNDIDAD
    float depth_factor = (frag_pos.y + 1.0) / 2.0;
    vec3 depth_color = mix(water_color * 0.3, water_color, depth_factor);

    // 🎨 MEZCLA FINAL
    vec3 base_result = ambient + diffuse;
    vec3 reflective_result = mix(base_result, light_color, fresnel * 0.7);
    vec3 final_result = reflective_result + specular;
    
    // 🔵 APLICAR COLOR DE AGUA
    final_result = mix(final_result, water_color, 0.4);
    
    // 💎 TRANSPARENCIA CON VARIACIÓN
    float alpha = transparency + wave_pattern * 0.2;
    alpha = clamp(alpha, 0.5, 0.9);
    
    final_color = vec4(final_result, alpha);
}
'''

class WaterSphereApp(PyOGApp):
    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.water_sphere = None
        self.start_time = pygame.time.get_ticks()

    def initialise(self):
        self.program_id = create_program(vertex_shader_water, fragment_shader_water)
        print(f"✅ Programa shader de agua creado: {self.program_id}")
        
        # 🌊 CREAR ESFERA DE AGUA
        self.water_sphere = WaterSphere(self.program_id, 
                                      location=pygame.Vector3(0, 0, 0),
                                      move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
        
        print("✅ Esfera de agua creada")
        
        # Configurar cámara
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        self.camera.transformation = translate(identity_matrix(), 0, 0, -5)
        
        # ⚙️ CONFIGURACIÓN OPENGL PARA AGUA
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.1, 0.2, 0.3, 1.0)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        
        # 🕒 ACTUALIZAR TIEMPO PARA ANIMACIÓN
        current_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
        time_loc = glGetUniformLocation(self.program_id, "time")
        glUniform1f(time_loc, current_time)
        
        # Obtener posición de la cámara
        transformation = self.camera.transformation
        cam_pos = pygame.Vector3(transformation[0, 3], transformation[1, 3], transformation[2, 3])
        
        # Pasar uniformes al shader
        view_pos_loc = glGetUniformLocation(self.program_id, "view_pos")
        light_pos_loc = glGetUniformLocation(self.program_id, "light_pos")
        
        glUniform3f(view_pos_loc, cam_pos.x, cam_pos.y, cam_pos.z)
        glUniform3f(light_pos_loc, 2.0, 5.0, 3.0)
        
        # 🌊 Dibujar esfera de agua
        self.water_sphere.draw()

if __name__ == "__main__":
    WaterSphereApp().mainloop()