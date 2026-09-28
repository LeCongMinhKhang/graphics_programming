import sys
import os
import numpy as np
import logging

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window  # noqa: E402
from src.camera.trackball import Trackball  # noqa: E402
import src.shape_generators.D3.uv_sphere  # noqa: E402

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def setup():
  sphere = src.shape_generators.D3.uv_sphere.generate(n=10)
  sphere["vert_shader"] = "./shaders/camera.vert"
  sphere["frag_shader"] = "./shaders/interp.frag"
  sphere["colors"] = ((sphere["vertices"] / np.abs(sphere["vertices"]).max()) * 0.5 + 0.5).astype(
    np.float32
  )
  return [sphere]


if __name__ == "__main__":
  data = setup()
  src.window.display(data, camera=Trackball)
