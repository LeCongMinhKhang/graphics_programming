#version 330 core

in vec3 fragment_color;
out vec4 out_color;

uniform ivec2 iResolution;
uniform float testUniform;

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy; // normalized pixel coordinates (from 0 to 1)
    uv -= 0.5; // centers uv

    out_color = vec4(fragment_color * (sqrt(1) - length(uv)) + vec3(0., 0., testUniform), 1.0);
}
