#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal;

uniform mat4 projection, view, model; // space transformation matrices
uniform float iRotation; // rotation period, if 0 then no movement
uniform float iTime; // seconds

out vec3 frag_pos; // world space
out vec3 frag_color;
out vec3 frag_normal; // world space

#define PI 3.14159265358979323846

void main() {
    // rotation
    mat4 rot;
    if (iRotation > 1e-6) {
        float theta = 2. * PI * iTime / iRotation;
        rot = mat4(
                cos(theta), 0., -sin(theta), 0.,
                0., 1., 0., 0.,
                sin(theta), 0., cos(theta), 0.,
                0., 0., 0., 1.
            );
    } else {
        rot = mat4(1.);
    }

    vec4 world_pos = rot * model * vec4(position, 1.0);

    // interpolated
    frag_pos = world_pos.xyz;
    frag_color = color;
    frag_normal = mat3(transpose(inverse(rot * model))) * normal;

    gl_Position = projection * view * world_pos;
}
