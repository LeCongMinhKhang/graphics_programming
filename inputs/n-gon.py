from numpy import pi, cos, sin

def generate(shape_type = "pentagon"|"hexagon"|"circle"|"ellipse",size = 1.0, size_wide = 1.0, z = 0.0):
  n = 3
  w_multiplier = 1
  if size <= 0:
    print("Warning: invalid size 0")
    size = 0.001

  match(shape_type):
    case "pentagon": n = 5
    case "hexagon":  n = 6
    case "circle":   n = 60
    case "ellipse":  
      n = 60
      w_multiplier = size_wide/size
    case _: n = 3

  return __circularish(n,size,w_multiplier,z)

def __circularish(n,size,w_multiplier,z):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }

  for i in range(n):
    theta = i * 2 * pi / n
    obj["v"].append( [cos(theta) * size * w_multiplier, sin(theta) * size, z] )

  for i in range(1,n-1):
    obj["f"].append( [[0,i,i+1]] )

  return obj