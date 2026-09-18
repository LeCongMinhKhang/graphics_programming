#version 330 core

layout(location = 0) in vec3 position;  // vertex position (object space)
layout(location = 1) in vec3 color;     // vertex color (used as albedo)
layout(location = 2) in vec3 normal;    // vertex normal (object space)

flat out vec3 fragment_color;   // `flat`: no interpolation between vertices

void main() {
    fragment_color = color;
    gl_Position = vec4(position, 1.);
}
