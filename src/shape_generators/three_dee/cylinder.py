import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)
def generate(top_mult:  float = 1.0,
             n:         int   = 36, 
             radius:    float = 1.0,
             height:    float = 1.0,
             color:     str   = "position",
             **kwargs):
  top_mult = float(top_mult)
  n        = int(n)  
  radius   = float(radius)
  height   = float(height)
  color    = str(color)  
  for arg in kwargs.keys():
    logger.debug(f"Unused kwarg: {arg} = {kwargs[arg]}")
  
  if n <= 0:
    n = 36
  if top_mult > 1 or top_mult <= 0:
    top_mult = 0.5
  data = tools.dataStructure()
  data["vertices"] += tools.simple_ngonGenerator(n,radius,-height/2)
  data["vertices"] += tools.simple_ngonGenerator(n,radius*top_mult,height/2)
  data["vertices"].append([0.0,-height/2,0.0])
  data["vertices"].append([0.0,height/2,0.0])

  listOfQuads = []
  for i in range(n):
    listOfQuads.append([(i  )%n,
                        (i+1)%n,
                        (i+1)%n + n,
                        (i  )%n + n])
    data["indices"].append(2*n)
    data["indices"].append((i+1)%n)
    data["indices"].append(i)

    data["indices"].append(2*n+1)
    data["indices"].append(i+n)
    data["indices"].append((i+1)%n+n)

  data["indices"] += tools.quads2triangles(listOfQuads)
  tools.dataToNumpyArray(data)
  
  tools.vertexNeighborNormals(data)
  tools.chooseColoring(color,textureColoring=textureColoring)(data,height = height, radius = radius)
  tools.dataToNumpyArray(data)
  
  return data

def textureColoring(data,height,radius):
  data["colors"] = np.empty((data["vertices"].shape[0],2),dtype=np.float32)
  ratioSide = height/(height+2*radius)
  ratioTop = radius/(height+2*radius)
  
  n = int((data["vertices"].shape[0]-2)/2)
  for i in range(n):
    data["colors"][i]   = [i/n-1,ratioTop+ratioSide]
    data["colors"][i+n] = [i/n-1,ratioTop]
  data["colors"][2*n] = [0.5,1.0]
  data["colors"][2*n+1] = [0.5,0.0]

  # baseNum = data["vertices"].shape[0] - 2
  # for i in range(baseNum):
  #   data["colors"][i] = [i/(baseNum-1),i/(baseNum-1)]
  # data["colors"][baseNum] = [1.0, 0.0]
  # data["colors"][baseNum+1] = [0.0, 1.0]


# def __circularish(n,size,top_mult,z):
#   obj = {
#     "v"  : [],
#     "vt" : [],
#     "vn" : [],
#     "f"  : [],
#     "l"  : [],
#   }

#   for i in range(n):
#     theta = i * 2 * pi / n
#     obj["v"].append( [cos(theta) * size * top_mult, sin(theta) * size * top_mult,  z/2] )
#     obj["v"].append( [cos(theta) * size, sin(theta) * size, -z/2] )

#   for i in range(1,n-1):
#     obj["f"].append( [[     0,         2*i, 2*(i+1)]] )
#     obj["f"].append( [[ 1 + 0, 1 + 2*(i+1), 1 + 2*i]] )

#   return obj