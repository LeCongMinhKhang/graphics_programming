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

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
  vertices = np.array([[-1, -1, 0], [1, -1, 0], [-1, 1, 0], [1, 1, 0]], dtype=np.float32)
  colors = np.array([[0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0]], dtype=np.float32)
  normals = np.array([[0, 0, 1]] * vertices.shape[0], dtype=np.float32)
  vert_shader = "./shaders/interp.vert"
  frag_shader = "./shaders/resolution.frag"
  indices = np.array([0, 1, 2, 3], dtype=np.int32)

  # define scene data, one list entry per object (a dictionary)
  data = [
    {
      "vertices": vertices,
      "normals": normals,
      "colors": colors,
      "vert_shader": vert_shader,
      "frag_shader": frag_shader,
      "indices": indices,
      "mode": GL.GL_TRIANGLE_STRIP,
    }
  ]

  src.window.display(data)
