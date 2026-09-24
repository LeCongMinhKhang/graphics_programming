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
from inputs.two_dee.star import generate
from src.camera.trackball import Trackball

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
  vert_shader = "./shaders/cube.vert"
  frag_shader = "./shaders/interp.frag"

  data = [objToPipelineable(generate())]
  data[0]["vert_shader"] = vert_shader
  data[0]["frag_shader"] = frag_shader

  src.window.display(data, camera=Trackball)
