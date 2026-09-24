from numpy import sqrt

def generate(size = 1.0, z = 0.0):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  # With the center of the triangle at 0,0,z
  height = size * sqrt(3) / 2
  obj["v"].append([      0.0, 2*height/3, z ])
  obj["v"].append([ - size/2, - height/3, z ])
  obj["v"].append([   size/2, - height/3, z ])

  obj["f"].append([[0,1,2]])

  return obj
