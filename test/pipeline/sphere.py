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
from src.shape_generators.three_dee import uv_sphere, torus, surface, n_gon_piramid, cylinder, cube
import numpy as np

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def setup():
  # sphere = src.shape_generators.D3.uv_sphere.generate(n=10)
  
  # sphere = uv_sphere.generate(n=10)
  # sphere = torus.generate(n=100)
  # sphere = surface.generate(func = lambda x, y: np.sin(x) + np.sin(y), limx=25,limy=25,color="position",calcNormals=True,n=3)
  # sphere= n_gon_piramid.generate(shape_type="cone",color= "normal")
  # sphere = cylinder.generate()
  sphere = cube.generate()

  sphere["vert_shader"] = "./shaders/camera.vert"
  sphere["frag_shader"] = "./shaders/interp.frag"
  # sphere["colors"] = ((sphere["vertices"] / np.abs(sphere["vertices"]).max()) * 0.5 + 0.5).astype(
  #   np.float32
  # )
  return [sphere]


if __name__ == "__main__":
  data = setup()
  src.window.display(data, camera=Trackball)
