import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)
def generate(top_mult:  float = 1.0,
             n:         int   = 36, 
             radius:    float = 1.0,
             height:    float = 2.0,
             color:     str   = "position",
             hex = 0xff69ff,
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
  data["vertices"].append([0.0,0.0,-height/2])
  data["vertices"].append([0.0,0.0, height/2])

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
  tools.chooseColoring(color)(data,hex = hex)
  uvTexture(data,height,radius,n)
  tools.dataToNumpyArray(data)
  
  return data

def uvTexture(data,height,radius,n):
  mercatorProjection = tools.uvSlicer(data,[
    # pole to pole
    {"splits":[0,n],"tears":[2*n,2*n+1]},
  ] + [
    # bottom edge
    {"splits":[2*n],"tears":[i,None]} for i in range(n)
  ] + [
    # top edge
    {"splits":[2*n+1],"tears":[i+n,None]} for i in range(n)
  ])
  data["uvs"] = np.full((data["vertices"].shape[0],2),[5,5],dtype=np.float32)
  ratioSide = height/(height+2*radius)
  ratioTop = radius/(height+2*radius)
  
  # middle
  for i in range(1,n):
    data["uvs"][i]   = [i/n,ratioTop]
    data["uvs"][i+n] = [i/n,ratioTop+ratioSide]
    if i < n-1:
      correctSideBottomEdge = tools.getUvSide(data,mercatorProjection,[2*n],[i,i+1])
      data["uvs"][mercatorProjection[2*n][correctSideBottomEdge]] = [(i+0.5)/n,0]
      correctSideTopEdge = tools.getUvSide(data,mercatorProjection,[2*n+1],[i+n,i+n+1])
      data["uvs"][mercatorProjection[2*n+1][correctSideTopEdge]] = [(i+0.5)/n,1]
  # left right 
  leftSide = tools.getUvSide(data,mercatorProjection,[0,n],[1,n+1])
  data["uvs"][mercatorProjection[0][leftSide]] = [0,ratioTop]
  data["uvs"][mercatorProjection[n][leftSide]] = [0,ratioTop+ratioSide]
  rightSide = tools.getUvSide(data,mercatorProjection,[0,n],[n-1,2*n-1])
  data["uvs"][mercatorProjection[0][rightSide]] = [1,ratioTop]
  data["uvs"][mercatorProjection[n][rightSide]] = [1,ratioTop+ratioSide]

  # topright bottomright
  bottomRight = tools.getUvSide(data,mercatorProjection,[2*n+1],[2*n-1,mercatorProjection[n][rightSide]])
  data["uvs"][mercatorProjection[2*n+1][bottomRight]] = [(n-0.5)/n,1]
  topRight = tools.getUvSide(data,mercatorProjection,[2*n],[n-1,mercatorProjection[0][rightSide]])
  data["uvs"][mercatorProjection[2*n][topRight]] = [(n-0.5)/n,0]
  # topleft bottomleft 
  topLeft = tools.getUvSide(data,mercatorProjection,[2*n+1],[n+1,mercatorProjection[n][leftSide]])
  data["uvs"][mercatorProjection[2*n+1][topLeft]] = [0.5/n,1]
  bottomLeft = tools.getUvSide(data,mercatorProjection,[2*n],[1,mercatorProjection[0][leftSide]])
  data["uvs"][mercatorProjection[2*n][bottomLeft]] = [0.5/n,0]