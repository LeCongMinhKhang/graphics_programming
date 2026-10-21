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
  tools.chooseColoring(color)(data, hex = hex)
  uvTexture(data,numOfVertPerLatRing,n)
  tools.dataToNumpyArray(data)
  return data

def uvTexture(data,novplr,n):
  poleIndex = novplr * n

  mercatorProjection = tools.uvSlicer(data,[
    # pole to pole
    {"splits":[i*novplr for i in range(n)],"tears":[poleIndex,poleIndex+1]},
  ] + [
    # bottom edge
    {"splits":[poleIndex],"tears":[i,None]} for i in range(novplr)
  ] + [
    # top edge
    {"splits":[poleIndex+1],"tears":[i+(n-1)*novplr,None]} for i in range(novplr)
  ])
  data["uvs"] = np.full((data["vertices"].shape[0],2),[5,5],dtype=np.float32)
  
  data["colors"][0] = [1,0,1]
  
  # middle
  for i in range(n):
    for j in range(1,novplr):
      data["uvs"][i*novplr + j]   = [j/novplr,(i+1)/(n+1)]
  for i in range(1,novplr-1):
    correctSideBottomEdge = tools.getUvSide(data,mercatorProjection,[poleIndex],[i,i+1])
    data["uvs"][mercatorProjection[poleIndex][correctSideBottomEdge]] = [(i+0.5)/novplr,0]
    correctSideTopEdge = tools.getUvSide(data,mercatorProjection,[poleIndex+1],[i+(n-1)*novplr,i+(n-1)*novplr+1])
    data["uvs"][mercatorProjection[poleIndex+1][correctSideTopEdge]] = [(i+0.5)/novplr,1]
  # left right 
  leftSide = tools.getUvSide(data,mercatorProjection,[0],[1])
  rightSide = tools.getUvSide(data,mercatorProjection,[0],[novplr-1])
  for i in range(n):
    data["uvs"][mercatorProjection[i*novplr][leftSide]] = [0,(i+1)/(n+1)]
    data["uvs"][mercatorProjection[i*novplr][rightSide]] = [1,(i+1)/(n+1)]

  # topright bottomright
  topRight = tools.getUvSide(data,mercatorProjection,[poleIndex+1],[n*novplr-1,mercatorProjection[(n-1)*novplr][rightSide]])
  data["uvs"][mercatorProjection[poleIndex+1][topRight]] = [(novplr-0.5)/novplr,1]
  bottomRight = tools.getUvSide(data,mercatorProjection,[poleIndex],[novplr-1,mercatorProjection[0][rightSide]])
  data["uvs"][mercatorProjection[poleIndex][bottomRight]] = [(novplr-0.5)/novplr,0]
  # topleft bottomleft 
  topLeft = tools.getUvSide(data,mercatorProjection,[poleIndex+1],[(n-1)*novplr+1,mercatorProjection[(n-1)*novplr][leftSide]])
  data["uvs"][mercatorProjection[poleIndex+1][topLeft]] = [0.5/novplr,1]
  bottomLeft = tools.getUvSide(data,mercatorProjection,[poleIndex],[1,mercatorProjection[0][leftSide]])
  data["uvs"][mercatorProjection[poleIndex][bottomLeft]] = [0.5/novplr,0]