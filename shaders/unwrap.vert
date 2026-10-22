#version 330 core

layout(location = 0) in vec3 position; // vertex position (object space)
layout(location = 1) in vec3 color; // vertex color (no lighting)
layout(location = 2) in vec2 uv; // uv coordinates

uniform mat4 projection, view, model; // space transformation matrices
uniform float iRotation; // rotation period, if 0 then no movement
uniform float iTime; // seconds

out vec3 frag_color; // vertex color
out vec2 frag_tex_coord; // texture coordinates

#define PI 3.14159265358979323846

void main() {
    frag_color = color;
    frag_tex_coord = uv;

    // rotation
    mat4 rot;
    rot = mat4(1.);
    vec3 pos;
    if (iRotation == 0) {
        pos = position;
    } else {
        pos = position * ((iRotation - 0.5) / 9.5) + 2 * (vec3(uv, 0.0) + vec3(-0.5, -0.5, 0.0)) * ((10 - iRotation) / 9.5);
    }
    gl_Position = projection * view * model * vec4(pos, 1.0);
}
