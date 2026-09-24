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
      arr = string.split(" ")
      match arr[0]:
        case "v":
          parsed = _parseVertex(arr)
          if not parsed is None:
            obj["v"].append(parsed)
        case "f":
          parsed = _parseFace(arr)
          if parsed is not None and parsed:
            obj["f"].append(parsed)
        case "l":
          parsed = _parseLineStrip(arr)
          if parsed is not None and parsed:
            obj["l"].append(parsed)
        case "#":
          continue
        case _:
          continue
  return obj


def _parseVertex(arr):
  match len(arr):
    case 4:
      return [float(arr[1]), float(arr[2]), float(arr[3])]
    case 5:
      return [float(arr[1]), float(arr[2]), float(arr[3]), float(arr[4])]

    case _:
      return None


def _parseFace(arr):
  if len(arr) == 4:
    arrarr = (
      [[int(f[0])-1 for f in [e.split("/") for e in arr[1:]]]]
    )
    return arrarr
  else:
    return None


def _parseLineStrip(arr):
  if len(arr) > 2:
    arrarr = list(map(lambda e: int(e), arr[1:]))
    return arrarr
  else:
    return None


def objToPipelineable(obj):
  res = {
    # "vertices": [],                # : np.array((n, 3))
    # "indices": [],                 # (optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
    # "colors": [],                  # : np.array((n, 3)) each component must be in [0, 1]
    # "normals": [],                 # : np.array((n, 3))
    "mode": GL.GL_TRIANGLES  # : GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
  }
  # List comprehension is my passion
  res["vertices"] = np.array(obj["v"], dtype=np.float32) if obj["v"] is not None else []
  res["indices"] = (
    np.array([f[0][i] for f in obj["f"] for i in range(3) ], dtype=np.uint32)
    if obj["f"] is not None
    else []
  )
  res["colors"] = (
    np.array([[(v[0]*500)%1000/1000,(v[1]*500)%1000/1000,(v[2]*500)%1000/1000] for v in obj["v"]], dtype=np.float32)
    if obj["v"] is not None
    else []
  )
  res["normals"] = (
    np.array([[0, 0, 0] for v in obj["v"]], dtype=np.float32) if obj["v"] is not None else []
  )

  return res
