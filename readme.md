# Assignement 1: Computer Graphics

## Part I: Drawing basic shapes

### Default uniforms
Some uniforms are made available to shaders by default.
- `float iTime`: the time since the window opening, in seconds.
- `vec4 iMouse`: mouse info (xy: current if MLB down, zw: click).
- `vec2 iResolution`: the dimensions of the display window, in pixels.

- `mat4 model`: the model matrix to place an object in the world
- `mat4 view`: the tranform matrix from world to camera view
- `mat4 projection`: the transform matrix from camera view to screen
- `vec3 view_pos`: the world position of the camera

### Data Structure 
The pipeline rendering needs to be supplied with:
- **vertices**: np.array((n, 3))
- **indices**(optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
- **colors**: np.array((n, 3)) each component must be in [0, 1]
- **normals**: np.array((n, 3))
- **mode**: GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)

### Usage
```sh
python test/generators/generator.py --scene triangle 
python test/generators/generator.py --scene torus
python test/generators/generator.py --scene surface
python test/pipeline/lighting/sphere.py  # phong lighting
```

### Modules
#### Pipeline modules
- [x] different GL modes
- [ ] different GL primitives
  - [x] triangles
  - [ ] segments
  - [ ] points
- [ ] textures input
- [x] shaders files support
  - [x] uniforms
- [x] camera
- [x] Wireframe mode for visualizing only the edges of the shape.
- [ ] lighting 
  - [x] Flat color (single uniform color for the entire object).
  - [ ] Vertex color interpolation using Gouraud shading.
  - [x] Phong shading (with per-fragment lighting).
  - [ ] Texture mapping using external image files provided by the user.
  - [x] multiple lights
  - [ ] directional light
  - [x] puncual light
#### GUI modules
- [ ] toolbar/menus
- [x] GL display (rendering loop, GL interface)
- [x] window 
- [x] mouse and time support
- [ ] keyboard interaction
- [ ] fps

### 2D Shapes
- [x] triangle
- [x] rectangle
- [x] pentagon
- [x] regular hexagon
- [x] circle
- [x] ellipse
- [x] trapezoid
- [x] star
- [x] arrow

### 3D Shapes
- [x] basic solids
  - [x] cube
  - [x] sphere
  - [x] cylinder
  - [x] cone
  - [x] truncated cone
  - [x] tetrahedron
  - [x] torus
  - [x] prism.
- [x] Mathematical surface defined by a user-provided function z = f (x, y).
- [x] Imported 3D model from .obj or .ply file.


## Questions:
should the wireframe be able to be activated for each separately?
-> ie one parameter to toggle it globally (default behaviour) and one parameter for each object specifically

Currently: model matrix is static.
Consider making a class allowing the objects to move within the scene by modifying the model matrix (then the `model` uniform should become dynamic, maybe handled by a class similarly to the camera).

Same discussion with lights

## TODO: 
Cache uniform locations. glGetUniformLocation with string formatting every frame is slow in Python. Build a dict of locations once after linking the program
