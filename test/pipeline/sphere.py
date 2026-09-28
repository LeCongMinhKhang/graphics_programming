import sys
import os
import OpenGL.GL as GL
import numpy as np
import logging

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window  # noqa: E402
from src.camera.trackball import Trackball  # noqa: E402
from inputs.three_dee import uv_sphere
from src.parsefile import objToPipelineable

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def setup():
  vert_shader = "./shaders/camera.vert"
  frag_shader = "./shaders/interp.frag"
  data = [objToPipelineable(uv_sphere.generate(n=10))]
  data[0]["vert_shader"] = vert_shader
  data[0]["frag_shader"] = frag_shader
  return data


if __name__ == "__main__":
  data = setup()
  src.window.display(data, camera=Trackball)
