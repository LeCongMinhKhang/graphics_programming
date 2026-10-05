import sys
import os
import OpenGL.GL as GL
import numpy as np
import logging

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.tkwindow
from src.parsefile import objToPipelineable
from src.camera.trackball import Trackball

from src import parsefile
import argparse

from src.shape_generators.two_dee import triangle, trapezoid, rectangle, star, n_gon, arrow
from src.shape_generators.three_dee import cube, cylinder, n_gon_piramid, surface, uv_sphere, torus

parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default=None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default=None)
parser.add_argument("--wireframe", action="store_true", help="Render in Wireframe")
# args = parser.parse_args()
args, extra_args = parser.parse_known_args()

file_path = args.file
scene_path = args.scene
arbitrary_dict = {}
for i in range(0, len(extra_args), 2):
  # Ensure it looks like a flag and has a corresponding value
  if extra_args[i].startswith("--") and i + 1 < len(extra_args):
    key = extra_args[i].lstrip("-")
    val = extra_args[i + 1]
    arbitrary_dict[key] = val

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def getInput():
  if file_path is None and scene_path is None:
    parser.print_help()
    return None

  elif file_path is not None:
    return parsefile.parseFile(file_path)
  elif scene_path is not None:
    match scene_path:
      case "triangle":
        return triangle.generate(**arbitrary_dict)
      case "rectangle":
        return rectangle.generate(**arbitrary_dict)
      case "pentagon":
        return n_gon.generate(shape_type="pentagon", **arbitrary_dict)
      case "hexagon":
        return n_gon.generate(shape_type="hexagon", **arbitrary_dict)
      case "circle":
        return n_gon.generate(shape_type="circle", **arbitrary_dict)
      case "ellipse":
        return n_gon.generate(shape_type="ellipse", **arbitrary_dict)
      case "trapezoid":
        return trapezoid.generate(**arbitrary_dict)
      case "star":
        return star.generate(**arbitrary_dict)
      case "arrow":
        return arrow.generate(**arbitrary_dict)
      # 3d
      case "cube":
        return cube.generate(**arbitrary_dict)
      case "cylinder":
        return cylinder.generate(**arbitrary_dict)
      case "prism":
        return cylinder.generate(n=3, **arbitrary_dict)
      case "truncated_cone":
        return cylinder.generate(top_mult=0.5, **arbitrary_dict)
      case "cone":
        return n_gon_piramid.generate(shape_type="cone")
      case "tetrahedron":
        return n_gon_piramid.generate(shape_type="tetrahedron")
      case "surface":
        return surface.generate(func=lambda x, y: np.sin(x) + np.sin(y))
      case "sphere":
        return uv_sphere.generate(n=16)
      case "torus":
        return torus.generate(n=8)


if __name__ == "__main__":
  vert_shader = "./shaders/turn.vert"
  frag_shader = "./shaders/interp.frag"
  obj = getInput()
  if obj is not None:
    data = [obj]
    data[0]["vert_shader"] = vert_shader
    data[0]["frag_shader"] = frag_shader

    src.tkwindow.display(data, camera=Trackball, wireframe=args.wireframe)
