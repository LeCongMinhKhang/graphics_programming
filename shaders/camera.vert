#version 330 core

layout(location = 0) in vec3 position; // vertex position (object space)
layout(location = 1) in vec3 color; // vertex color (no lighting)

uniform mat4 projection, view;

out vec3 fragment_color; // vertex color → interpolated to the fragment

void main() {
    fragment_color = color;
    gl_Position = projection * view * vec4(position, 1.0);
}
