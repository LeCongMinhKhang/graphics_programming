#version 330 core

out vec4 out_color;

uniform mat4 projection;
uniform vec3 iColor;

void main() {
    out_color = vec4(iColor, 1.);
}
