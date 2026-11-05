#version 330 core

out vec4 out_color;

uniform mat4 projection;

// void main() {
//     float zNdc = gl_FragCoord.z * 2.0 - 1.0;
//     float dist = projection[3][2] / (zNdc + projection[2][2]);
//     out_color = vec4(vec3(dist / 20.0), 1.0); // try 5, 20, 50
// }
void main() {
    float zNdc = gl_FragCoord.z * 2.0 - 1.0;

    float dist = projection[3][2] / (zNdc + projection[2][2]);
    float far = projection[3][2] / (projection[2][2] + 1.0);

    float v = clamp(dist / far, 0.0, 1.0);
    out_color = vec4(vec3(v), 1.0);
}
