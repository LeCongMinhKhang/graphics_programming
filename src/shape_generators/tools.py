from numpy import pi, sin, cos
import numpy as np
from OpenGL import GL
import logging

logger = logging.getLogger(__name__)

def dataStructure():
  return {
    "vertices": [],          # : np.array((n, 3))
    "indices": [],           # (optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
    "colors": [],            # : np.array((n, 3)) each component must be in [0, 1]
    "normals": [],           # : np.array((n, 3))
    "mode": GL.GL_TRIANGLES  # : GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
  }
def dataToNumpyArray(data):
  if not isinstance(data["vertices"],np.ndarray): data["vertices"] = np.array(data["vertices"], dtype=np.float32)
  if not isinstance(data["indices" ],np.ndarray): data["indices" ] = np.array(data["indices" ], dtype=np.uint32 ) 
  if not isinstance(data["colors"  ],np.ndarray): data["colors"  ] = np.array(data["colors"  ], dtype=np.float32)
  if not isinstance(data["normals" ],np.ndarray): data["normals" ] = np.array(data["normals" ], dtype=np.float32)

def quads2triangles(listOfQuads):
  #      0.----.3
  #       |\   |
  #       | \  |
  #       |  \ |
  #       |   \|
  #      1'----'2
  # quad = [0,1,2,3]
  res = []
  for quad in listOfQuads:
    res.append(quad[0])
    res.append(quad[1])
    res.append(quad[2])
    res.append(quad[0])
    res.append(quad[2])
    res.append(quad[3])
  return res

# n-gon generators #####################################
def star_ngonGenerator(n,size,size_inner,z):
  data = dataStructure()
  
  vertices = np.zeros((2*n,3),dtype=np.float32)
  for i in range(0,2*n,2):
    theta = i * pi / n
    alpha = theta + pi / n
    vertices[  i][0], vertices[  i][1], vertices[  i][2] = cos(theta) * size_inner, sin(theta) * size_inner, z
    vertices[i+1][0], vertices[i+1][1], vertices[i+1][2] = cos(alpha) *       size, sin(alpha) *       size, z
  data["vertices"] = vertices
  
  for i in range(0, 2 * n, 2):
    data["indices"].append(i)
    data["indices"].append(i+1)
    data["indices"].append((i+2)%(2*n))
  for i in range(1,n-1):
    data["indices"].append(0)
    data["indices"].append(2*i%(2*n))
    data["indices"].append(2*(i+1)%(2*n))

  return data

def ngon_ngonGenerator(n,size,w_multiplier,z):
  data = dataStructure()
  vertices = np.zeros((n,3),dtype = np.float32)
  for i in range(n):
    theta = i * 2 * pi / n
    vertices[i][0], vertices[i][1], vertices[i][2] = cos(theta) * size * w_multiplier, sin(theta) * size, z
  data["vertices"] = vertices

  for i in range(1,n-1):
    data["indices"].append(0)
    data["indices"].append(i)
    data["indices"].append(i+1)

  return data

def simple_ngonGenerator(n,size,z):
  res = []
  for i in range(n):
    theta = i * 2 * pi / n
    res.append( [cos(theta) * size , sin(theta) * size, z] )
  return res

# colorings ###################################
def normalColoring(data, **kwargs):
  data["colors"] = data["normals"]/2 + 0.5
  return data

def positionalColoring(data, **kwargs):
  vertices = data["vertices"] if (np.max(data["vertices"], axis=0) - np.min(data["vertices"], axis=0))[2] != 0 else data["vertices"][:, :2]
  data["colors"] = (vertices - np.min(vertices, axis=0)) / (np.max(vertices, axis=0) - np.min(vertices, axis=0))

  return data

def moduloColoring(data, **kwargs):
  data["colors"] = data["vertices"] * 500 % 1000 / 1000
  
def hexColoring(data, hex = 0xff69ff, **kwargs):
  red   = float(((hex & 0xff0000) >> 16)/0xff)
  green = float(((hex & 0x00ff00) >> 8 )/0xff)
  blue  = float(((hex & 0x0000ff) >> 0 )/0xff)
  data["colors"] = np.full_like(data["vertices"],[red,green,blue])
  
def chooseColoring(mode,textureColoring):
  match mode:
    case "position":
      return positionalColoring
    case "normal":
      return normalColoring
    case "modulo":
      return moduloColoring
    case "texture":
      return textureColoring
    case "hex":
      return hexColoring
    case _:
      return positionalColoring
    

# vertex normals ###################################
def vertexNeighborNormals(data):
  normals = np.zeros_like(data["vertices"])
  indices = data["indices"]
  vertices = data["vertices"]
  total = len(indices)
  logger.debug("Starting normals")
  def fastCross(c, d):
    e = np.zeros_like(c)
    e[0] = c[1]*d[2] - c[2]*d[1]
    e[1] = c[2]*d[0] - c[0]*d[2]
    e[2] = c[0]*d[1] - c[1]*d[0]
    return e
  for i in range(0,total,3):
    if i % 10000 == 0: print(f"Doing {i}/{total} normal calculations", end="\r")
    v0,v1,v2 = indices[i  ], indices[i+1], indices[i+2]
    v00, v11 , v22 = vertices[v0], vertices[v1], vertices[v2]
    d0 = v11 - v00
    d1 = v22 - v11
    d2 = v00 - v22

    normals[v0] += fastCross(d0, -d2)
    normals[v1] += fastCross(d1, -d0)
    normals[v2] += fastCross(d2, -d1)
    
  logger.debug("Normalizing normals")
  # don't ask me, my brain is out of steam
  normals = normals / np.linalg.norm(normals, axis=1)[:, np.newaxis]

  data["normals"] = normals