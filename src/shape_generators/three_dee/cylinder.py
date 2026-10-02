from ._quad_triangulator import triangulationNation
from numpy import pi, cos, sin

def generate(top_mult = 1.0,n = 36,radius = 1.0,height = 1.0):
  if n <= 0:
    n = 36
  if top_mult > 1 or top_mult <= 0:
    top_mult = 0.5
  
  obj = __circularish(n,radius,top_mult,height)

  listOfQuads = []
  for i in range(0,2*n,2):
    listOfQuads.append([(i+0)%(2*n),(i+1)%(2*n),(i+3)%(2*n),(i+2)%(2*n)])

  obj["f"] = obj["f"] + triangulationNation(listOfQuads) 

  return obj


def __circularish(n,size,top_mult,z):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }

  for i in range(n):
    theta = i * 2 * pi / n
    obj["v"].append( [cos(theta) * size * top_mult, sin(theta) * size * top_mult,  z/2] )
    obj["v"].append( [cos(theta) * size, sin(theta) * size, -z/2] )

  for i in range(1,n-1):
    obj["f"].append( [[     0,         2*i, 2*(i+1)]] )
    obj["f"].append( [[ 1 + 0, 1 + 2*(i+1), 1 + 2*i]] )

  return obj