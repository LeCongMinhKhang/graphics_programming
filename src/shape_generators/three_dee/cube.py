import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)
def generate(size:  float = 1.0,
             color: str   = "normal",
             hex = 0xff69ff,
             **kwargs):
  size  = float(size)
  color = str(color)  
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")
  
  data = tools.dataStructure()
  vertices = np.empty((8,3),dtype=np.float32)
  p = size/2
  vertices[0] = [ -p ,  p ,  p]
  vertices[1] = [ -p ,  p , -p]
  vertices[2] = [ -p , -p ,  p]
  vertices[3] = [ -p , -p , -p]
  vertices[4] = [  p , -p ,  p]
  vertices[5] = [  p , -p , -p]
  vertices[6] = [  p ,  p ,  p]
  vertices[7] = [  p ,  p , -p]
  data["vertices"] = vertices
  listOfQuads = []
  # top
  listOfQuads.append([0,2,4,6])
  # bottom
  listOfQuads.append([7,5,3,1])

  for i in range(0,8,2):
    listOfQuads.append([(i+0)%8,(i+1)%8,(i+3)%8,(i+2)%8])

  data["indices"] = tools.quads2triangles(listOfQuads)
  tools.vertexNeighborNormals(data)
  tools.chooseColoring(color)(data, hex = hex)
  tools.dataToNumpyArray(data)
  uvTexture(data)
  
  return data

def uvTexture(data):
  isTheSame = tools.uvSlicer(data,[
    {"splits":[2,4],"tears":[0,6]},
    {"splits":[3,2,4,5],"tears":[1,7]},
  ])
  print(isTheSame)
  data["uvs"] = np.full((data["vertices"].shape[0],2),[0.0,0.0],dtype=np.float32)

  #  y=1     ? --- ?
  #          |     |
  #    ? --- 0 --- 6 --- ?
  #    |     |     |     |
  #    ? --- 1 --- 7 --- ?
  #          |     |
  #          3 --- 5
  #          |     |
  #x,y=0     2 --- 4
  
  data["uvs"][0] = [0.25,0.75]
  topSide = tools.getUvSide(data,isTheSame,[2,4],[0,6])
  data["uvs"][isTheSame[2][topSide]] = [0.25,1.0]
  data["uvs"][isTheSame[4][topSide]] = [0.5 ,1.0]
  data["uvs"][6] = [0.5 ,0.75]
  leftSide = tools.getUvSide(data,isTheSame,[2,3],[0,1])
  data["uvs"][isTheSame[2][leftSide]] = [0.0,0.75]
  data["uvs"][isTheSame[3][leftSide]] = [0.0,0.5 ]
  data["uvs"][1] = [0.25,0.5]
  data["uvs"][7] = [0.5 ,0.5]
  rightSide = tools.getUvSide(data,isTheSame,[4,5],[6,7])
  data["uvs"][isTheSame[4][rightSide]] = [0.75,0.75]
  data["uvs"][isTheSame[5][rightSide]] = [0.75,0.5 ]

  data["uvs"][3] = [0.25,0.25]
  data["uvs"][5] = [0.5 ,0.25]
  data["uvs"][2] = [0.25,0.0 ]
  data["uvs"][4] = [0.5 ,0.0 ]

  [print(i,data["uvs"][i]) for i in range(len(data["uvs"]))]

