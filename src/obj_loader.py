from OpenGL import GL
import numpy as np
import os
from pathlib import Path
from src.shape_generators import tools

import logging

logger = logging.getLogger(__name__)


def parseMaterials(path):
  materials = {}
  currentMat = None
  file_path = Path(path)
  if file_path.exists():
    file = file_path.read_text()
    for line in file.split("\n"):
      string = line.strip()
      arr = string.split(" ")
      match arr[0]:
        case "newmtl":
          materials[arr[1]] = [1, 1, 1]
          currentMat = arr[1]
        case "Kd":
          materials[currentMat] = [arr[1], arr[2], arr[3]]
  return materials


def resolve(idx, n):
  """OBJ index
  positive: index starts at
  negative: relative position
  empty: None"""
  if not idx:
    return None
  i = int(idx)
  if i < 0:
    print("aaaaa")
  return i - 1 if i > 0 else n + i


def parseFile(path):
  obj = {
    "v": [],
    "vt": [],
    "vn": [],
    "f": [],
  }
  logger.debug('parsing "%s" file', path)

  data = tools.dataStructure()

  verticesCount = 0
  hasUv = True
  hasNormal = True
  tripletHashmap = {}

  file_path = Path(path)
  if file_path.exists():
    file = file_path.read_text()
    vNone = [None for i in obj["v"][0]] if len(obj["v"]) > 0 else None
    vtNone = [None for i in obj["vt"][0]] if len(obj["vt"]) > 0 else None
    vnNone = [None for i in obj["vn"][0]] if len(obj["vn"]) > 0 else None
    materials = {}
    currentMat = None
    for line in file.split("\n"):
      string = " ".join(line.strip().split())
      arr = string.split(" ")
      match arr[0]:
        case "mtllib":
          matFile = " ".join(line.strip().split(" ")[1:])
          materials = parseMaterials(os.path.dirname(path) + f"/{matFile}")
        case "usemtl":
          currentMat = arr[1]
        case "v":
          obj["v"].append([float(i) for i in arr[1:]])
          if vNone is None:
            vNone = [None for i in obj["v"][0]] if len(obj["v"]) > 0 else None
        case "vt":
          obj["vt"].append([float(i) for i in arr[1:3]])
          if vtNone is None:
            vtNone = [None for i in obj["vt"][0]] if len(obj["vt"]) > 0 else None
        case "vn":
          obj["vn"].append([float(i) for i in arr[1:]])
          if vnNone is None:
            vnNone = [None for i in obj["vn"][0]] if len(obj["vn"]) > 0 else None
        case "f":
          keys = arr[1:]
          if len(keys) < 3:
            continue
          newKeys = [keys[0], keys[1], keys[2]]
          for i in range(3, len(keys)):
            newKeys += [keys[0], keys[i - 1], keys[i]]
          for key in newKeys:
            # resolve relative indices now, so the hashmap key is unambiguous
            parts = (key.split("/") + ["", ""])[:3]
            vi = resolve(parts[0], len(obj["v"]))
            ti = resolve(parts[1], len(obj["vt"]))
            ni = resolve(parts[2], len(obj["vn"]))
            cacheKey = (vi, ti, ni, currentMat)

            index = tripletHashmap.get(cacheKey)
            if index is None:
              data["vertices"].append(obj["v"][vi])
              data["colors"].append(materials.get(currentMat, [1.0, 1.0, 1.0]))

              # always append something, so all arrays stay the same length
              if ti is None:
                data["uvs"].append([0.0, 0.0])
                hasUv = False
              else:
                data["uvs"].append(obj["vt"][ti])

              if ni is None:
                data["normals"].append([0.0, 0.0, 0.0])
                hasNormal = False
              else:
                data["normals"].append(obj["vn"][ni])

              index = tripletHashmap[cacheKey] = verticesCount
              verticesCount += 1

            data["indices"].append(index)
        case "#":
          continue
        case _:
          continue

  # partial UVs/normals are unusable
  if not hasUv:
    data["uvs"] = []
  if not hasNormal:
    data["normals"] = []
  logger.debug("parsing finished")

  tools.dataToNumpyArray(data)
  tools.vertexNeighborNormals(data) if data["normals"].size == 0 else None
  # temp override default texture mapping of colors            vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
  # tools.normalColoring(data) if data["colors"] is None == 0 or data["colors"].shape[
  #   1
  # ] != 3 else None
  tools.dataToNumpyArray(data)
  return data


def _parseFace(arr):
  if len(arr) == 4:
    arrarr = ()
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


def objToFile(obj, filename="object.obj"):
  with open(filename, "w", encoding="utf-8") as file:
    file.writelines([f"v {v[0]} {v[1]} {v[2]}\n" for v in obj["v"]])
    file.writelines([f"f {f[0][0] + 1} {f[0][1] + 1} {f[0][2] + 1}\n" for f in obj["f"]])
