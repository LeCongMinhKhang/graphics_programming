import sys
import os
import numpy as np
import logging
import OpenGL.GL as GL

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window  # noqa: E402
from src.camera.trackball import Trackball  # noqa: E402
import src.shape_generators.D3.uv_sphere  # noqa: E402
import src.transform  # noqa: E402

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def setup():
  sphere_tr = src.shape_generators.D3.uv_sphere.generate(n=10)
  sphere_tr["vert_shader"] = "./shaders/camera.vert"
  sphere_tr["frag_shader"] = "./shaders/interp.frag"
  sphere_tr["model_matrix"] = src.transform.translate(-1, 0, 0)
  sphere_tr["mode"] = GL.GL_TRIANGLES

  sphere_ln = sphere_tr.copy()
  sphere_ln["model_matrix"] = src.transform.translate(0, 0, 0)
  sphere_ln["mode"] = GL.GL_LINES

  sphere_pt = sphere_ln.copy()
  sphere_pt["model_matrix"] = src.transform.translate(1, 0, 0)
  sphere_pt["mode"] = GL.GL_POINTS

  return [sphere_tr, sphere_ln, sphere_pt]


if __name__ == "__main__":
  data = setup()
  src.window.display(data, camera=Trackball)
