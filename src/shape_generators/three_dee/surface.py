from ._quad_triangulator import triangulationNation
def generate(func = lambda x,y: 0, limx = 5,limy = 5, n = 0): 
  obj = {
    "v"  : [],
    "vt" : [],
    "vn" : [],
    "f"  : [],
    "l"  : [],
  }

  for yi in range(-limy*int(2**n),(limy*int(2**n))+1):
    for xi in range(-limx*int(2**n),(limx*int(2**n))+1):
      obj["v"].append([xi/int(2**n),yi/int(2**n),func(xi/int(2**n),yi/int(2**n))])

  index = lambda x,y: (y + limy*int(2**n)) * (2*limx*int(2**n) + 1) + x + limx*int(2**n)

  listOfQuads = []
  for yi in range(-limy*int(2**n),limy*int(2**n)):
    for xi in range(-limx*int(2**n),limx*int(2**n)):
      listOfQuads.append([index(xi,yi),index(xi+1,yi),index(xi+1,yi+1),index(xi,yi+1)])
  obj["f"] = triangulationNation(listOfQuads) 
  
  return obj