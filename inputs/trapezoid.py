def generate(width_1,width_2,height,offset, z = 0.0):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  #           0.----.3
  #           / \   |
  #          /   \  |
  #         /     \ |
  #        /       \|
  #      1'---------'2
  obj["v"].append([ - offset/2 - width_1/2, - height/2, z ])
  obj["v"].append([ - offset/2 - width_2/2,   height/2, z ])
  obj["v"].append([   offset/2 + width_1/2,   height/2, z ])
  obj["v"].append([   offset/2 + width_2/2, - height/2, z ])

  obj["f"].append([[0,1,2]])
  obj["f"].append([[0,2,3]])

  return obj
