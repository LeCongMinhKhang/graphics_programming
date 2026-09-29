#version 330 core

layout(location = 0) in vec3 position; // vertex position (object space)
layout(location = 1) in vec3 color; // vertex color (no lighting)

uniform mat4 projection, view;
uniform float iTime;

out vec3 fragment_color; // vertex color → interpolated to the fragment

#define PI 3.14159265358979323846
void main() {
    fragment_color = color;
    float theta = 1 * iTime;
    mat4 rotation = mat4(cos(theta), - sin(theta), 0, 0,
                         sin(theta),   cos(theta), 0, 0,
                                  0,            0, 1, 0,
                                  0,            0, 0, 1);
    gl_Position = projection * view * rotation * vec4(position, 1.0);
}
