import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(n:           int   = 5, 
             size:        float = 1.0, 
             size_inner:  float = 0.0, 
             z:           float = 0.0, 
             color:       str   = "position",
             hex = 0xff69ff,
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

  tools.chooseColoring(mode=color)(data,hex=hex)
  uvTexture(data)
  tools.dataToNumpyArray(data)
  return data

def uvTexture(data):
  data["uvs"] = data["vertices"][:,:2] / np.max(data["vertices"][:,:2]) / 2 + 0.5