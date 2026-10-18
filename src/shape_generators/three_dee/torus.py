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
  verticalSlice = tools.uvSlicer(data,[
    {"splits":[v * ringCount for v in range(vertPerRing)]+[0]},
    # {"splits":[v * ringCount + ringCount//2 for v in range(vertPerRing)]+[ringCount//2]},
    # {"splits":[c for c in range(ringCount)]+[0]},
    # {"splits":[c for c in range(ringCount*vertPerRing//2,ringCount + ringCount*vertPerRing//2)]+[ringCount*vertPerRing//2]},


    # {"splits":[v * ringCount for v in range(vertPerRing)]+[0],"tears":[ringCount * vertPerRing//2+1,ringCount * (vertPerRing//2+1)-1]},
    # {"splits":[c for c in range(ringCount)]+[0],"tears":[ringCount + ringCount//2,ringCount*(vertPerRing-1) + ringCount//2]},
  ])
  rightSide = tools.getUvSide(data,verticalSlice,[0],[ringCount-1])
  horizontalSlice = tools.uvSlicer(data,[
    {"splits":[c for c in range(ringCount)]+[verticalSlice[0][rightSide]]},
  ])
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
  data["uvs"] = np.full((data["vertices"].shape[0],2),[0.0,0.0],dtype=np.float32)

  bottomSide = tools.getUvSide(data,horizontalSlice,[0],[ringCount*(vertPerRing-1)])
  # starts from top left, assign to top, left, topleft, and middle
  for x in range(ringCount):
    for y in range(vertPerRing-1,-1,-1):
      data["uvs"][y*ringCount+x] = [x/ringCount,y/vertPerRing]
  
  print(verticalSlice)
  # starts from top right, assign to topright and right
  for y in range(vertPerRing-1,-1,-1):
    data["uvs"][verticalSlice[y*ringCount+0][rightSide]] = [1,y/vertPerRing]
  
  # starts from bottom left, assign to bottom left and bottom
  for x in range(ringCount):
    data["uvs"][horizontalSlice[0*ringCount+x][rightSide]] = [x/ringCount,1]

  # assign to bottom right
    data["uvs"][horizontalSlice[verticalSlice[0][rightSide]][bottomSide]] = [1,1]
  
# stop looking at my screen, I can see you
# every time you intrude into my privacy I will take note