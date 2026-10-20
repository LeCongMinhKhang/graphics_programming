from numpy import pi, cos, sin
import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(thickness: float = 1.0, 
             hole_size: float = 1.0,
             n:         int   = 8, 
             color:     str   = "hex",
             hex = 0xffffff,
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
  tools.chooseColoring(color)(data, hex = hex)
  uvTexture(data,ringCount=ringCount,vertPerRing=n)
  tools.dataToNumpyArray(data)
  
  return data

def uvTexture(data,ringCount,vertPerRing):
  # me when I box splitter attack:
  
  verticalSlice = tools.uvSlicer(data,[
    {"splits":[v * ringCount for v in range(vertPerRing)]+[0]},
  ])
  leftSide = tools.getUvSide(data,verticalSlice,[0],[1])
  rightSide = tools.getUvSide(data,verticalSlice,[0],[ringCount-1])
  
  horizontalSlice = tools.uvSlicer(data,[
    {"splits":[verticalSlice[0][leftSide]]+[c for c in range(1,ringCount)]+[verticalSlice[0][rightSide]]},
  ])
  # topSide = tools.getUvSide(data,horizontalSlice,[0],[ringCount])
  # bottomSide = tools.getUvSide(data,horizontalSlice,[0],[ringCount*(vertPerRing-1)])
  topSide = tools.getUvSide(data,horizontalSlice,[0],[ringCount*(vertPerRing-1)])
  bottomSide = tools.getUvSide(data,horizontalSlice,[0],[ringCount])
  
  # sides of uv mapped
  #               -rc+
  #     tl ------ top ------- tr
  #      |                    |
  # -    l                    r
  # v    e                    i
  # p    f      middle        g
  # r    t                    h
  # +    |                    t
  #      |                    |
  #     bl----- bottom ------ br
  # quite annoying that (IringCount,IvertexPerRing) is upside down compared to (uvx,uvy)

  data["uvs"] = np.full((data["vertices"].shape[0],2),[5.0,5.0],dtype=np.float32)
  
  # middle
  for x in range(1,ringCount):
    for y in range(1,vertPerRing):
      data["uvs"][y*ringCount+x] = [x/ringCount,y/vertPerRing]
  
  # topleft
  data["uvs"][horizontalSlice[verticalSlice[0][leftSide]][topSide]] = [0,1]
  # top
  for x in range(1,ringCount):
    data["uvs"][horizontalSlice[0*ringCount+x][topSide]] = [x/ringCount,1]
  # topright
  data["uvs"][horizontalSlice[verticalSlice[0][rightSide]][topSide]] = [1,1]

  # left
  for y in range(1,vertPerRing):
    data["uvs"][verticalSlice[y*ringCount+0][leftSide]] = [0,y/vertPerRing]
  # right
  for y in range(1,vertPerRing):
    data["uvs"][verticalSlice[y*ringCount+0][rightSide]] = [1,y/vertPerRing]
  
  # # bottomleft
  data["uvs"][horizontalSlice[verticalSlice[0][leftSide]][bottomSide]] = [0,0]
  # bottom
  for x in range(1,ringCount):
    data["uvs"][horizontalSlice[0*ringCount+x][bottomSide]] = [x/ringCount,0]
  # bottomright
  data["uvs"][horizontalSlice[verticalSlice[0][rightSide]][bottomSide]] = [1,0]
  