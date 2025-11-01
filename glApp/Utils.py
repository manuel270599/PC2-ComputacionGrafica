from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

def compile_shader(shader_type, source):
    shader_id = glCreateShader(shader_type)
    glShaderSource(shader_id, source)
    glCompileShader(shader_id)
    
    # Verificar errores
    if not glGetShaderiv(shader_id, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader_id).decode()
        print(f"Error compilando shader: {error}")
        raise RuntimeError("Shader compilation failed")
    
    return shader_id

def create_program(vertex_shader_code, fragment_shader_code):
    vertex_shader_id = compile_shader(GL_VERTEX_SHADER, vertex_shader_code)
    fragment_shader_id = compile_shader(GL_FRAGMENT_SHADER, fragment_shader_code)
    
    program_id = glCreateProgram()
    glAttachShader(program_id, vertex_shader_id)
    glAttachShader(program_id, fragment_shader_id)
    glLinkProgram(program_id)
    
    # Verificar enlace
    if not glGetProgramiv(program_id, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program_id).decode()
        print(f"Error enlazando programa: {error}")
        raise RuntimeError("Program linking failed")
    
    glDeleteShader(vertex_shader_id)
    glDeleteShader(fragment_shader_id)
    
    return program_id