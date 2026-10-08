import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)


def generate(length:  float = 1.0,
             girth:   float = 1.0, 
             z:       float = 0.0, 
             color:   str   = "position",
             hex = 0xff69ff,
             **kwargs):
  length = float(length) 
  girth  = float(girth) 
  z      = float(z) 
  color  = str(color)   
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  if length <= girth/2:
    length = girth/2
    
  shaft_length = length - girth/2
  #           0.
  #           / \
  #          /   \
  #         /     \
  #        /       \
  #      1'--•---•--'2
  #         3|\  |6
  #          | \ |
  #          |  \|
  #         4'---'5  
  data = tools.dataStructure()

  vertices = np.zeros((7 if shaft_length > 0 else 3 ,3), dtype= np.float32)

  vertices[0][0], vertices[0][1], vertices[0][2] =         0, girth/2, z
  vertices[1][0], vertices[1][1], vertices[1][2] = - girth/2,       0, z
  vertices[2][0], vertices[2][1], vertices[2][2] =   girth/2,       0, z

  if shaft_length > 0:
    vertices[3][0], vertices[3][1], vertices[3][2] = - girth/4,              0, z
    vertices[4][0], vertices[4][1], vertices[4][2] = - girth/4, - shaft_length, z
    vertices[5][0], vertices[5][1], vertices[5][2] =   girth/4, - shaft_length, z
    vertices[6][0], vertices[6][1], vertices[6][2] =   girth/4,              0, z

    data["indices"] = [0,1,3,0,3,6,0,6,2,3,4,5,3,5,6]
  else:
    data["indices"] = [0,1,2]
    
  data["vertices"] = vertices

  data["normals" ] = np.full((data["vertices"].shape[0],3),[0.0,0.0,1.0],dtype=np.float32)

  tools.chooseColoring(mode=color,textureColoring=textureColoring)(data, hex = hex)

  tools.dataToNumpyArray(data)
  return data

def textureColoring(data):
  data["colors"] = data["vertices"][:,:2] / np.max(data["vertices"][:,:2]) / 2 + 0.5
  print(data["colors"])