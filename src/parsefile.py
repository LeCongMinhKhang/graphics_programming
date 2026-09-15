
def parseFile(path):
  obj = {}
  obj["v"] = []
  obj["f"] = []
  with open(path) as file:
    for line in file:
      string = line.rstrip()
      print(f"Parsed line: {string}")
      arr = string.split(" ")
      match arr[0]:
        case "v":
          parsed = _parseVertex(arr)
          if not parsed is None:
            obj["v"].append(parsed)
        case "f":
          parsed = _parseFace(arr)
          if not parsed is None and not parsed == []:
            obj["f"].append(parsed)
        case "#":
          continue

        case _:
          print(f"Parsed unknown: '{string}'")

  return obj

def _parseVertex(arr):
  match len(arr):
    case 4:
      return [ float(arr[1]), float(arr[2]), float(arr[3]), None ]
    case 5:
      return [ float(arr[1]), float(arr[2]), float(arr[3]), float(arr[4]) ]

    case _:
      print(f"Parsed vertex with unknown length: {len(arr)}")
      return None

def _parseFace(arr):
  if len(arr) == 4:
    arrarr = list(map(
      lambda e: 
        list(map(
          lambda f: 
            None if f == '' else int(f)
          ,e.split('/')))
      ,arr[1:]))
    return arrarr
  else:
    print(f"Parsed vertex with unknown length: {len(arr)}")
    return None
  # Horrible, please rewrite
  # if len(arr) == 4:
  #   arrarr = []
  #   res = []
  #   for e in arr[1:4]:
  #     splitted = e.split("/")
  #     arrarr.append(list(map(lambda a: None if a == '' else int(a) ,splitted[1:len(splitted)-1])))

  #   for e in range(len(arrarr[0])):
  #     resres = []
  #     for f in arrarr:
  #       resres.append(f[e])
  #     res.append(resres)
  
  #   return res 
  # else:
  #   print(f"Parsed vertex with unknown length: {len(arr)}")
  #   return None