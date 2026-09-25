
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
We choose to have object data to be put into the pipeline as a dictionary with the form:
```
{
  "vertices": np.array((n, 3))
  "indices"(optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
  "colors": np.array((n, 3)) each component must be in [0, 1]
  "normals": np.array((n, 3))
  "mode": GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
}
```
And all the generators and .obj files shall be converted to this format before being rendered.
For the sake of simplicity, we decided to just assume that the rendering mode will always be GL_TRIANGLES, and for now, have colors and normals be automatically populated
Vertex colors are generated as some formula here
normals are always initialised as [0,0,0]

== Obj files
From the wiki, we can glance that obj files are formatted as
```
<fieldtype> <field1> <field2> <etc..>
# example
v 1.0 1.0 1.0
v 1.0 0.0 1.0
v 1.0 1.0 0.0
f 1 2 3
```
At the moment we shall only focus on the 2 fields v (Vertex) and f (Triangle).

For vertices, we read in the "v" fields as is
For triangles, .obj files actually has the "f" fields be 1-indexed, as such, converting "f" fields to "indices" will need to decrement all referenced indices by 1
Moreover, .obj's "f" fields are already set up to be rendered in the mode GL_TRIANGLES as is so we don't need to touch it
== 2D shapes
=== `__circularish` helper function
Generating circles comes in quite often in some of the 2D and 3D shapes, thus a helper function like `__circularish` comes in very handy.

The exact functionality varies depending on use cases (which is why the function is copied accross files instead of declared and imported). But in general, it takes:
- n: a number of vertices it will generate
- size: distance from (0,0,z) it vertices will be
- z: the z coordinate of vertices

it follows:

given step size

#align(center)[$theta = frac(2 pi, n)$]

for i in range(n) we create a new vertex at coordinate

#align(center)[$(cos (i theta) times "size",sin (i theta) times "size", z)$]

=== Simple 2D shapes (triangle, rectangle, trapezoid, arrow)
Most of these simple shapes have vertices and faces predefined, only taking in arguments to scale some attributes as a nicety, otherwise, basically hardcoded

image here

image here

image here

=== n-gon shapes (pentagon, hexagon, circle, ellipse)
All of these shapes can be generated with some variation of the `__circularish` function. Notably:
- Pentagon: n = 5
- Hexagon: n = 6
- Circle: n = 60
- Ellipse: n = 60, with a multiplier to the width of the n-gon in one of the axis

For triangulation, these shapes are triangulated to all have 1 common vertex, and then iterate around the n-gon for the other 2 vertices. This ensures the correct ordering of the indices but leads to rendering artifacts (pinching) around the common vertex. A better way would be to do it in zigzag strips, like a triangle fan. But I'm lazy

== 3D shapes
=== `triangulationNation` helper function
A lot of 3d shapes are more conveniently generated as quads (4 sided polygon). However, to keep consistency with the always GL_TRIANGLES thing, we have a helper function to convert a list of quads into the properly ordered list of triangle.

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
=== Cube
much like the simple 2d shapes, has args for nicety, but mostly hardcoded

=== Simple `__circularish` and `triangulationNation` shapes (cylinder, cone, truncated cone, tetrahedron, prism)
All of these shapes is some combination of `__circularish` and `triangulationNation` applications as a side walls:
- cylinder: 2 circles with a list of quads connecting the two
- prism: 2 triangles with a list of quads connecting the two
- truncated cone: a cylinder with 1 of the circles smaller than the other
- cone: an n-gon pyramid, with a circle as the base and kind of triangle fan as the side
- tetrahedron: a cone with a triangle as a base
=== Sphere and torus
These shapes utilises similar methodology as the previous shapes with some strong distinctions.

There are multiple ways to create a sphere, but we chose uv sphere to take advantage of tricks we have used before.
In which, a sphere contains multiple `__circularish` with various sizes and z placements, akin to the latitudes of a globe. These rings are then connected to eachother with a loop of creating a listOfQuads
At the pole, it is kind of triangle fan.

For a torus, one could make it by creating a vertical circle, and then apply some matrix transformation to rotate it around the z axis, but we did it by making a circle offsetted off the z axis, referencing the distance from the z axis and the z positioning to create rings along side the doughnut with `__circularish`, and then use a different loop to construct a listOfQuads that connects them
=== Surface
Surface rendering takes in a function z = f(x,y) where f(x,y) is a python lambda x, y. It also has params to control the limits of what to show in the x and y direction (limx and limy). Then we iterate ix, iy over the ranges of [-limx,limx] and [-limy,limy] creating vertices with the coordinates (ix,iy,lambda(x,y)).
Finally we make another listOfQuads

= Shaders

= GUI
// explain user interface choices and navigation

= Performance

= Challenges encountered


#pagebreak()
#outline(title: "List of Figures", target: figure.where(kind: image))
