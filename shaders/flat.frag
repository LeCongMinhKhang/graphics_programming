#version 330 core

flat in vec3 frag_color; // constant over the face, not interpolated
flat in vec2 frag_tex_coord;
out vec4 out_color;

uniform sampler2D image;
uniform bool isTextured;

void main() {
    if (isTextured) {
        out_color = texture(image, frag_tex_coord);
    } else {
        out_color = vec4(frag_color, 1.0);
    }
}
