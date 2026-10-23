#version 330 core

uniform vec2 iResolution;
uniform float iTime; // in seconds
uniform vec2 iMouse;

#define PI 3.1415926538

const vec3 BLACK = vec3(0., 0., 0.);
const vec3 WHITE = vec3(1., 1., 1.);
const vec3 RED = vec3(1., 0., 0.);
const vec3 GREEN = vec3(0., 1., 0.);
const vec3 BLUE = vec3(0., 0., 1.);
const vec3 YELLOW = vec3(1., 1., 0.);

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

float rand(float seed) {
    return fract(sin(dot(vec2(seed), vec2(12.9898, 78.233))) * 43758.5453);
}

int fact(int n) {
    int res = 1;
    while (n > 0) {
        res *= n;
        n--;
    }
    return res;
}

int binom(int n, int k) {
    return fact(n) / (fact(k) * fact(n - k));
}

float remap(float a, float b, float c, float d, float x) {
    // remap x from [a,b] on [c,d], linear
    return c + (x - a) / (b - a) * (d - c);
}

float my_smoothstep1(float edge0, float edge1, float x) {
    // Scale, and clamp x to 0..1 range
    x = clamp((x - edge0) / (edge1 - edge0), 0., 1.);

    return x * x * (3.0f - 2.0f * x);
}

float my_smoothstep2(float edge0, float edge1, float x) {
    // Scale, and clamp x to 0..1 range
    x = clamp((x - edge0) / (edge1 - edge0), 0., 1.);

    return 6. * pow(x, 5.) - 15. * pow(x, 4.) + 10. * pow(x, 3.);
}

float my_smoothstep(float edge0, float edge1, float x, int n) {
    // computes the sigmoid of rank n (S_n(x))
    x = clamp((x - edge0) / (edge1 - edge0), 0., 1.);

    float res = 0.;
    for (int k = 0; k <= n; k++) {
        res += float(binom(n + k, k) * binom(2 * n + 1, n - k)) * pow(-x, float(k));
    }
    return res * pow(x, float(n + 1));
}

float my_smoothstep_linear(float edge0, float edge1, float x)
{
    return (x - edge0) / (edge1 - edge0);
}

vec3 my_mix1(vec3 col0, vec3 col1, float ratio) {
    vec3 col;
    for (int i = 0; i < 3; i++) {
        col[i] = remap(0., 1., col0[i], col1[i], my_smoothstep2(0., 1., ratio));
    }
    return col;
}

float two_seg_func(float edge0, float edge1, vec2 p, float x) {
    // two linear functions sticked to each other joining in point p (relatively in 0..1)
    x = clamp((x - edge0) / (edge1 - edge0), 0., 1.);
    if (x < p.x)
        return p.y * x;
    else
        return p.x * (x - p.x) + p.y;
}

vec3 my_mix2(vec3 col0, vec3 col1, float ratio) {
    vec3 col;
    for (int i = 0; i < 3; i++) {
        col[i] = remap(0., 1., col0[i], col1[i], two_seg_func(0., 1., vec2(1. / 4., .8), ratio));
    }
    return col;
}

vec3 Circle(vec2 uv, vec3 color, vec2 center, float radius, float blur) {
    return color * my_smoothstep1(radius, radius - blur, length(uv - center));
}

vec3 Particle(vec2 uv, vec3 color, vec2 origin, float orientation, float v0) {
    float tau = 1.;
    float radius = 0.05;
    vec2 direction = vec2(cos(orientation), sin(orientation));
    return Circle(uv, color, origin + v0 * tau * (1. - exp(-iTime / tau)) * direction, radius, 0.1 * radius);
}

vec3 Flame(vec2 uv, int n, vec3 startColor, vec3 endColor, vec2 origin, float orientation, float height, float angular_op) {
    float radius = 0.07;
    float startTime;
    float d = 2.; // duration of a cycle
    float d_orientation;
    float pTime = 0.;
    float pHeight = height;

    vec3 col = vec3(0);
    for (int i = 0; i < n; i++) {
        startTime = float(i) * d / float(n);

        pTime = mod(iTime - startTime, d);
        float tau = d / 3.;
        //vec3 color = mix(startColor, endColor, pTime/d);
        vec3 color = my_mix2(startColor, endColor, pTime / d);
        d_orientation = rand(vec2(i, int((iTime - startTime) / d)));
        float angle = PI / 180. * (orientation + remap(0., 1., -angular_op / 2., angular_op / 2., d_orientation));
        vec2 direction = vec2(cos(angle), sin(angle));

        pHeight = height / 2. + remap(0., 0.5, height / 2., 0., abs(d_orientation - 0.5)); // shape of the flame
        col += Circle(uv, color, origin + pHeight * (1. - exp(-pTime / tau)) * direction, radius, 0.5 * radius);
        //col = max(col, Circle(uv, color, origin + pHeight*(1. - exp(-pTime/tau)) * direction, radius, 0.5*radius));
    }
    return col;
}

void main(void)
{
    // Defining and scaling uv
    vec2 uv = gl_FragCoord.xy.xy / iResolution.xy; // in [0;1]
    uv -= 0.5; // centers uv
    uv.x *= iResolution.x / iResolution.y; // scales uv to get correctly scaled axes

    vec3 col;

    //col = Circle(uv, YELLOW, vec2(0.2), 0.3, 0.02);
    //col += Circle(uv, BLUE, vec2(0.1), 0.3, 0.02);

    // col = Rectangle(uv, GREEN, vec2(0.3, 0), 0.5, 0.3, 10., 0.01);

    // flame
    vec3 startColor = YELLOW * .3;
    vec3 endColor = RED * .3;

    int n = 150;
    col = Flame(uv, n, startColor, endColor, vec2(0., -0.5), 90., .6, 40.);
    if (distance(col, vec3(0.)) < 1e-3) {
        col = vec3(.2);
    }

    gl_FragColor.rgb = col;
}
