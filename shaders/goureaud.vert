#version 330 core

struct Light {
    vec3 position; // world space
    vec3 color;
    float intensity;
};

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec2 uv;
layout(location = 3) in vec3 normal;

uniform mat4 projection, view, model;
uniform float iRotation; // rotation period, if 0 then no movement
uniform float iTime; // seconds
uniform vec3 view_pos; // camera position in world space

out vec3 frag_pos; // world space
out vec3 frag_color;
out vec2 frag_tex_coord;
out vec3 frag_normal; // world space

#define PI 3.14159265358979323846
#define MAX_LIGHTS 16

// texture
uniform sampler2D image;
uniform bool isTextured;

// lights
uniform Light lights[MAX_LIGHTS];
uniform int num_lights;

// material
uniform vec3 ambient_color; // e.g. vec3(0.1)
uniform float k_ambient; // e.g. 1.0
uniform float k_diffuse; // e.g. 1.0
uniform float k_specular; // e.g. 0.5
uniform float shininess; // e.g. 32.0

vec3 calcLight(vec3 vert_pos, vec3 surface_color, Light light, vec3 N, vec3 V) {
    vec3 L = normalize(light.position - vert_pos); // toward the light
    vec3 radiance = light.color * light.intensity;

    // diffuse
    float diff = max(dot(N, L), 0.0);

    // specular (Phong)
    float spec = 0.0;
    if (diff > 0.0) {
        vec3 R = reflect(-L, N);
        spec = pow(max(dot(R, V), 0.0), shininess);
    }

    // diffuse tinted by surface color, specular stays white
    return radiance * (k_diffuse * diff * surface_color + k_specular * spec);
}

void main() {
    // rotation about Z (GLSL is column-major: each group of 4 is a column)
    mat4 rot = mat4(1.0);
    if (iRotation > 1e-6) {
        float theta = 2.0 * PI * iTime / iRotation;
        float c = cos(theta), s = sin(theta);
        rot = mat4(
                c, s, 0., 0.,
                -s, c, 0., 0.,
                0., 0., 1., 0.,
                0., 0., 0., 1.
            );
    }

    // space transformations
    mat4 world = rot * model;
    vec4 world_pos = world * vec4(position, 1.0);
    vec4 view_space_pos = view * world_pos;

    frag_pos = world_pos.xyz;
    frag_tex_coord = uv;
    frag_normal = transpose(inverse(mat3(world))) * normal;

    // texture
    vec4 surface_color;
    if (isTextured) {
        surface_color = texture(image, frag_tex_coord);
    } else {
        surface_color = vec4(color, 1.0);
    }

    // Gouraud shading (lighting computed per vertex)
    vec3 N = normalize(frag_normal);
    vec3 V = normalize(view_pos - frag_pos);

    vec3 result = k_ambient * ambient_color * surface_color.xyz;
    for (int i = 0; i < num_lights; ++i) {
        result += calcLight(frag_pos, surface_color.xyz, lights[i], N, V);
    }

    frag_color = result;
    gl_Position = projection * view_space_pos;
}
