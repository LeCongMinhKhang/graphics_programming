
#import "@preview/tablex:0.0.9": hlinex, tablex, vlinex // optional, for fancier tables
#import "@preview/datify:1.0.1": custom-date-format

#let coursename = "Computer Graphics"
#let reporttype = "Progress Report"
#let report-title = "Assignement 1"
#let advisor = "Trần Thị Ngọc Trâm"
#let students = (
  ("Lê Công Minh Khang", "2252295"),
  ("Philippe Belda", "2660010"),
)

// Cover page
#let cover-page() = {
  set page(numbering: none)
  set align(center)

  text(size: 1em)[
    #upper[VIETNAM NATIONAL UNIVERSITY HO CHI MINH CITY] \
    #upper[HO CHI MINH CITY UNIVERSITY OF TECHNOLOGY ] \
    #upper[Faculty of Computer Science and Engineering] \
  ]

  v(2em)
  image("images/hcmut-logo.webp", width: 5cm)

  v(2em)
  text(size: 1.3em, weight: "bold")[#coursename]

  v(0.5em)
  line(length: 80%)
  v(2em)

  text(size: 1.3em, weight: "bold")[#reporttype]
  v(1em)
  text(size: 2em, weight: "bold")[#report-title]

  line(length: 80%, stroke: .12em)
  v(2em)

  align(left)[
    #set align(center)
    #table(
      columns: 3,
      stroke: none,
      column-gutter: 1em,
      align: left,
      [Advisor(s):], [#advisor], [],
      ..students
        .enumerate()
        .map(((i, s)) => (
          if i == 0 [Student(s)] else [],
          s.at(0),
          s.at(1),
        ))
        .flatten(),
    )
  ]

  v(1fr)
  upper[Ho Chi Minh City,
    #custom-date-format(
      datetime.today(),
      pattern: "dd MMMM yyyy",
      lang: "en",
    )]
  v(1fr)
  pagebreak()
}

// General page / text setup
#let conf(doc) = {
  set document(title: report-title)
  set page(
    paper: "a4",
    margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 2cm),
    numbering: "1",
    footer: context {
      set align(center)
      set text(size: .9em)
      [
        #counter(page).get().first() / #counter(page).final().first()
      ]
    },
  )
  set text(font: "New Computer Modern", size: 12pt, lang: "en")
  set heading(numbering: "I.1.")
  set par(justify: true)

  set figure(numbering: "1a")

  doc
}

#show: conf

#cover-page()
#outline(title: "Table of Contents", indent: auto)
#pagebreak()

= Introduction
// presentation of the project

= Software structure
#figure(
  image("images/software_structure.drawio.png", width: 100%),
  caption: [Diagram of the software structure],
)

= Shape Generators
== Data format
We choose to have object data bundled for rendering in the form:
```
data = {
  "vertices": np.array((n, 3))
  "indices"(optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
  "colors": np.array((n, 3)) each component must be in [0, 1]
  "normals": np.array((n, 3))
  "mode": GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
}
```
All shape generators and .obj files when read is converted to this format.
For the sake of simplicity at the moment, the rendering mode is always be GL_TRIANGLES, and colors and normals be automatically populated.
== Obj files
From the wiki, we can glance that obj files are text files with the syntax:
```
<fieldtype> <field1> <field2> <etc..>
v 0.123 0.234 0.345 1.0
...
vt 0.500 1 [0]
...
vn 0.707 0.000 0.707
...
vp 0.310000 3.210000 2.100000
...
f 1 2 3
f 3/1 4/2 5/3
f 6/4/1 3/5/3 7/6/5
f 7//1 8//2 9//3
f ...
```
At the moment we shall only focus on the 2 fields v (Vertex) and f (Triangle):

- For `data["vertices"]`, we parse the "v" fields as is

- For `data["indices"]`, .obj files has the "f" fields be 1-indexed when referencing which vertex is part of a triangle, as such, converting "f" fields to "indices" will need to decrement all referenced indices by 1.
== 2D shapes
=== `__circularish` helper function
Generating circles comes up a few times in some of the 2D and 3D shapes generation methods, thus a helper function like `__circularish` comes in very handy.

The exact functionality and implementation varies depending on use cases, which is why the function is copied accross files instead of declared and imported. In general, it takes in:
- n: a number of vertices it will generate
- size: distance from (0,0,z) it vertices will be
- z: the z coordinate of vertices

It follows:

Given step size in angle:

#align(center)[$theta = frac(2 pi, n)$]

for i in range(n) we create a new vertex at coordinate:

#align(center)[$(cos (i theta) times "size",sin (i theta) times "size", z)$]

=== Simple 2D shapes (triangle, rectangle, trapezoid, arrow)
These shapes are relatively simple, so each generators mostly only takes in a few basic arguments to scale them in different aspects. The vertices then gets their coordinate multiplied accordingly and populating `data["indices"]` is hardcoded

