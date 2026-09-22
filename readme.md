# Assignement 1: Computer Graphics

## Part I: Drawing basic shapes

## TODO
### Modules
#### Pipeline modules
- [] data provider (vertices, normals, uvs, ...)
  - [ ] obj parser
  - [ ] textures input
  - [ ] shaders input    
- [ ] shader pipeline
#### GUI modules
- [ ] toolbar
- [ ] GL display (rendering loop, GL interface)
- [ ] window 

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
  - [ ] Flat color (single uniform color for the entire object).
  - [ ] Vertex color interpolation using Gouraud shading.
  - [ ] Phong shading (with per-fragment lighting).
  - [ ] Texture mapping using external image files provided by the user.
  - [ ] Wireframe mode for visualizing only the edges of the shape.
