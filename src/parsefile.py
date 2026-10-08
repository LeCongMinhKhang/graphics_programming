from OpenGL import GL
import numpy as np
from src.shape_generators import tools


def parseFile(path):
  obj = {
    "v":[],
    "vt":[],
    "vn":[],
    "f":[],
  }
  data = tools.dataStructure()

  verticesCount = 0
  tripletHashmap = {}

  with open(path) as file:
    vNone  = [None for i in obj["v" ][0]] if len (obj["v" ]) > 0 else None 
    vtNone = [None for i in obj["vt"][0]] if len (obj["vt"]) > 0 else None 
    vnNone = [None for i in obj["vn"][0]] if len (obj["vn"]) > 0 else None 
    for line in file:
      string = line.rstrip()
      arr = string.split(" ")
      match arr[0]:
        case "v":
          obj["v"].append([float(i) for i in arr[1:]])
          if vNone is None:
            vNone  = [None for i in obj["v" ][0]] if len (obj["v" ]) > 0 else None 
        case "vt":
          obj["vt"].append([float(i) for i in arr[1:]])
          if vtNone is None:
            vtNone = [None for i in obj["vt"][0]] if len (obj["vt"]) > 0 else None 
        case "vn":
          obj["vn"].append([float(i) for i in arr[1:]])
          if vnNone is None:
            vnNone = [None for i in obj["vn"][0]] if len (obj["vn"]) > 0 else None 
        case "f":
          keys = arr[1:]
          newKeys = [keys[0],keys[1],keys[2]]
          for i in range(3,len(keys)):
            newKeys.append(keys[0])
            newKeys.append(keys[i-1])
            newKeys.append(keys[i])
          keys = newKeys
          parsed = [[int(v)-1 if v is not None else None for v in i.split("/")] for i in keys]
          for i in range(len(keys)):
            verticesIndex = tripletHashmap.get(keys[i], None)

            if verticesIndex is None:
              data["vertices"].append(obj["v" ][parsed[i][0]] if parsed[i][0] is not None else vNone)
              data["uvs"     ].append(obj["vt"][parsed[i][1]]) if len(parsed[i]) > 1 and parsed[i][1] is not None else None
              data["normals" ].append(obj["vn"][parsed[i][2]]) if len(parsed[i]) > 2 and parsed[i][2] is not None else None

              tripletHashmap[keys[i]] = verticesCount
              verticesIndex = verticesCount
              verticesCount += 1

            data["indices"].append(verticesIndex)
        # case "l":
        #   parsed = _parseLineStrip(arr)
        #   if parsed is not None and parsed:
        #     obj["l"].append(parsed)
        case "#":
          continue
        case _:
          continue
  tools.dataToNumpyArray(data)
  tools.vertexNeighborNormals(data) if data["normals"].size == 0 else None
  # temp override default texture mapping of colors      vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
  tools.normalColoring(data) if data["colors"].size == 0 or data["colors"].shape[1] != 3 else None
  tools.dataToNumpyArray(data)
  return data

def _parseFace(arr):
  if len(arr) == 4:
    arrarr = (
    )
    return arrarr
  else:
    return None


# def _parseLineStrip(arr):
#   if len(arr) > 2:
#     arrarr = list(map(lambda e: int(e), arr[1:]))
#     return arrarr
#   else:
#     return None


# def objToPipelineable(obj):
#   res = {
#     # "vertices": [],                # : np.array((n, 3))
#     # "indices": [],                 # (optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
#     # "colors": [],                  # : np.array((n, 3)) each component must be in [0, 1]
#     # "normals": [],                 # : np.array((n, 3))
#     "mode": GL.GL_TRIANGLES  # : GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
#   }
#   # List comprehension is my passion
#   res["vertices"] = np.array(obj["v"], dtype=np.float32) if obj["v"] is not None else []
#   res["indices"] = (
#     np.array([f[0][i] for f in obj["f"] for i in range(3) ], dtype=np.uint32)
#     if obj["f"] is not None
#     else []
#   )
#   res["colors"] = (
#     np.array([[(v[0]*500)%1000/1000,(v[1]*500)%1000/1000,(v[2]*500)%1000/1000] for v in obj["v"]], dtype=np.float32)
#     if obj["v"] is not None
#     else []
#   )
#   res["normals"] = (
#     np.array([[0, 0, 0] for v in obj["v"]], dtype=np.float32) if obj["v"] is not None else []
#   )

#   return res


def objToFile(obj,filename = "object.obj"):
  with open(filename, "w", encoding="utf-8") as file :
    file.writelines(
      [f"v {v[0]} {v[1]} {v[2]}\n" for v in obj["v"]]
    )
    file.writelines(
      [f"f {f[0][0]+1} {f[0][1]+1} {f[0][2]+1}\n" for f in obj["f"]]
    )
