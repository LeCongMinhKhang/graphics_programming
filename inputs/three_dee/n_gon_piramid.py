from numpy import pi, cos, sin, sqrt

def generate(type = "cone",base = 1.0, height = 1.0):
  n = 36

  if base <= 0:
    print("Warning: invalid size 0")
    base = 0.001
  if height <= 0:
    print("Warning: invalid size 0")
    height = 0.001

  if type == "tetrahedron":
    n = 3
    edge_length = base * sqrt(3)
    height =  edge_length * sqrt(6)/3
  else:
    n = 36

  obj = __circularish(n,base,-height/2)

  top_index = len(obj["v"])
  obj["v"].append([0,0,height/2])

  for i in range(top_index):
    obj["f"].append([[top_index,i,(i+1)%top_index]])

  return obj

def __circularish(n,size,z):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  for i in range(n):
    theta = i * 2 * pi / n
    obj["v"].append( [cos(theta) * size, sin(theta) * size, z] )

  for i in range(1,n-1):
    obj["f"].append( [[0,i,i+1]] )

  return obj