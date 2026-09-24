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
from src.camera.trackball import Trackball

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
  vertices = np.array(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]],
    dtype=np.float32,
  )
  colors = np.array([[1, 0, 0], [0, 1, 0]] * int(vertices.shape[0] / 2), dtype=np.float32)
  normals = np.array(
    [
      [-1, -1, -1],
      [1, -1, -1],
      [-1, 1, -1],
      [1, 1, -1],
      [-1, -1, 1],
      [1, -1, 1],
      [-1, 1, 1],
      [1, 1, 1],
    ],
    dtype=np.float32,
  )
  vert_shader = "./shaders/cube.vert"
  frag_shader = "./shaders/interp.frag"
  indices = np.array(
    [
      0,
      2,
      3,
      0,
      3,
      1,  # back  face (z = 0), normal -z
      4,
      5,
      7,
      4,
      7,
      6,  # front face (z = 1), normal +z
      0,
      1,
      5,
      0,
      5,
      4,  # bottom face (y = 0), normal -y
      2,
      6,
      7,
      2,
      7,
      3,  # top face (y = 1), normal +y
      0,
      4,
      6,
      0,
      6,
      2,  # left face (x = 0), normal -x
      1,
      3,
      7,
      1,
      7,
      5,  # right face (x = 1), normal +x
    ],
    dtype=np.uint32,
  )

  # define scene data, one list entry per object (a dictionary)
  data = [
    {
      "vertices": vertices,
      "normals": normals,
      "colors": colors,
      "vert_shader": vert_shader,
      "frag_shader": frag_shader,
      "indices": indices,
      "mode": GL.GL_TRIANGLES,
    }
  ]

  src.window.display(data, camera=Trackball)
