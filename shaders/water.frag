#version 330 core

#define MAX_LIGHTS 16
#define PI 3.14159265359
#define BLUE vec3(0, 0, 1)

struct Light {
    vec3 position; // world space
    vec3 color;
    float intensity;
};

in vec3 frag_pos; // world space
in vec3 frag_color;
in vec2 frag_tex_coord;
in vec3 frag_normal; // world space

out vec4 out_color;

uniform vec3 view_pos; // camera position in world space
uniform float iTime;

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

vec3 calcLight(vec3 pos, vec3 color, Light light, vec3 N, vec3 V) {
    vec3 L = normalize(light.position - pos); // toward the light
    vec3 radiance = light.color * light.intensity;

    // diffuse
    float diff = max(dot(N, L), 0.0);

    // specular (Phong: reflect the incoming light direction about N)
    float spec = 0.0;
    if (diff > 0.0) { // only if the face sees the light
        vec3 R = reflect(-L, N);
        spec = pow(max(dot(R, V), 0.0), shininess);
    }

    // diffuse is tinted by the surface color (done in main),
    // specular is left white so highlights take the light's color
    return radiance * (k_diffuse * diff * color
            + k_specular * spec);
}

void main() {

    // texture
    vec4 surface_color = vec4(0., 0., 0., 1.);
    if (isTextured) {
        surface_color = texture(image, frag_tex_coord);
    } else {
        surface_color = vec4(frag_color, 1.0);
    }

    // waves
    float amplitude = .1;
    float x_period = 1.;
    float x_wave_number = 4.;
    float y_period = .7;
    float y_wave_number = 6.;

    float ax = iTime * 2. * PI / x_period + frag_tex_coord.x * (x_wave_number * 4.);
    // float ay = iTime * 2. * PI / y_period + frag_tex_coord.y * (y_wave_number * 4.);
    float ay = 0.;

    float dhdx = -sin(ax) * (x_wave_number * 4.) * amplitude;
    float dhdy = -sin(ay) * (y_wave_number * 4.) * amplitude;

    vec3 offset_pos = vec3(frag_pos.xy, frag_pos.z + amplitude * cos(ax) + amplitude * cos(ay));
    vec3 offset_normal = normalize(vec3(-dhdx, -dhdy, 1.));

    // vec3 offset_pos = frag_pos;
    // vec3 offset_normal = frag_normal;

    // vec3 offset = vec3(
    //     	cos(iTime * 2. * PI / x_period + frag_tex_coord.x * (x_wave_number * 4.)),
    //     	cos(iTime * 2. * PI / y_period + frag_tex_coord.y * (y_wave_number * 4.)),
    //     	0.
    //     		);
    // vec3 offset_pos = vec3(frag_pos.xy, frag_pos.z + offset.x + offset.y);
    // vec3 offset_normal = frag_normal + offset;

    // phong calculation
    vec4 result = vec4(1.);
    vec3 N = normalize(offset_normal);
    vec3 V = normalize(view_pos - offset_pos);
    vec3 Vdebug = normalize(view_pos - frag_pos);

    result.xyz *= k_ambient * ambient_color;
    for (int i = 0; i < num_lights; ++i) {
        result.xyz += calcLight(offset_pos, BLUE, lights[i], N, V);
    }

    out_color = result;
    // no lights uniforms
    // out_color = vec4(mix(BLUE, vec3(0, 1, 0), (cos(ax) + 1) / 2), 1.);
    // out_color = vec4(N, 1.);
}
