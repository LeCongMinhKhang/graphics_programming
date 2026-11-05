from OpenGL import GL
import numpy as np
from .. import tools

import logging

logger = logging.getLogger(__name__)


def generate(
  topleft=(-0.5, 1),
  width: float = 1.0,
  height: float = 2.0,
  z: float = 0.0,
  color: str = "hex",
  hexa=0xFF69FF,
  **kwargs,
):
  width = float(width)
  height = float(height)
  z = float(z)
  color = str(color)
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  data = tools.dataStructure()
  left = topleft[0]
  right = left + width
  top = topleft[1]
  bot = top - height
  vertices = [[left, top, z], [right, top, z], [right, bot, z], [left, bot, z]]
  data["vertices"] = vertices

  data["normals"] = [[0, 0, 1] for i in range(len(vertices))]

  # data["indices"] = [0, 1, 2, 3, 0]
  data["indices"] = [0, 1, 1, 2, 2, 3, 3, 0]

  data["gl_mode"] = GL.GL_LINES

  tools.chooseColoring(mode=color)(data, hexa=hexa)
  uvTexture(data)
  tools.dataToNumpyArray(data)
  return data


def uvTexture(data):
  data["uvs"] = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
