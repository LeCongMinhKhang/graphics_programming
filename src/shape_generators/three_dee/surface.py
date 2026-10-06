import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)

def generate(func = lambda x,y: 0, 
             limx:        int  = 25,
             limy:        int  = 25, 
             n:           int  = 5, 
             color:       str  = "normal", 
             calcNormals: bool = False,**kwargs):
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
  tools.chooseColoring(color,textureColoring=textureColoring)(data,totalx=2**n * 2*limx + 1,totaly=2**n * 2*limy + 1)
  
  logger.debug("Standardizing data type")
  tools.dataToNumpyArray(data)
  return data

def textureColoring(data, totalx, totaly):
  colors = np.empty((totalx * totaly,2),dtype=np.float32)
  for j in range(totaly):
    for i in range(totalx):
      colors[j*totalx + i][0], colors[j*totalx + i][1] = i/(totalx-1), 1.0 - j/(totaly-1)
  data["colors"] = colors