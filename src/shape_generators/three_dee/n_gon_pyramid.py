import numpy as np
from .. import tools

import logging

logger = logging.getLogger(__name__)


def generate(
  shape_type: str = "cone",
  base: float = 1.0,
  height: float = 2.0,
  color: str = "position",
  **kwargs,
):
  shape_type = str(shape_type)
  base = float(base)
  height = float(height)
  color = str(color)
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  n = 6
  z = 0
  if base <= 0:
    logger.warning("invalid size 0")
    base = 0.001
  if height <= 0:
    logger.warning("invalid size 0")
    height = 0.001

  if shape_type == "tetrahedron":
    n = 3
    edge_length = base * np.sqrt(3)
    height = edge_length * np.sqrt(6) / 3
    z = height / 4

  else:
    n = 36
  data = tools.dataStructure()
  data["vertices"] = tools.simple_ngonGenerator(n, base, -height / 2 + z)

  data["vertices"].append([0, 0, -height / 2 + z])
  data["vertices"].append([0, 0, height / 2 + z])

  for i in range(n):
    data["indices"].append(n)
    data["indices"].append((i + 1) % (n))
    data["indices"].append(i)

    data["indices"].append(n + 1)
    data["indices"].append(i)
    data["indices"].append((i + 1) % (n))
  tools.dataToNumpyArray(data)

  tools.vertexNeighborNormals(data)
  tools.chooseColoring(color, textureColoring=textureColoring)(data)
  tools.dataToNumpyArray(data)

  return data


def textureColoring(data):
  data["colors"] = np.empty((data["vertices"].shape[0], 2), dtype=np.float32)
  baseNum = data["vertices"].shape[0] - 2
  for i in range(baseNum):
    data["colors"][i] = [i / (baseNum - 1), i / (baseNum - 1)]
  data["colors"][baseNum] = [1.0, 0.0]
  data["colors"][baseNum + 1] = [0.0, 1.0]
