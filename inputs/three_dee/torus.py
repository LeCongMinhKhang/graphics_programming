from numpy import pi, cos, sin
from ._quad_triangulator import triangulationNation

def generate(thickness = 1.0, hole_size = 1.0, n = 3):

  if thickness <= 0:
    thickness = 0.001
  if hole_size <= 0:
    hole_size = 0.001
  # n is the magical density number whatever the hell
  if n < 3:
    n = 3

  ringCount = 2*n
    
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  
  tempRing = __circularish(n,thickness,0)
  centerOffset = thickness + hole_size
  for ring in tempRing:
    obj["v"] = obj["v"] + __circularish(ringCount,centerOffset - ring[0],ring[1])
  
  index = lambda i,j: (i % n) * ringCount + j % ringCount

  listOfQuads = []
  for i in range(n+1):
    for j in range(ringCount+1):
      listOfQuads.append([index(i+1,j),index(i+1,j+1),index(i,j+1),index(i,j)])
  obj["f"] = triangulationNation(listOfQuads)
  return obj


def __circularish(n,size,z):
  res = []
  for i in range(n):
    theta = i * 2 * pi / n
    res.append( [cos(theta) * size , sin(theta) * size, z] )
  return res