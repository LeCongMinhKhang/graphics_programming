from numpy import pi, cos, sin
from ._quad_triangulator import triangulationNation

def generate(size = 1.0, n = 3):
  if size <= 0:
    size = 0.001
  # n is the magical density number whatever the hell
  if n < 1:
    n = 1
    
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }

  listOfLatitudes = []
  for i in range(1,n+1):
    listOfLatitudes.append( i * pi / (n + 1))

  numOfVertPerLatRing = 2 * (n+1)
  for theta in listOfLatitudes:
    obj["v"] = obj["v"] + __circularish(
        numOfVertPerLatRing, 
        sin(theta)*size,  # the radius of the lat ring
        - cos(theta)*size # z height of the lat ring
        )
  
  index = lambda i,j: i * numOfVertPerLatRing + j % numOfVertPerLatRing

  listOfQuads = []
  for i in range(n-1):
    for j in range(numOfVertPerLatRing):
      listOfQuads.append([index(i,j),index(i,j+1),index(i+1,j+1),index(i+1,j)])
  obj["f"] = triangulationNation(listOfQuads)

  # the poles
  poleIndex = numOfVertPerLatRing * n
  obj["v"].append([0,0, - size])
  obj["v"].append([0,0,   size])

  # triangle fan the long way around
  for i in range (numOfVertPerLatRing):
    obj["f"].append([[
      poleIndex,
      (i+1) % numOfVertPerLatRing,
      i
    ]])
    obj["f"].append([[
      poleIndex + 1,
      poleIndex - 1 - (i+1) % numOfVertPerLatRing,
      poleIndex - 1 - i
    ]])

  return obj


def __circularish(n,size,z):
  res = []
  for i in range(n):
    theta = i * 2 * pi / n
    res.append( [cos(theta) * size , sin(theta) * size, z] )
  return res