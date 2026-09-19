from numpy import pi, cos, sin

def generate(n = 5, size = 1.0, size_inner = 0.0, z = 0.0):
  if n < 2:
    n = 2
  if size_inner <= 0:
    size_inner = 0.5 * size
  if size_inner >= 1:
    size_inner = 0.999

  return __circularish(n,size,size*size_inner,z)

def __circularish(n,size,size_inner,z):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }

  for i in range(n):
    theta = i * 2 * pi / n
    alpha = theta + pi / n
    obj["v"].append( [cos(theta) * size_inner, sin(theta) * size_inner, z] )
    obj["v"].append( [      cos(alpha) * size,       sin(alpha) * size, z] )

  for i in range(0, 2 * n, 2):
    obj["f"].append( [[i,i+1,(i+2)%(2*n)]] )
  # please verify that these generates actual triangles
  for i in range(1,n-1):
    obj["f"].append( [[0,2*i%(2*n),2*(i+1)%(2*n)]] )

  return obj