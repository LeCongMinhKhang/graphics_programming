#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal;

uniform mat4 projection, view, model;

out vec3 frag_pos; // world space
out vec3 frag_color;
out vec3 frag_normal; // world space

void main() {
    vec4 world_pos = model * vec4(position, 1.0);

    // interpolated
    frag_pos = world_pos.xyz;
    frag_color = color;
    frag_normal = mat3(transpose(inverse(model))) * normal;

    gl_Position = projection * view * world_pos;
}
