from OpenGL import GL
import numpy as np

def parseFile(path):
  obj = {}
  obj["v"] = []
  obj["f"] = []
  obj["l"] = []
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
          if not parsed is None and not parsed:
            obj["f"].append(parsed)
        case "l":
          parsed = _parseLineStrip(arr)
          if not parsed is None and not parsed:
            obj["l"].append(parsed)
        case "#":
          continue

        case _:
          print(f"Parsed unknown: '{string}'")

  return obj

def _parseVertex(arr):
  match len(arr):
    case 4:
      return [ float(arr[1]), float(arr[2]), float(arr[3]) ]
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


def _parseLineStrip(arr):
  if len(arr) > 2:
    arrarr = list(map(
      lambda e: int(e)
      ,arr[1:]))
    return arrarr
  else:
    print(f"Parsed line with unknown length: {len(arr)}")
    return None
  

def objToPipelineable(obj):
  res = {
    # "vertices": [],                # : np.array((n, 3))
    # "indices": [],                 # (optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
    # "colors": [],                  # : np.array((n, 3)) each component must be in [0, 1]
    # "normals": [],                 # : np.array((n, 3))
    "mode": GL.GL_TRIANGLES        # : GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
  }
  # List comprehension is my passion
  res["vertices"] = np.array(obj["v"], dtype=np.float32) if obj["v"] is not None else []
  res["indices"]  = np.array([f[0][i] for i in range(3) for f in obj["f"]], dtype=np.float32) if obj["f"] is not None else []
  res["colors"]   = np.array([np.random.default_rng(seed=42).random(size=3) for v in obj["v"]], dtype=np.float32) if obj["v"] is not None else []
  res["normals"]  = np.array([[0,0,0] for v in obj["v"]], dtype=np.float32) if obj["v"] is not None else []

  return res