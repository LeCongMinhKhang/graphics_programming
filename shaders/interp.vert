#version 330 core

layout(location = 0) in vec3 position; // vertex position (object space)
layout(location = 1) in vec3 color; // vertex color (no lighting)

uniform mat4 projection, view, model; // space transformation matrices
uniform float iRotation; // rotation period, if 0 then no movement
uniform float iTime; // seconds

out vec3 fragment_color; // vertex color

#define PI 3.14159265358979323846

void main() {
    fragment_color = color;

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

    gl_Position = projection * view * rot * model * vec4(position, 1.0);
}
