#version 330 core

in vec3 fragment_color;
out vec4 out_color;

uniform vec2 iResolution;
uniform float iTime;

#define PI 3.14159265358979323846

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy; // normalized pixel coordinates (from 0 to 1)
    uv -= 0.5; // centers uv

    vec3 col = vec3(
            cos(iTime * (2. * PI / 12.) + uv.x),
            cos(iTime * (2. * PI / 7.) + uv.y),
            cos(iTime * (2. * PI / 20.) + length(uv))
        );
    out_color = vec4(col, 1.0);
}
