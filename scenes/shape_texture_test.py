from src.scene import Scene, AppOgl
import src.transform as transform
import numpy as np
from src.shape_generators.two_dee import triangle, rectangle, n_gon, trapezoid, star, arrow
from src.shape_generators.three_dee import cube, uv_sphere, cylinder, n_gon_pyramid, torus, surface
from types import MethodType


def scenes(gl_app: AppOgl):
  default_texture = "inputs/textures/colors.jpg"
  scenes = {}
  shapes={
    "triangle"       : {"gen": lambda: triangle.generate() },
    "rectangle"      : {"gen": lambda: rectangle.generate()},
    "pentagon"       : {"gen": lambda: n_gon.generate(shape_type="pentagon")},
    "hexagon"        : {"gen": lambda: n_gon.generate(shape_type="hexagon") },
    "circle"         : {"gen": lambda: n_gon.generate(shape_type="circle")  },
    "ellipse"        : {"gen": lambda: n_gon.generate(shape_type="ellipse") },
    "trapezoid"      : {"gen": lambda: trapezoid.generate()},
    "star"           : {"gen": lambda: star.generate()     },
    "arrow"          : {"gen": lambda: arrow.generate()    },
    "cube"           : {"gen": lambda: cube.generate()      ,"texture":"inputs/textures/cube_test_texture.jpg"},
    "sphere"         : {"gen": lambda: uv_sphere.generate()},
    "cylinder"       : {"gen": lambda: cylinder.generate() },
    "cone"           : {"gen": lambda: n_gon_pyramid.generate(shape_type="cone")},
    "truncated_cone" : {"gen": lambda: cylinder.generate(top_mult=0.5)          },
    "tetrahedron"    : {"gen": lambda: n_gon_pyramid.generate(shape_type="tetrahedron")},
    "torus"          : {"gen": lambda: torus.generate()},
    "prism"          : {"gen": lambda: cylinder.generate(n=3)},
    "surface"        : {"gen": lambda: surface.generate(limx=5,limy=5,n=3,func=lambda x,y: np.sin(x)+np.sin(y))},
  }
  def make_build_scene(name):
    def build_scene(self):
      self.program_name = "unwrap"
      self.gl_app.create_program("unwrap")
      self.color_mode = "texture"

      obj = shapes[name]["gen"]()
      
      objId, _ = self.add_object(f"!texture_{name}", data=obj)
      self.update_object(
        objId,
        program_name="unwrap",
        textures={"image": shapes[name].get("texture",default_texture)},
        color_mode="texture",
      )

    return build_scene

  for name in shapes:
    scene = Scene(gl_app)
    scene.build_scene = MethodType(make_build_scene(name), scene)
    scenes[f"!texture_{name}"] = scene

  return scenes
