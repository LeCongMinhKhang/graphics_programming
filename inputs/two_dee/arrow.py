def generate(length = 1.0,girth = 1.0, z = 0.0):
  if length <= girth/2:
    length = girth/2
    
  shaft_length = length - girth/2

  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  #           0.
  #           / \
  #          /   \
  #         /     \
  #        /       \
  #      1'--•---•--'2
  #         3|\  |6
  #          | \ |
  #          |  \|
  #         4'---'5  
  
  obj["v"].append([         0, - girth/2, z ])
  obj["v"].append([ - girth/2,         0, z ])
  obj["v"].append([   girth/2,         0, z ])

  if shaft_length > 0:
    obj["v"].append([ - girth/3,            0, z ])
    obj["v"].append([ - girth/3, shaft_length, z ])
    obj["v"].append([   girth/3, shaft_length, z ])
    obj["v"].append([   girth/3,            0, z ])

    obj["f"].append([[0,1,3]])
    obj["f"].append([[0,3,6]])
    obj["f"].append([[0,6,2]])
    obj["f"].append([[3,4,5]])
    obj["f"].append([[3,5,6]])
  else:
    obj["f"].append([[0,1,2]])

  return obj