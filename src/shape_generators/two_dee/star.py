import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(n:           int   = 5, 
             size:        float = 1.0, 
             size_inner:  float = 0.0, 
             z:           float = 0.0, 
             color:       str   = "position",
             **kwargs):
  n          = int(n)  
  size       = float(size)
  size_inner = float(size_inner)
  z          = float(z)
  color      = str(color)  
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  if n < 2:
    n = 2
  if size_inner <= 0:
    size_inner = 0.5 * size
  if size_inner >= 1:
    size_inner = 0.999
  data = tools.star_ngonGenerator(n,size,size*size_inner,z)

  data["normals" ] = np.full((data["vertices"].shape[0],3),[0.0,0.0,1.0],dtype=np.float32)

  tools.chooseColoring(mode=color,textureColoring=textureColoring)(data)

  tools.dataToNumpyArray(data)
  return data

def textureColoring(data):
  data["colors"] = data["vertices"][:,:2] / np.max(data["vertices"][:,:2]) / 2 + 0.5
  print(data["colors"])
# def __circularish(n,size,size_inner,z):
#   obj = {
#     "v"  : [],
#     "vt" : [],
#     "vn" : [],
#     "f"  : [],
#     "l"  : [],
#   }

#   for i in range(n):
#     theta = i * 2 * pi / n
#     alpha = theta + pi / n
#     obj["v"].append( [cos(theta) * size_inner, sin(theta) * size_inner, z] )
#     obj["v"].append( [      cos(alpha) * size,       sin(alpha) * size, z] )

#   for i in range(0, 2 * n, 2):
#     obj["f"].append( [[i,i+1,(i+2)%(2*n)]] )
#   # please verify that these generates actual triangles
#   for i in range(1,n-1):
#     obj["f"].append( [[0,2*i%(2*n),2*(i+1)%(2*n)]] )

#   return obj