import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(func = lambda x,y: 0, 
             limx:        int  = 25,
             limy:        int  = 25, 
             n:           int  = 5, 
             color:       str  = "normal", 
             hex = 0xff69ff,
             calcNormals: bool = True,**kwargs):
  limx        = int(limx) 
  limy        = int(limy) 
  n           = int(n) 
  color       = str(color) 
  calcNormals = bool(calcNormals)
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")
  data = tools.dataStructure()

  # uhoh
  logger.debug("Initializing vertices")
  vertices = np.zeros(((2**n * 2*limx + 1) * (2**n * 2*limy + 1),3),dtype=np.float32)
  index = lambda x,y: (((y+limy) % (2*limy * 2**n + 1))) * (2*limx * 2**n + 1) + (x+limx) % (2*limx * 2**n + 1)

  logger.debug("Started generating vertices")
  for yi in range(-limy * 2**n,limy * 2**n + 1):
    for xi in range(-limx * 2**n,limx * 2**n + 1):
      vertices[index(xi,yi)][0], vertices[index(xi,yi)][1], vertices[index(xi,yi)][2] = xi/int(2**n), yi/int(2**n), func(xi/int(2**n),yi/int(2**n))
  
  logger.debug("Assigning vertices")
  data["vertices"] = vertices
  
  logger.debug("Quadding")
  listOfQuads = []
  for yi in range(-limy * 2**n,limy * 2**n):
    for xi in range(-limx * 2**n,limx * 2**n):
      listOfQuads.append([index(xi,yi),index(xi+1,yi),index(xi+1,yi+1),index(xi,yi+1)])
  
  logger.debug("Assigning indices")
  data["indices"] = tools.quads2triangles(listOfQuads) 

  logger.debug("Making normals")
  if calcNormals: tools.vertexNeighborNormals(data)
  else: data["normals"] = np.full_like(data["vertices"],fill_value=[1.0,105/255,1.0])
  
  logger.debug("Picking Colors")
  tools.chooseColoring(color)(data, hex = hex)
  
  logger.debug("Standardizing data type")
  uvTexture(data, limx=limx,limy=limy,n=n)
  tools.dataToNumpyArray(data)
  return data

def uvTexture(data, limx, limy, n):
  index = lambda x,y: (((y+limy) % (2*limy * 2**n + 1))) * (2*limx * 2**n + 1) + (x+limx) % (2*limx * 2**n + 1)
  uvs = np.full(((2*limy * 2**n + 1) * (2*limx * 2**n + 1),2),[0,0],dtype=np.float32)
  for yi in range(-limy * 2**n,limy * 2**n + 1):
    for xi in range(-limx * 2**n,limx * 2**n + 1):
      uvs[index(xi,yi)] = [(xi/int(2**n)/2+limx)/limx,(yi/int(2**n)/2+limy)/limy]
  
  data["uvs"] = uvs