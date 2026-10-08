from numpy import pi, cos, sin
import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(thickness: float = 1.0, 
             hole_size: float = 1.0,
             n:         int   = 8, 
             color:     str   = "normal",
             hex = 0xff69ff,
             **kwargs):
  thickness = float(thickness) 
  hole_size = float(hole_size) 
  n         = int(n)   
  color     = str(color)   
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  if thickness <= 0:
    thickness = 0.001
  if hole_size <= 0:
    hole_size = 0.001
  # n is the magical density number whatever the hell
  if n < 3:
    n = 3
  data = tools.dataStructure()
  ringCount = 2*n
  tempRing = tools.simple_ngonGenerator(n,thickness,0)
  centerOffset = thickness + hole_size
  vertices = []
  for ring in tempRing:
   vertices = vertices + tools.simple_ngonGenerator(ringCount,centerOffset - ring[0],ring[1])
  data["vertices"] = np.array(vertices,dtype=np.float32)

  index = lambda i,j: (i % n) * ringCount + j % ringCount
  listOfQuads = []
  for i in range(n+1):
    for j in range(ringCount+1):
      listOfQuads.append([index(i+1,j),index(i+1,j+1),index(i,j+1),index(i,j)])
  data["indices"] = tools.quads2triangles(listOfQuads)
  tools.vertexNeighborNormals(data)
  tools.chooseColoring(color,textureColoring=textureColoring)(data, hex = hex,ringCount=ringCount,vertPerRing=n)
  tools.dataToNumpyArray(data)
  
  return data

def textureColoring(data,ringCount,vertPerRing):
  data["colors"] = np.zeros((ringCount*vertPerRing, 2), dtype= np.float32)
  for i in range(1,ringCount):
    for j in range(1,vertPerRing):
      data["colors"][i*vertPerRing + j][0],data["colors"][1] = i / (ringCount-1) ,1.0 - j / (vertPerRing-1)
  
  

# def __circularish(n,size,z):
#   res = []
#   for i in range(n):
#     theta = i * 2 * pi / n
#     res.append( [cos(theta) * size , sin(theta) * size, z] )
#   return res