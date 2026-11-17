# from OpenGL import GL
# import numpy as np
from pathlib import Path
import numpy as np
import logging

from src.shape_generators import tools

logger = logging.getLogger(__name__)

# Remark: maybe it is needed to check for each property name to ensure the correct order
#  For now we assume vertex: x y z r g b nx ny nz

VERTEX_POS_NAMES = ["x", "y", "z"]
VERTEX_COL_NAMES = ["red", "green", "blue"]
VERTEX_NOR_NAMES = ["nx", "ny", "nz"]
VERTEX_TEX_NAMES = ["u", "v"]
VERTEX_NAMES = VERTEX_POS_NAMES + VERTEX_COL_NAMES + VERTEX_NOR_NAMES + VERTEX_TEX_NAMES
PROPERTY_NAMES = VERTEX_NAMES + ["vertex_indices"]

TYPES = ["char", "uchar", "short", "ushort", "int", "uint", "float", "double"]


def inter(it1, it2):
  for e1 in it1:
    if e1 in it2:
      return True
  return False


def unroll_triangle_fan(indices):
  hub = indices[0]
  previous = indices[2]
  decompressed_indices = [hub, indices[1], previous]
  for i in indices[3:]:
    decompressed_indices.append(hub)
    decompressed_indices.append(previous)
    decompressed_indices.append(i)
    previous = i
  return decompressed_indices


def parse_header(lines):
  # [
  #   {"format", "ascii"/"binary_little_endian"/"binary_big_endian", version number},
  # ]
  file_layout = []
  current_field = None  # remember the current field (a member of file_layout) to add properties

  line_arr = (" ".join(next(lines).strip().split())).split(" ")
  if line_arr[0] != "ply" or len(line_arr) != 1:
    logger.error("invalid header first line: not a ply file")
    exit(1)
  line_arr = (" ".join(next(lines).strip().split())).split(" ")

  while lines is not None and line_arr[0] != "end_header":
    match line_arr[0]:
      case "format":
        if len(line_arr) != 3:
          logger.error("format line should be of length 3, not %d", len(line_arr))
          exit(1)
        file_format = line_arr[1]
        if file_format not in ("ascii", "binary_little_endian", "binary_big_endian"):
          logger.error(
            'unknown format option %s (valid are "ascii", "binary_little_endian", "binary_big_endian")',
            file_format,
          )
          exit(1)
        file_layout.append(
          {"field": "format", "format": file_format, "version": float(line_arr[2])}
        )

      case "comment":
        pass

      case "element":
        if len(line_arr) != 3:
          logger.error("element line should be of length 3, not %d", len(line_arr))
          exit(1)
        match line_arr[1]:
          case "vertex":
            file_layout.append({"field": "vertex", "number": int(line_arr[2]), "entries": []})
            current_field = file_layout[-1]
          case "face":
            file_layout.append({"field": "face", "number": int(line_arr[2]), "entries": []})
            current_field = file_layout[-1]
          case _:
            logger.error('keyword "%s" not recognized"', line_arr[0])
            exit(1)

      case "property":
        if current_field is None:
          logger.error("property line without a corresponding element")
          exit(1)
        if len(line_arr) < 2:
          logger.error("property line should be of length 2, not %d", len(line_arr))
          exit(1)
        match line_arr[1]:
          case "char" | "uchar" | "short" | "ushort" | "int" | "uint" | "float" | "double":
            if len(line_arr) != 3:
              logger.error("property list line should be of length 3, not %d", len(line_arr))
              exit(1)
            if line_arr[2] not in PROPERTY_NAMES:
              logger.error('unknown property name "%s"', line_arr[2])
              exit(1)
            current_field["entries"].append((line_arr[2], line_arr[1]))
          case "list":
            if len(line_arr) != 5:
              logger.error("property list line should be of length 5, not %d", len(line_arr))
              exit(1)
            if line_arr[2] not in TYPES:
              logger.error('unknown list type "%d"', line_arr[2])
              exit(1)
            if line_arr[3] not in TYPES:
              logger.error('unknown list type "%d"', line_arr[3])
              exit(1)
            if line_arr[4] not in PROPERTY_NAMES:
              logger.error('unknown property name "%s"', line_arr[4])
              exit(1)
            current_field["entries"].append((line_arr[4], (line_arr[1], line_arr[2], line_arr[3])))

          case _:
            logger.error('keyword "%s" not recognized"', line_arr[2])
            exit(1)

      case _:
        logger.error('keyword "%s" not recognized"', line_arr[0])
        exit(1)
    line_arr = (" ".join(next(lines).strip().split())).split(" ")

  return file_layout


def parse_body(lines, header, data):
  if len(header) < 1:
    logger.error("no content in header structure")
    exit(1)
  if header[0]["field"] != "format":
    logger.error(
      'first entry in header structure should be the format, not "%s"', header[0]["field"]
    )
    exit(1)
  file_format = header[0]["format"]
  if file_format == "ascii":  # ascii data
    for field in header[1:]:
      n = field["number"]
      entries = field["entries"]
      field_name = field["field"]

      if field_name == "vertex":
        names = [name for name, _ in field["entries"]]
        if inter(names, VERTEX_POS_NAMES):
          data["vertices"] = np.zeros((n, 3), dtype=np.float32)
        if inter(names, VERTEX_COL_NAMES):
          data["colors"] = np.zeros((n, 3), dtype=np.float32)
        if inter(names, VERTEX_NOR_NAMES):
          data["normals"] = np.zeros((n, 3), dtype=np.float32)
        if inter(names, VERTEX_TEX_NAMES):
          data["uvs"] = np.zeros((n, 2), dtype=np.float32)
      # cannot initialize indices array as we may have lists of different sizes

      for i in range(n):
        line_arr = (" ".join(next(lines).strip().split())).split(" ")
        for j, (name, dtype) in enumerate(entries):
          match name:
            case "vertex_indices":
              k = int(line_arr[0])
              if len(line_arr) != k + 1:
                logger.error("%s line should be of length %d, not %d", name, k, len(line_arr))
                exit(1)
              if k > 3:
                data["indices"] += unroll_triangle_fan([int(el) for el in line_arr[1:]])
              else:
                data["indices"] += [int(el) for el in line_arr[1:]]
            case "x":
              data["vertices"][i][0] = float(line_arr[j])
            case "y":
              data["vertices"][i][1] = float(line_arr[j])
            case "z":
              data["vertices"][i][2] = float(line_arr[j])
            case "red":
              data["colors"][i][0] = float(line_arr[j])
            case "green":
              data["colors"][i][1] = float(line_arr[j])
            case "blue":
              data["colors"][i][0] = float(line_arr[j])
            case "nx":
              data["normals"][i][0] = float(line_arr[j])
            case "ny":
              data["normals"][i][1] = float(line_arr[j])
            case "nz":
              data["normals"][i][2] = float(line_arr[j])
            case "u":
              data["uvs"][i][0] = float(line_arr[j])
            case "v":
              data["uvs"][i][1] = float(line_arr[j])
            case _:
              logger.error('unknown name "%s"', name)
              exit(1)

  else:  # binary data
    pass

  return data


def parse(path):
  data = tools.dataStructure()

  file_path = Path(path)
  if file_path.exists():
    file = file_path.read_text()

    lines = iter(file.split("\n"))
    header = parse_header(lines)
    parse_body(lines, header, data)
    tools.dataToNumpyArray(data)
    tools.vertexNeighborNormals(data) if data["normals"].size == 0 else None
    tools.dataToNumpyArray(data)
  return data


if __name__ == "__main__":
  parse("inputs/ply/test.ply")