=== n-gon shapes (pentagon, hexagon, circle, ellipse)
All of these shapes can be generated with some variation of the `__circularish` function. Notably:
- Pentagon: n = 5
- Hexagon: n = 6
- Circle: n = 60
- Ellipse: n = 60, with a multiplier to the width of the n-gon in one of the axis

These rings of vertices are triangulated to all have 1 common vertex, and then iterate around the n-gon for the other 2 vertices. This method is simple and ensures the correct ordering of the indices but can leads to rendering artifacts (pinching) around the common vertex. A better way would be to do it in zigzag strips, or manually implementing the GL_TRIANGLE_FAN mode (recall that we assume that all shapes will always render in GL_TRIANGLES mode).

== 3D shapes
=== `triangulationNation` helper function
A lot of 3d shapes are more conveniently generated as quads (4 sided polygon). However, to beable to render in mode GL_TRIANGLES, we need to convert these lists of quads into a list of triangles.

It follows:
#align(center)[```python
  #      0.----.3
  #       |\   |
  #       | \  |
  #       |  \ |
  #       |   \|
  #      1'----'2
  # inputQuad = [0,1,2,3]
  res = []
  for quad in listOfQuads:
    res.append([[quad[0],quad[1],quad[2]]])
    res.append([[quad[0],quad[2],quad[3]]])
  return res
```]
Note that the method requires that quads part of the input list needs to have vertices indexed in a counter clockwise direction. Usage of this method would need some consideration in how the listOfQuads are generated.

=== Cube
The simplest 3d shape, establises the generation pattern that is used futher down the line.
#align(center)[```python
  p = size/2
  obj["v"].append([ -p ,  p ,  p])
  obj["v"].append([ -p ,  p , -p])
  obj["v"].append([ -p , -p ,  p])
  obj["v"].append([ -p , -p , -p])
  obj["v"].append([  p , -p ,  p])
  obj["v"].append([  p , -p , -p])
  obj["v"].append([  p ,  p ,  p])
  obj["v"].append([  p ,  p , -p])

  listOfQuads = []
  # top
  listOfQuads.append([0,2,4,6])
  # bottom
  listOfQuads.append([7,5,3,1])

  for i in range(0,8,2):
    listOfQuads.append([(i+0)%8,(i+1)%8,(i+3)%8,(i+2)%8])
```]

We initialize vertices in pairs that makes up 4 parallel edges of the cube going counter clockwise (in the code shown it is parallel to the z axis).

Then quads of the top and bottom faces of the cube is hard coded, putting in care to "reverse" the order for the bottom face to ensure that it faces the correct way.

Finally, thanks to the prepaired order that the vertices are declared, we can use a loop to iterate over the 4 side faces of the cube, with modulo operation `%` to beable to connect the last vertex pair to the first  

=== Simple `__circularish` and `triangulationNation` shapes (cylinder, cone, truncated cone, tetrahedron, prism)
All of these shapes is generated an a process similarly to the Cube, as some combination of `__circularish` for the top/bottom faces and a loop to generate quads as side walls:
- Cylinder: 2 n-gon top/bottom faces with a list of quads connecting the two
- Prism: 2 triangle top/bottom faces with a list of quads connecting the two
- Truncated cone: a Cylinder with 1 of the circles scaled down
- Cone: an n-gon pyramid, with an n-gon bottom face and a triangle fan as the side connecting to a vertex at the top
- tetrahedron: a specifically scaled cone with a triangle as a base

=== Sphere
There are multiple ways to create a sphere, we chose uv sphere due to similarity in construction with the earlier shapes.

In which, a sphere contains multiple `__circularish` n-gons of various sizes and z offsets, akin to the latitudes of a globe. These rings are connected to adjacent loops akin to how the sides of a cylinder was generated, only for multiple levels.
At the pole, the nearest n-gon to the pole vertex is connected similar to how the cone was generated.

=== Torus
Generating torus could make it by creating an n-gon in the xz plane, offset from the origin, and then apply some matrix transformation to rotate it around the z axis, but we did it by treating it like a cylinder that connects the top and bottom faces.

In particular, we first generate an n-gon using `__circularish`, then use the coordinates of these vertices to inform the offset from the z axis and z placements for generating the "verticle lines" of our "cylinder", which are made using `__circularish` and connected to eachother like the other shapes.

=== Surface
Surface rendering takes in a function z = f(x,y) where f(x,y) is a python lambda:
example: #align(center)[```python 
func = lambda x, y: numpy.sin(x) + numpy.cos(y)
```]

It also takes in params to control the limits of the surface to be shown in the x and y direction (+-limx and +-limy).

Then we iterate ix, iy over the ranges of [-limx,limx] and [-limy,limy] creating vertices with the coordinates (ix,iy,lambda(x,y)) and connect them with eachother using `triangulationNation`. Note that this implementation will not handle illegal or limits and can't render (or render accurately) discontinuous functions. 

= Shaders

= GUI
// explain user interface choices and navigation

= Performance

= Challenges encountered


#pagebreak()
#outline(title: "List of Figures", target: figure.where(kind: image))
