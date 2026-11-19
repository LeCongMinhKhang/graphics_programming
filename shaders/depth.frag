#version 330 core

out vec4 out_color;

uniform mat4 projection;

void main() {
    float near = projection[3][2] / (projection[2][2] - 1.0);
    float far = projection[3][2] / (projection[2][2] + 1.0);

    float z_ndc = gl_FragCoord.z * 2.0 - 1.0; // normalized device coordinates

    // formula deduced from https://en.wikipedia.org/wiki/Z-buffering
    float dist = -2. * far * near / (z_ndc * (far - near) - (far + near));

    // we normalize the distance between 0 (camera) and 1 (far plane)
    float v = clamp(dist / far, 0., 1.);
    out_color = vec4(vec3(v), 1.0);
}
