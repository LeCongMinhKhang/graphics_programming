#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
// layout(location = 2) in vec3 normal;

out vec3 fragment_color; // vertex color → interpolated to the fragment
// out vec3 vWorldPos;
// out vec3 vNormal;

uniform mat4 uModel;

uniform vec4 uRotation; // trackball rotation as unit quaternion
uniform vec2 uPan; // trackball 2d pos
uniform float uDistance; // trackball distance

uniform float uFovyDegrees; // e.g. 35.0
uniform float uAspect; // winsize[0] / winsize[1]
uniform float uNear; // 0.1 * distance
uniform float uFar; // 100.0 * distance

mat4 quatToMat4(vec4 q) {
    float x = q.x, y = q.y, z = q.z, w = q.w;
    float nxx = -x * x, nyy = -y * y, nzz = -z * z;
    float qwx = w * x, qwy = w * y, qwz = w * z;
    float qxy = x * y, qxz = x * z, qyz = y * z;

    // column-major, matches transform.quaternion_matrix row-by-row
    return mat4(
        2.0 * (nyy + nzz) + 1.0, 2.0 * (qxy + qwz), 2.0 * (qxz - qwy), 0.0,
        2.0 * (qxy - qwz), 2.0 * (nxx + nzz) + 1.0, 2.0 * (qyz + qwx), 0.0,
        2.0 * (qxz + qwy), 2.0 * (qyz - qwx), 2.0 * (nxx + nyy) + 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
}

mat4 translateMat(vec3 t) {
    return mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        t.x, t.y, t.z, 1.0
    );
}

mat4 perspectiveMat(float fovyDegrees, float aspect, float near, float far) {
    float scale = 1.0 / tan(radians(fovyDegrees) * 0.5);
    float sx = scale / aspect;
    float sy = scale;
    float zz = (far + near) / (near - far);
    float zw = 2.0 * far * near / (near - far);

    return mat4(
        sx, 0.0, 0.0, 0.0,
        0.0, sy, 0.0, 0.0,
        0.0, 0.0, zz, -1.0,
        0.0, 0.0, zw, 0.0
    );
}

void main() {
    fragment_color = color;

    mat4 view = translateMat(vec3(uPan, -uDistance)) * quatToMat4(uRotation);

    mat4 proj = perspectiveMat(uFovyDegrees, uAspect, uNear, uFar);

    vec4 worldPos = uModel * vec4(position, 1.0);
    // vWorldPos = worldPos.xyz;
    // vNormal = mat3(uModel) * normal;

    gl_Position = proj * view * worldPos;
}
