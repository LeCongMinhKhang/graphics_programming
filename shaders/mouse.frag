#version 330 core

in vec3 fragment_color;
out vec4 out_color;

uniform vec2 iResolution;
uniform vec4 iMouse;

void main() {
    vec2 mouse = iMouse.xy / iResolution.xy - 0.5;
    out_color = (1 - length(mouse)) * vec4(fragment_color, 1.0);
}
