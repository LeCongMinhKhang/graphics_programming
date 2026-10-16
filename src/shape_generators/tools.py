from numpy import pi, sin, cos
import numpy as np
from OpenGL import GL
import logging

logger = logging.getLogger(__name__)


def dataStructure():
  return {
    "vertices": [],  # : np.array((n, 3))
    "indices": [],  # (optional): np.array((n)) if ommited, will be picking k-tuples from the vertices array where k is the size of primitive (eg 3 for triangles)
    "uvs": [],
    "colors": [],  # : np.array((n, 3)) each component must be in [0, 1]
    "normals": [],  # : np.array((n, 3))
    "mode": GL.GL_TRIANGLES,  # : GL mode, indicating the rendering mode (eg: GL\_TRIANGLES, GL\_TRIANGL_STRIP, ...)
  }


def dataToNumpyArray(data):
  if not isinstance(data["vertices"], np.ndarray):
    data["vertices"] = np.array(data["vertices"], dtype=np.float32)
  if not isinstance(data["indices"], np.ndarray):
    data["indices"] = np.array(data["indices"], dtype=np.uint32)
  if not isinstance(data["uvs"], np.ndarray):
    data["uvs"] = np.array(data["uvs"], dtype=np.float32) if data["uvs"] else None
  if not isinstance(data["colors"], np.ndarray):
    data["colors"] = np.array(data["colors"], dtype=np.float32) if data["colors"] else None
  if not isinstance(data["normals"], np.ndarray):
    data["normals"] = np.array(data["normals"], dtype=np.float32)


def quads2triangles(listOfQuads):
  #      0.----.3
  #       |\   |
  #       | \  |
  #       |  \ |
  #       |   \|
  #      1'----'2
  # quad = [0,1,2,3]
  res = []
  for quad in listOfQuads:
    res.append(quad[0])
    res.append(quad[1])
    res.append(quad[2])
    res.append(quad[0])
    res.append(quad[2])
    res.append(quad[3])
  return res
