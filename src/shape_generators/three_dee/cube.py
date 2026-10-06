import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)
def generate(size:  float = 1.0,
             color: str   = "position",
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
  tools.chooseColoring(color,textureColoring=textureColoring)(data)
  tools.dataToNumpyArray(data)
  
  return data

def textureColoring(data):
  normals = np.empty((8,2),dtype=np.float32)
  normals[0] = [1.0,0.0]
  normals[1] = [2/3,0.0]
  normals[2] = [1/3,0.0]
  normals[3] = [0.0,0.0]
  normals[4] = [1.0,0.5]
  normals[5] = [2/3,0.5]
  normals[6] = [1/3,0.5]
  normals[7] = [0.0,0.5]
  data["normals"] = normals