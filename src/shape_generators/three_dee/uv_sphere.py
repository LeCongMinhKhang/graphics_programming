from numpy import pi, cos, sin
import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(size:  float = 1.0, 
             n:     int   = 12, 
             color: str   = "normal",
             hex = 0xff69ff,
             **kwargs):
  size  = float(size) 
  n     = int(n)   
  color = str(color)   
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  if size <= 0:
    size = 0.001
  # n is the magical density number whatever the hell
  if n < 1:
    n = 1
    
  data = tools.dataStructure()

  listOfLatitudes = []
  for i in range(1,n+1):
    listOfLatitudes.append( i * pi / (n + 1))

  numOfVertPerLatRing = 2 * (n+1)
  vertices = np.empty((numOfVertPerLatRing*n+2,3),dtype=np.float32)
  for i in range(n):
    vertices[numOfVertPerLatRing*i:numOfVertPerLatRing*(i+1)] = tools.simple_ngonGenerator(
        numOfVertPerLatRing, 
        sin(listOfLatitudes[i])*size,  # the radius of the lat ring
        - cos(listOfLatitudes[i])*size # z height of the lat ring
        )
  
  index = lambda i,j: i * numOfVertPerLatRing + j % numOfVertPerLatRing

  listOfQuads = []
  for i in range(n-1):
    for j in range(numOfVertPerLatRing):
      listOfQuads.append([index(i,j),index(i,j+1),index(i+1,j+1),index(i+1,j)])
  indices = tools.quads2triangles(listOfQuads)

  # the poles
  poleIndex = numOfVertPerLatRing * n
  vertices[numOfVertPerLatRing*n]     = [0,0, - size]
  vertices[numOfVertPerLatRing*n + 1] = [0,0,   size]

  # triangle fan the long way around
  for i in range (numOfVertPerLatRing):
    indices.append(poleIndex)
    indices.append((i+1) % numOfVertPerLatRing)
    indices.append(i)
    
    indices.append(poleIndex + 1)
    indices.append(poleIndex - 1 - (i+1) % numOfVertPerLatRing)
    indices.append(poleIndex - 1 - i)

  data["vertices"] = vertices
  data["indices" ] = indices

  tools.vertexNeighborNormals(data)
  tools.chooseColoring(color,textureColoring=textureColoring)(data, hex = hex,latNum=n,numOfVertPerLatRing=numOfVertPerLatRing)
  tools.dataToNumpyArray(data)
  return data

def textureColoring(data,latNum,numOfVertPerLatRing):
  data["colors"] = np.zeros((latNum*numOfVertPerLatRing + 2, 2), dtype= np.float32)
  for i in range(1,latNum):
    for j in range(numOfVertPerLatRing):
      data["colors"][i * numOfVertPerLatRing + j][0],data["colors"][1] = j / (numOfVertPerLatRing-1) ,1.0 - i / latNum
  
  poleIndex = latNum*numOfVertPerLatRing
  data["colors"][poleIndex    ][0], data["colors"][poleIndex    ][1] = 0.0,1.0
  data["colors"][poleIndex + 1][0], data["colors"][poleIndex + 1][1] = 1.0,0.0
 
# def __circularish(n,size,z):
#   res = []
#   for i in range(n):
#     theta = i * 2 * pi / n
#     res.append( [cos(theta) * size , sin(theta) * size, z] )
#   return res