#version 330 core

in vec3 fragment_color;
out vec4 out_color;

uniform vec2 iResolution;

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy; // normalized pixel coordinates (from 0 to 1)
    uv = 2. * uv - 1.; // uv in [-1, 1]²

    out_color = 1. / sqrt(2) * vec4(length(uv) * fragment_color, 1.0);
}
