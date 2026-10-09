#version 330 core

in vec3 fragment_color;
in vec2 fragment_tex_coord;
out vec4 out_color;

uniform sampler2D image;
uniform bool isTextured;

void main() {
    if (isTextured) {
        out_color = texture(image, fragment_tex_coord);
    } else {
        out_color = vec4(fragment_color, 1.0);
    }
}
