#version 330 core

layout(location = 0) in vec3 position; // vertex position (object space)
layout(location = 1) in vec3 color; // vertex color (no lighting)

uniform mat4 projection, view, model;
uniform bool iRotation;
uniform float iTime;

#define PI 3.14159265358979323846

out vec3 fragment_color; // vertex color → interpolated to the fragment

void main() {
    fragment_color = color;
    float theta = 2. * PI * iTime / 3.;
    mat4 rot = iRotation ? mat4(
            cos(theta), 0., -sin(theta), 0.,
            0., 1., 0., 0.,
            sin(theta), 0., cos(theta), 0.,
            0., 0., 0., 1.
        ) : mat4(1.);
    gl_Position = projection * view * model * rot * vec4(position, 1.0);
}
