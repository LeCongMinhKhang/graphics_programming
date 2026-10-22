import numpy as np
from .. import tools

import logging

logger = logging.getLogger(__name__)


def generate(
  shape_type: str = "cone",
  base: float = 1.0,
  height: float = 2.0,
  color: str = "position",
  hex = 0xff69ff,
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
  tools.chooseColoring(color)(data, hex = hex)
  uvTexture(data,height,base,n)
  tools.dataToNumpyArray(data)

  return data


def uvTexture(data,height,radius,n):
  mercatorProjection = tools.uvSlicer(data,[
    {"splits":[0],"tears":[n,n+1]},
  ] + [
    # bottom edge
    {"splits":[n],"tears":[i,None]} for i in range(n)
  ] + [
    # top edge
    {"splits":[n+1],"tears":[i,None]} for i in range(n)
  ])
  data["uvs"] = np.full((data["vertices"].shape[0],2),[5,5],dtype=np.float32)
  # ratioSide = height/(height+radius)
  ratioBase = radius/(height+radius)
  
  # middle
  for i in range(1,n):
    data["uvs"][i]   = [i/n,ratioBase]
    if i < n-1:
      correctSideBottomEdge = tools.getUvSide(data,mercatorProjection,[n],[i,i+1])
      data["uvs"][mercatorProjection[n][correctSideBottomEdge]] = [(i+0.5)/n,0]
      correctSideTopEdge = tools.getUvSide(data,mercatorProjection,[n+1],[i,i+1])
      data["uvs"][mercatorProjection[n+1][correctSideTopEdge]] = [(i+0.5)/n,1]
  # left right 
  leftSide = tools.getUvSide(data,mercatorProjection,[0],[1])
  data["uvs"][mercatorProjection[0][leftSide]] = [0,ratioBase]
  rightSide = tools.getUvSide(data,mercatorProjection,[0],[n-1])
  data["uvs"][mercatorProjection[0][rightSide]] = [1,ratioBase]

  # topright bottomright
  bottomRight = tools.getUvSide(data,mercatorProjection,[n+1],[n-1,mercatorProjection[0][rightSide]])
  data["uvs"][mercatorProjection[n+1][bottomRight]] = [(n-0.5)/n,1]
  topRight = tools.getUvSide(data,mercatorProjection,[n],[n-1,mercatorProjection[0][rightSide]])
  data["uvs"][mercatorProjection[n][topRight]] = [(n-0.5)/n,0]
  # topleft bottomleft 
  topLeft = tools.getUvSide(data,mercatorProjection,[n+1],[n+1,mercatorProjection[0][leftSide]])
  data["uvs"][mercatorProjection[n+1][topLeft]] = [0.5/n,1]
  bottomLeft = tools.getUvSide(data,mercatorProjection,[n],[1,mercatorProjection[0][leftSide]])
  data["uvs"][mercatorProjection[n][bottomLeft]] = [0.5/n,0]
