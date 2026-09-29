#version 330 core

flat in vec3 fragment_color; // constant over the face, not interpolated
out vec4 out_color;

void main() {
    out_color = vec4(fragment_color, 1.0);
}
