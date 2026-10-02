from numpy import pi, sin, cos
import numpy as np
from OpenGL import GL

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

def uvSphere_torus_ngonGenerator(n,size,z):
  res = []
  for i in range(n):
    theta = i * 2 * pi / n
    res.append( [cos(theta) * size , sin(theta) * size, z] )
  return res

def ngonPiramid_ngonGenerator(n,size,z):
  data = dataStructure()
  for i in range(n):
    theta = i * 2 * pi / n
    data["vertices"].append( [cos(theta) * size, sin(theta) * size, z] )

  for i in range(1,n-1):
    data["indices"].append(0,i,i+1)

  return data

def normalColoring(data):
  data["colors"] = data["normals"]/2 + 0.5
  return data

def positionalColoring(data):
  data["colors"] = data["vertices"] / np.max(data["vertices"]) / 2 + 0.5 
  return data

def moduloColoring(data):
  data["colors"] = data["vertices"] * 500 % 1000 / 1000
  
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
    case _:
      return positionalColoring