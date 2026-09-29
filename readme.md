# Assignement 1: Computer Graphics

## Part I: Drawing basic shapes

### Default uniforms
Some uniforms are made available to shaders by default.
- `float iTime`: the time since the window opening, in seconds.
- `vec4 iMouse`: mouse info (xy: current if MLB down, zw: click).
- `vec2 iResolution`: the dimensions of the display window, in pixels.

### Data Structure 
The pipeline rendering needs to be supplied with:
- **vertices**: np.array((n, 3))
- **indices**(optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
- **colors**: np.array((n, 3)) each component must be in [0, 1]
- **normals**: np.array((n, 3))
- **mode**: GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)


## TODO
### Modules
#### Pipeline modules
- [] data provider (vertices, normals, uvs, ...)
  - [ ] obj parser
  - [ ] textures input
  - [ ] shaders input    
- [x] shader pipeline
- [x] camera
- [x] support flat shading
#### GUI modules
- [ ] toolbar
- [x] GL display (rendering loop, GL interface)
- [x] window 
- [x] mouse and time support
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

### Basic requirements:
- The application must include a graphical user interface (GUI) with menus or toolbars
that allow users to select which shape to draw or add.
- The application must support mouse and/or keyboard interaction to zoom, pan, and
rotate the objects in the scene.
- The application must provide multiple rendering modes for each object:
  - [x] Flat color (single uniform color for the entire object).
  - [ ] Vertex color interpolation using Gouraud shading.
  - [ ] Phong shading (with per-fragment lighting).
  - [ ] Texture mapping using external image files provided by the user.
  - [x] Wireframe mode for visualizing only the edges of the shape.

### Lighting
multiple lights supported
lights passed as uniforms, can be passed as static uniforms (via object declaration) 

## Questions:
should the wireframe be able to be activated for each separately?
-> ie one parameter to toggle it globally (default behaviour) and one parameter for each object specifically

Currently: model matrix is static.
Consider making a class allowing the objects to move within the scene by modifying the model matrix (then the `model` uniform should become dynamic, maybe handled by a class similarly to the camera).

Same discussion with lights

## TODO: 
Cache uniform locations. glGetUniformLocation with string formatting every frame is slow in Python. Build a dict of locations once after linking the program
