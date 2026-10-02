from ._quad_triangulator import triangulationNation

def generate(size = 1.0):
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }
  p = size/2
  obj["v"].append([ -p ,  p ,  p])
  obj["v"].append([ -p ,  p , -p])
  obj["v"].append([ -p , -p ,  p])
  obj["v"].append([ -p , -p , -p])
  obj["v"].append([  p , -p ,  p])
  obj["v"].append([  p , -p , -p])
  obj["v"].append([  p ,  p ,  p])
  obj["v"].append([  p ,  p , -p])

  listOfQuads = []
  # top
  listOfQuads.append([0,2,4,6])
  # bottom
  listOfQuads.append([7,5,3,1])

  for i in range(0,8,2):
    listOfQuads.append([(i+0)%8,(i+1)%8,(i+3)%8,(i+2)%8])

  obj["f"] = triangulationNation(listOfQuads)

  return obj