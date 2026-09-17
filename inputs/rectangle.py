def generate(width,height, z = 0.0):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  #      0.----.3
  #       |\   |
  #       | \  |
  #       |  \ |
  #       |   \|
  #      1'----'2
  obj["v"].append([ - width/2, - height/2, z ])
  obj["v"].append([ - width/2,   height/2, z ])
  obj["v"].append([   width/2,   height/2, z ])
  obj["v"].append([   width/2, - height/2, z ])

  obj["f"].append([[0,1,2]])
  obj["f"].append([[0,2,3]])

  return obj
