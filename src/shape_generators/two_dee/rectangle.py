import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)


def generate(width = 1.0,height = 2.0, z = 0.0, color = "position",**kwargs):
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  data = tools.dataStructure()
  #      0.----.3
  #       |\   |
  #       | \  |
  #       |  \ |
  #       |   \|
  #      1'----'2
  vertices = np.zeros((4,3),dtype=np.float32)
  vertices[0][0], vertices[0][1], vertices[0][2] = - width/2,   height/2, z 
  vertices[1][0], vertices[1][1], vertices[1][2] = - width/2, - height/2, z 
  vertices[2][0], vertices[2][1], vertices[2][2] =   width/2, - height/2, z 
  vertices[3][0], vertices[3][1], vertices[3][2] =   width/2,   height/2, z 
  data["vertices"] = vertices

  data["normals" ] = np.full((data["vertices"].shape[0],3),[0.0,0.0,1.0],dtype=np.float32)

  data["indices" ] = np.array(tools.quads2triangles([[0,1,2,3]]),dtype=np.uint32)
  
  tools.chooseColoring(mode=color,textureColoring=textureColoring)(data)

  tools.dataToNumpyArray(data)
  return data

def textureColoring(data):
  data["colors"] = np.array([[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0]],dtype= np.float32)