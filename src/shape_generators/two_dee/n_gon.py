import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(shape_type:  str   = "circle",
             size:        float = 1.0, 
             size_wide:   float = 0.8, 
             z:           float = 0.0, 
             color:       str   = "position",
             **kwargs):
  shape_type = str(shape_type)   
  size       = float(size) 
  size_wide  = float(size_wide) 
  z          = float(z) 
  color      = str(color)   
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")

  n = 3
  w_multiplier = 1
  if size <= 0:
    print("Warning: invalid size 0")
    size = 0.001

  match(shape_type):
    case "pentagon": n = 5
    case "hexagon":  n = 6
    case "circle":   n = 60
    case "ellipse":  
      n = 60
      w_multiplier = size_wide/size
    case _: n = 3

  data = tools.ngon_ngonGenerator(n,size,w_multiplier,z)

  data["normals" ] = np.full((data["vertices"].shape[0],3),[0.0,0.0,1.0],dtype=np.float32)

  tools.chooseColoring(mode=color,textureColoring=textureColoring)(data)

  tools.dataToNumpyArray(data)
  return data

def textureColoring(data):
  data["colors"] = data["vertices"][:,:2] / np.max(data["vertices"][:,:2]) / 2 + 0.5
  print(data["colors"])
# def __circularish(n,size,w_multiplier,z):
#   obj = {
#     "v"  : [],
#     "vt" : [],
#     "vn" : [],
#     "f"  : [],
#     "l"  : [],
#   }

#   for i in range(n):
#     theta = i * 2 * pi / n
#     obj["v"].append( [cos(theta) * size * w_multiplier, sin(theta) * size, z] )

#   for i in range(1,n-1):
#     obj["f"].append( [[0,i,i+1]] )

#   return obj