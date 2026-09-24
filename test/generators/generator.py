import sys
import os
import OpenGL.GL as GL
import numpy as np
import logging

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window
from src.parsefile import objToPipelineable
from src.camera.trackball import Trackball

from src import parsefile
import argparse

from inputs.two_dee import triangle,trapezoid,rectangle,star,n_gon,arrow
from inputs.three_dee import cube, cylinder, n_gon_piramid, surface, uv_sphere, torus

parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default=None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default=None)
args = parser.parse_args()

file_path = args.file
scene_path = args.scene

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
        return triangle.generate()
      case "rectangle":
        return rectangle.generate()
      case "pentagon":
        return n_gon.generate("pentagon")
      case "hexagon":
        return n_gon.generate("hexagon")
      case "circle":
        return n_gon.generate("circle")
      case "ellipse":
        return n_gon.generate("ellipse")
      case "trapezoid":
        return trapezoid.generate()
      case "star":
        return star.generate()
      case "arrow":
        return arrow.generate()
      # 3d
      case "cube":
        return cube.generate()
      case "cylinder":
        return cylinder.generate()
      case "prism":
        return cylinder.generate(1.0,3)
      case "truncated_cone":
        return cylinder.generate(0.5)
      case "cone":
        return n_gon_piramid.generate("cone")
      case "tetrahedron":
        return n_gon_piramid.generate("tetrahedron")
      case "surface":
        return surface.generate(lambda x,y: np.sin(x)+np.sin(y),5,5,3)
      case "sphere":
        return uv_sphere.generate()
      case "torus":
        return torus.generate(n=8)

if __name__ == "__main__":
  vert_shader = "./shaders/cube.vert"
  frag_shader = "./shaders/interp.frag"
  obj = getInput()
  if obj is not None:
    data = [objToPipelineable(obj)]
    data[0]["vert_shader"] = vert_shader
    data[0]["frag_shader"] = frag_shader

    src.window.display(data, camera=Trackball)
