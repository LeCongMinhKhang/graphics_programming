# ascii parser written by hand, binary one by Claude free version

from pathlib import Path
import numpy as np
import logging

from src.shape_generators import tools

logger = logging.getLogger(__name__)

VERTEX_POS_NAMES = ["x", "y", "z"]
VERTEX_COL_NAMES = ["red", "green", "blue"]
VERTEX_NOR_NAMES = ["nx", "ny", "nz"]
VERTEX_TEX_NAMES = ["u", "v"]

# PLY type name -> numpy type code (legacy and modern names)
TYPE_MAP = {
  "char": "i1",
  "int8": "i1",
  "uchar": "u1",
  "uint8": "u1",
  "short": "i2",
  "int16": "i2",
  "ushort": "u2",
  "uint16": "u2",
  "int": "i4",
  "int32": "i4",
  "uint": "u4",
  "uint32": "u4",
  "float": "f4",
  "float32": "f4",
  "double": "f8",
  "float64": "f8",
}

FORMATS = {"ascii": None, "binary_little_endian": "<", "binary_big_endian": ">"}

# alternative property names
ALIASES = {
  "r": "red",
  "g": "green",
  "b": "blue",
  "diffuse_red": "red",
  "diffuse_green": "green",
  "diffuse_blue": "blue",
  "s": "u",
  "t": "v",
  "texture_u": "u",
  "texture_v": "v",
  "texture_s": "u",
  "texture_t": "v",
  "vertex_index": "vertex_indices",
}


class PlyError(ValueError):
  pass


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
  #   {"field": "format", "format": ..., "version": ...},
  #   {"field": <element name>, "number": n, "entries": [(name, dtype) | (name, ("list", count_dtype, item_dtype))]},
  # ]
  file_layout = []
  current_field = None  # remember the current field (a member of file_layout) to add properties

  try:
    line_arr = next(lines).split()
    if line_arr != ["ply"]:
      raise PlyError("invalid header first line: not a ply file")
    line_arr = next(lines).split()

    while not line_arr or line_arr[0] != "end_header":
      keyword = line_arr[0] if line_arr else None
      match keyword:
        case None:  # empty line
          pass

        case "format":
          if len(line_arr) != 3:
            raise PlyError(f"format line should be of length 3, not {len(line_arr)}")
          file_format = line_arr[1]
          if file_format not in FORMATS:
            raise PlyError(
              f'unknown format option "{file_format}" '
              '(valid are "ascii", "binary_little_endian", "binary_big_endian")'
            )
          try:
            version = float(line_arr[2])
          except ValueError:
            raise PlyError(f'invalid version "{line_arr[2]}"') from None
          file_layout.append({"field": "format", "format": file_format, "version": version})

        case "comment" | "obj_info":
          pass

        case "element":
          if len(line_arr) != 3:
            raise PlyError(f"element line should be of length 3, not {len(line_arr)}")
          try:
            number = int(line_arr[2])
          except ValueError:
            raise PlyError(f'invalid element count "{line_arr[2]}"') from None
          # any element is accepted; the ones we don't use are parsed and discarded
          file_layout.append({"field": line_arr[1], "number": number, "entries": []})
          current_field = file_layout[-1]

        case "property":
          if current_field is None:
            raise PlyError("property line without a corresponding element")
          if len(line_arr) < 2:
            raise PlyError(f"property line should be of length 3 or 5, not {len(line_arr)}")
          use_aliases = current_field["field"] in ("vertex", "face")

          if line_arr[1] == "list":
            if len(line_arr) != 5:
              raise PlyError(f"property list line should be of length 5, not {len(line_arr)}")
            if line_arr[2] not in TYPE_MAP:
              raise PlyError(f'unknown list type "{line_arr[2]}"')
            if line_arr[3] not in TYPE_MAP:
              raise PlyError(f'unknown list type "{line_arr[3]}"')
            name = line_arr[4]
            if use_aliases:
              name = ALIASES.get(name, name)
            current_field["entries"].append(
              (name, ("list", TYPE_MAP[line_arr[2]], TYPE_MAP[line_arr[3]]))
            )
          elif line_arr[1] in TYPE_MAP:
            if len(line_arr) != 3:
              raise PlyError(f"property line should be of length 3, not {len(line_arr)}")
            name = line_arr[2]
            if use_aliases:
              name = ALIASES.get(name, name)
            current_field["entries"].append((name, TYPE_MAP[line_arr[1]]))
          else:
            raise PlyError(f'unknown property type "{line_arr[1]}"')

        case _:
          raise PlyError(f'keyword "{keyword}" not recognized')

      line_arr = next(lines).split()
  except StopIteration:
    raise PlyError("no end_header found") from None

  return file_layout