# UV-Slicer ############################################
def uvSlicer(data,seams=[],debug = False):
  # there are a few groups of vertices with specific relation to the seam vertices
  # + add1 = vertices that connects to 2 of the seam's to form a face (unknown which side it is)
  # + add2 = when 1 seam vertex connects to 2 non seam vertices to form a face (unknown which side it is)
  # there is potential to have it be that a "side" of a seam is determined by a set of add1s and add2s that shares an non seam vertices
  isTheSame = {}
  plannedRedirection = {}
  indices   = data["indices" ].tolist() if isinstance(data["indices" ],np.ndarray) else data["indices" ]
  vertices  = data["vertices"].tolist() if isinstance(data["vertices"],np.ndarray) else data["vertices"]
  normals   = data["normals" ].tolist() if isinstance(data["normals" ],np.ndarray) else data["normals" ]
  colors    = data["colors"  ].tolist() if isinstance(data["colors"  ],np.ndarray) else data["colors"  ]
  
  def addToIsTheSame(dic):
    nonlocal isTheSame
    for key, value in dic.items():
      if key in isTheSame:
        isTheSame[key].add(value)
      else:
        flag = True
        for s in isTheSame.values():
          if key in s:
            flag = False
            s.add(value)
        if flag:
          isTheSame[key] = {value,}
  def expandToIncludeTheSame(listOfIndices):
    nonlocal isTheSame
    res = []
    for index in listOfIndices:
      res.append(index)
      if index in isTheSame:
        res += [i for i in isTheSame[index] if i != index]
    return res
  def assignSideToFaces(facesI):
    nonlocal indices, groups, fullSeam, seam2
    for i in facesI:
      triangle = indices[i:i+3]
      if groups == []:
        newNonSeam = list(filter(lambda e: e not in fullSeam,triangle))
        groups.append({"v": newNonSeam,"f": {i,}})
      else:
        isPartOf=[]
        newNonSeam = list(filter(lambda e: e not in fullSeam,triangle))
        match len(newNonSeam):
          case 3: None
          case 2: 
            for g in range(len(groups)):
              if len(list(filter(lambda e: e not in groups[g]["v"],triangle))) < 3:
                isPartOf.append(g)
          case 0 | 1:
            newMaybeSeamEdge = [{triangle[i],triangle[(i+1)%3]} for i in range(len(triangle)) if triangle[i] not in newNonSeam and triangle[(i+1)%3] not in newNonSeam]
            newNonSeamEdge = [e for e in newMaybeSeamEdge if e not in seam2]
            # print(newNonSeamEdge,) if newNonSeamEdge != [] else None
            newNonSeam += newNonSeamEdge
            # if len(newNonSeam)== 0:
              # print("Lost",newNonSeamEdge)
            for g in range(len(groups)):
              if len(list(filter(lambda e: e not in groups[g]["v"],triangle))) < len(triangle)\
              or len(list(filter(lambda e: e not in groups[g]["v"],newNonSeamEdge))) < len(newNonSeamEdge):
                # print("found",newNonSeamEdge)
                isPartOf.append(g)

        
        if isPartOf == []:
          groups.append({"v": newNonSeam,"f": {i,}})
        else:
          goTo = isPartOf[0]
          other = isPartOf[1:]
          [groups[goTo]["v"].append(v) if v not in fullSeam and v not in groups[goTo]["v"] else None for v in triangle ]
          groups[goTo]["f"].add(i)

          [[groups[goTo]["v"].append(v) if v not in groups[goTo]["v"] else None for v in groups[o]["v"]] for o in other ]
          [[groups[goTo]["f"].add(f) for f in groups[o]["f"]] for o in other ]
          for o in other: groups[o]["v"] = {}
          groups = [g for g in groups if len(g["v"])>0]
        
        # [print(g["v"]) for g in groups]
    # [print(g["f"]) for g in groups]
    
  def makeFaceVerticesCopy(nl,mun,num):
    nonlocal vertices, normals, colors, indices, splits, groups, plannedRedirection
    faces = {i for i in groups[nl]["f"]}
    toBeCopied = [indices[i+j] for j in range(3) for i in faces if indices[i+j] in splits]
    
    indexOfCopy = len(vertices)
    print("indexOfCopy",indexOfCopy)
    conversion = {}
    for tbc in toBeCopied:
      conversion[tbc] = len(vertices)
      vertices.append([
          vertices[tbc][0]+(0.1*num+0.1*(mun+0.5))*normals[tbc][0],
          vertices[tbc][1]+(0.1*num+0.1*(mun+0.5))*normals[tbc][1],
          vertices[tbc][2]+(0.1*num+0.1*(mun+0.5))*normals[tbc][2]
        ] if debug else vertices[tbc])
      normals.append(normals[tbc]) if normals != [] else None
      colors.append([colors[tbc][0],colors[tbc][1]/(mun+1),colors[tbc][2]/(num+1)] if debug else colors[tbc]) if colors != [] else None

    # addToIsTheSame(conversion)
    for f in groups[nl]["f"]:
      for v in range(3):
        try:
          offset = toBeCopied.index(indices[f+v])
          plannedRedirection[f+v] = indexOfCopy+offset
        except ValueError:
          continue

    
    # isTheSame, seam
    # indexOfCopy = len(vertices)
    
    # copy = {
    #   "vertices": [[vertices[j][0]+0.1*normals[j][0],vertices[j][1]+0.1*normals[j][1],vertices[j][2]+0.1*normals[j][2]] 
    #               if debug else vertices[j] for j in splits],
    #   "normals" : [normals[j] for j in splits] if normals != [] else [],
    #   "colors"  : [[colors[j][0],colors[j][1]/2,colors[j][2]/2] if debug else colors[j] for j in splits] if colors != [] else [],
    # }

    # vertices += copy["vertices"]
    # normals  += copy["normals" ]
    # colors   += copy["colors"  ]

    
    # conversion = {seam["tears"][0]:seam["tears"][0],seam["tears"][1]:seam["tears"][1]}
    # for i in range(len(splits)):
    #   conversion[splits[i]] = indexOfCopy + i
    # addToIsTheSame(conversion)

    # return indexOfCopy
  mun = 0
  seam2 = []
  for seam in seams:
    mun += 1
    if seam["splits"] is None or len(seam["splits"]) == 0: continue

    if seam["tears"] is None: seam["tears"] = [None,None]
    # tears  = [expandToIncludeTheSame([i]) for i in seam["tears"]]
    # splits = expandToIncludeTheSame(seam["splits"])
    tears  = [[i] for i in seam["tears"]]
    splits = seam["splits"]
    fullSeam = tears[0]+splits+tears[1]
    seam2  += [{fullSeam[i],fullSeam[i+1]} for i in range(len(fullSeam)-1)]

    groups = []

    for t in tears[0]:
      if t is not None and debug: colors[t] = [0.0,0.0,1.0]
    for t in tears[1]:
      if t is not None and debug: colors[t] = [0.0,0.0,1.0]
        
    # segregation
    for v in splits:
      facesConnectedToV = [i//3 * 3 for i in range(len(indices)) if v == indices[i]]
      assignSideToFaces(facesConnectedToV)
    
    # decide seam relocation
    longest = 0
    for i in range(1,len(groups)):
      if len(groups[i]["f"]) > len(groups[i-1]["f"]): longest = i
    [print(len(g["f"])) for g in groups]
    notLongest = [i for i in range(len(groups)) if i != longest]
    iterator = 0
    for nl in notLongest:
      iterator+=1
      makeFaceVerticesCopy(nl,mun,iterator)
      # for f in groups[nl]["f"]:
      #   for v in range(3):
      #     try:
      #       offset = splits.index(indices[f+v])
      #       plannedRedirection[f+v] = indexOfCopy+offset
      #     except ValueError:
      #       continue
  # apply Cleave
  for k,v in plannedRedirection.items():
    indices[k] = v
  data["vertices"] = vertices
  data["normals" ] = normals 
  data["colors"  ] = colors  
  data["indices" ] = indices
  dataToNumpyArray(data)
  return [[plannedRedirection[s] if s in plannedRedirection else s for s in seam] for s in seams]

# n-gon generators #####################################
def star_ngonGenerator(n, size, size_inner, z):
  data = dataStructure()

  vertices = np.zeros((2 * n, 3), dtype=np.float32)
  for i in range(0, 2 * n, 2):
    theta = i * pi / n
    alpha = theta + pi / n
    vertices[i][0], vertices[i][1], vertices[i][2] = (
      cos(theta) * size_inner,
      sin(theta) * size_inner,
      z,
    )
    vertices[i + 1][0], vertices[i + 1][1], vertices[i + 1][2] = (
      cos(alpha) * size,
      sin(alpha) * size,
      z,
    )
  data["vertices"] = vertices

  for i in range(0, 2 * n, 2):
    data["indices"].append(i)
    data["indices"].append(i + 1)
    data["indices"].append((i + 2) % (2 * n))
  for i in range(1, n - 1):
    data["indices"].append(0)
    data["indices"].append(2 * i % (2 * n))
    data["indices"].append(2 * (i + 1) % (2 * n))

  return data


def ngon_ngonGenerator(n, size, w_multiplier, z):
  data = dataStructure()
  vertices = np.zeros((n, 3), dtype=np.float32)
  for i in range(n):
    theta = i * 2 * pi / n
    vertices[i][0], vertices[i][1], vertices[i][2] = (
      cos(theta) * size * w_multiplier,
      sin(theta) * size,
      z,
    )
  data["vertices"] = vertices

  for i in range(1, n - 1):
    data["indices"].append(0)
    data["indices"].append(i)
    data["indices"].append(i + 1)

  return data


def simple_ngonGenerator(n, size, z):
  res = []
  for i in range(n):
    theta = i * 2 * pi / n
    res.append([cos(theta) * size, sin(theta) * size, z])
  return res


# colorings ###################################
def normalColoring(data, **kwargs):
  data["colors"] = data["normals"] / 2 + 0.5
  return data


def positionalColoring(data, **kwargs):
  vertices = (
    data["vertices"]
    if (np.max(data["vertices"], axis=0) - np.min(data["vertices"], axis=0))[2] != 0
    else data["vertices"][:, :3]
  )
  data["colors"] = (vertices - np.min(vertices, axis=0)) / (
    np.max(vertices, axis=0) - np.min(vertices, axis=0)
  )

  return data


def moduloColoring(data, **kwargs):
  data["colors"] = data["vertices"] * 500 % 1000 / 1000


def hexColoring(data, hex=0xFF69FF, **kwargs):
  red = float(((hex & 0xFF0000) >> 16) / 0xFF)
  green = float(((hex & 0x00FF00) >> 8) / 0xFF)
  blue = float(((hex & 0x0000FF) >> 0) / 0xFF)
  data["colors"] = np.full_like(data["vertices"], [red, green, blue])


def chooseColoring(mode, **kwargs):
  match mode:
    case "position":
      return positionalColoring
    case "normal":
      return normalColoring
    case "modulo":
      return moduloColoring
    case "hex":
      return hexColoring
    case _:
      return positionalColoring


# vertex normals ###################################
def vertexNeighborNormals(data):
  normals = np.zeros_like(data["vertices"])
  indices = data["indices"]
  vertices = data["vertices"]
  total = len(indices)
  logger.debug("Starting normals")

  def fastCross(c, d):
    e = np.zeros_like(c)
    e[0] = c[1] * d[2] - c[2] * d[1]
    e[1] = c[2] * d[0] - c[0] * d[2]
    e[2] = c[0] * d[1] - c[1] * d[0]
    return e

  for i in range(0, total, 3):
    if i % 10000 == 0:
      print(f"Doing {i}/{total} normal calculations", end="\r")
    v0, v1, v2 = indices[i], indices[i + 1], indices[i + 2]
    v00, v11, v22 = vertices[v0], vertices[v1], vertices[v2]
    d0 = v11 - v00
    d1 = v22 - v11
    d2 = v00 - v22

    normals[v0] += fastCross(d0, -d2)
    normals[v1] += fastCross(d1, -d0)
    normals[v2] += fastCross(d2, -d1)

  logger.debug("Normalizing normals")
  # don't ask me, my brain is out of steam
  normals = normals / np.linalg.norm(normals, axis=1)[:, np.newaxis]

  data["normals"] = normals
