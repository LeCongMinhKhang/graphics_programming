from numpy import sqrt
import numpy as np
from .. import tools

import logging

logger = logging.getLogger(__name__)


def generate(size: float = 1.0, z: float = 0.0, color: str = "position", **kwargs):
  size = float(size)
  z = float(z)
  color = str(color)
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  data = tools.dataStructure()
  # With the center of the triangle at 0,0,z
  vertices = np.zeros((3, 3), dtype=np.float32)
  height = size * sqrt(3) / 2
  vertices[0][0], vertices[0][1], vertices[0][2] = 0.0, 2 * height / 3, z
  vertices[1][0], vertices[1][1], vertices[1][2] = -size / 2, -height / 3, z
  vertices[2][0], vertices[2][1], vertices[2][2] = size / 2, -height / 3, z
  data["vertices"] = vertices

  # data["normals" ] = np.full((data["vertices"].shape[0],3),[0.0,0.0,1.0],dtype=np.float32)
  # ????? numpy array slices ?????
  # data["normals" ] = np.zeros((data["vertices"].shape[0],3),dtype=np.float32)
  # data["normals" ][:,0], data["normals"][:,1],data["normals"][:,2] = 0.0, 0.0, 1.0

  data["indices"] = np.array([0, 1, 2], dtype=np.uint32)

  tools.vertexNeighborNormals(data)

  tools.chooseColoring(mode=color, textureColoring=textureColoring)(data)
  tools.dataToNumpyArray(data)
  return data


def textureColoring(data):
  data["colors"] = np.array([[0.0, 1.0], [0.5, 0.0], [1.0, 1.0]], dtype=np.float32)