def make_reader(file_format, body):
  """Returns read(dtype) -> python number, consuming the body sequentially."""
  endian = FORMATS[file_format]
  pos = 0

  if endian is None:  # ascii: whitespace separated token stream, line breaks don't matter
    tokens = body.decode("ascii", errors="replace").split()

    def read(dtype):
      nonlocal pos
      try:
        tok = tokens[pos]
        pos += 1
        return int(float(tok)) if dtype[0] in "iu" else float(tok)
      except IndexError:
        raise PlyError("truncated ascii data") from None
      except ValueError:
        raise PlyError(f'malformed ascii value "{tok}"') from None

  else:

    def read(dtype):
      nonlocal pos
      dt = np.dtype(endian + dtype)
      end = pos + dt.itemsize
      if end > len(body):
        raise PlyError("truncated binary data")
      value = np.frombuffer(body, dt, 1, pos)[0].item()
      pos = end
      return value

  return read


def parse_body(body, header, data):
  if len(header) < 1:
    raise PlyError("no content in header structure")
  if header[0]["field"] != "format":
    raise PlyError(
      f'first entry in header structure should be the format, not "{header[0]["field"]}"'
    )

  read = make_reader(header[0]["format"], body)
  n_vertices = 0

  for field in header[1:]:
    n = field["number"]
    entries = field["entries"]
    field_name = field["field"]
    types = dict(entries)

    if field_name == "vertex":
      n_vertices = n
      names = [name for name, _ in entries]
      if inter(names, VERTEX_POS_NAMES):
        data["vertices"] = np.zeros((n, 3), dtype=np.float32)
      if inter(names, VERTEX_COL_NAMES):
        data["colors"] = np.zeros((n, 3), dtype=np.float32)
      if inter(names, VERTEX_NOR_NAMES):
        data["normals"] = np.zeros((n, 3), dtype=np.float32)
      if inter(names, VERTEX_TEX_NAMES):
        data["uvs"] = np.zeros((n, 2), dtype=np.float32)
    # cannot initialize indices array as we may have lists of different sizes

    skipped = 0
    for i in range(n):
      for name, dtype in entries:
        # read the value (scalar or list) so the stream always stays in sync
        if isinstance(dtype, tuple):
          _, count_dtype, item_dtype = dtype
          k = read(count_dtype)
          value = [read(item_dtype) for _ in range(k)]
        else:
          value = read(dtype)

        if field_name == "face":
          if name == "vertex_indices":
            k = len(value)
            if k < 3:
              skipped += 1
            elif k > 3:
              data["indices"] += unroll_triangle_fan(value)
            else:
              data["indices"] += value
          continue

        if field_name != "vertex":
          continue

        match name:
          case "x":
            data["vertices"][i][0] = value
          case "y":
            data["vertices"][i][1] = value
          case "z":
            data["vertices"][i][2] = value
          case "red" | "green" | "blue":
            if types[name][0] in "iu":  # integer colors (uchar 0..255) -> 0..1
              value = value / np.iinfo(np.dtype(types[name])).max
            data["colors"][i][VERTEX_COL_NAMES.index(name)] = value
          case "nx":
            data["normals"][i][0] = value
          case "ny":
            data["normals"][i][1] = value
          case "nz":
            data["normals"][i][2] = value
          case "u":
            data["uvs"][i][0] = value
          case "v":
            data["uvs"][i][1] = value
          case _:
            pass  # unknown vertex property (alpha, quality, ...): read and ignored

    if skipped:
      logger.warning("skipped %d degenerate faces (< 3 vertices)", skipped)

  if n_vertices and len(data["indices"]) > 0:
    if min(data["indices"]) < 0 or max(data["indices"]) >= n_vertices:
      raise PlyError("face index out of range")

  return data


def parse(path):
  logger.debug('parsing "%s" file', path)
  data = tools.dataStructure()

  file_path = Path(path)
  if not file_path.exists():
    logger.error("file %s does not exist", path)
    return data

  raw = file_path.read_bytes()  # bytes, so binary files work
  # the header is ascii; the body starts right after the newline following end_header
  idx = raw.find(b"\nend_header")
  if idx < 0:
    raise PlyError("no end_header found")
  nl = raw.find(b"\n", idx + 1)
  if nl < 0:
    raise PlyError("end_header is not terminated by a newline")

  lines = iter(raw[:nl].decode("ascii", errors="replace").split("\n"))
  header = parse_header(lines)
  parse_body(raw[nl + 1 :], header, data)
  logger.debug("parsing finished")

  tools.dataToNumpyArray(data)
  if data["normals"].size == 0:
    tools.vertexNeighborNormals(data)
  tools.dataToNumpyArray(data)

  return data


if __name__ == "__main__":
  parse("inputs/ply/test.ply")
