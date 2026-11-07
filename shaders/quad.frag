#version 330 core

in vec2 uv;

uniform sampler2D overlay;

out vec4 fragColor;

void main() {
    fragColor = texture(overlay, vec2(uv.x, 1.0 - uv.y)); // flip: array is top-down
}
