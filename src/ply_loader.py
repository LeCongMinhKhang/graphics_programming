from dataclasses import dataclass, field
from pathlib import Path
import logging

import numpy as np

from src.shape_generators import tools

logger = logging.getLogger(__name__)

# PLY type name -> numpy type code
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

POS_NAMES = ("x", "y", "z")
NOR_NAMES = ("nx", "ny", "nz")
COLOR_ALIASES = [
  ("red", "green", "blue"),
  ("r", "g", "b"),
  ("diffuse_red", "diffuse_green", "diffuse_blue"),
]
UV_ALIASES = [("u", "v"), ("s", "t"), ("texture_u", "texture_v"), ("texture_s", "texture_t")]
FACE_INDEX_NAMES = ("vertex_indices", "vertex_index")


class PlyError(ValueError):
  pass


@dataclass
class Property:
  name: str
  dtype: str  # numpy code; for lists this is the item type
  count_dtype: str | None = None  # set only for list properties

  @property
  def is_list(self):
    return self.count_dtype is not None


@dataclass
class Element:
  name: str
  count: int
  properties: list = field(default_factory=list)


@dataclass
class Header:
  format: str
  version: str
  elements: list
  body_offset: int
  comments: list


def _ply_type(name):
  try:
    return TYPE_MAP[name]
  except KeyError:
    raise PlyError(f'unknown type "{name}"') from None


def parse_header(raw: bytes) -> Header:
  end = raw.find(b"end_header")
  if end < 0:
    raise PlyError("no end_header found")
  nl = raw.find(b"\n", end)
  if nl < 0:
    raise PlyError("end_header is not terminated by a newline")
  lines = raw[:nl].decode("ascii", errors="replace").splitlines()

  if not lines or lines[0].split() != ["ply"]:
    raise PlyError("invalid header first line: not a ply file")

  file_format = None
  version = None
  elements = []
  comments = []

  for line in lines[1:]:
    tok = line.split()
    if not tok:
      continue
    kw = tok[0]

    if kw == "end_header":
      break
    elif kw == "format":
      if len(tok) != 3:
        raise PlyError(f"format line should have 3 fields, not {len(tok)}")
      if tok[1] not in FORMATS:
        raise PlyError(f'unknown format "{tok[1]}"')
      file_format, version = tok[1], tok[2]
    elif kw in ("comment", "obj_info"):
      comments.append(" ".join(tok[1:]))
    elif kw == "element":
      if len(tok) != 3:
        raise PlyError(f"element line should have 3 fields, not {len(tok)}")
      elements.append(Element(tok[1], int(tok[2])))
    elif kw == "property":
      if not elements:
        raise PlyError("property line without a corresponding element")
      if len(tok) >= 2 and tok[1] == "list":
        if len(tok) != 5:
          raise PlyError(f"list property should have 5 fields, not {len(tok)}")
        prop = Property(tok[4], _ply_type(tok[3]), _ply_type(tok[2]))
      else:
        if len(tok) != 3:
          raise PlyError(f"property line should have 3 fields, not {len(tok)}")
        prop = Property(tok[2], _ply_type(tok[1]))
      elements[-1].properties.append(prop)
    else:
      raise PlyError(f'unknown header keyword "{kw}"')

  if file_format is None:
    raise PlyError("missing format line")
  return Header(file_format, version, elements, nl + 1, comments)


# ASCII body ==============================


def _read_ascii_element(tokens, pos, el):
  props = el.properties
  n = el.count
  try:
    if not any(p.is_list for p in props):
      m = len(props)
      chunk = tokens[pos : pos + n * m]
      if len(chunk) < n * m:
        raise IndexError
      arr = np.array(chunk, dtype=np.float64).reshape(n, m)
      return {p.name: arr[:, i].astype(p.dtype) for i, p in enumerate(props)}, pos + n * m

    cols = {p.name: [] for p in props}
    for _ in range(n):
      for p in props:
        if p.is_list:
          k = int(tokens[pos])
          items = tokens[pos + 1 : pos + 1 + k]
          if len(items) < k:
            raise IndexError
          cols[p.name].append(np.array(items, dtype=np.float64).astype(p.dtype))
          pos += 1 + k
        else:
          cols[p.name].append(float(tokens[pos]))
          pos += 1
    out = {}
    for p in props:
      out[p.name] = cols[p.name] if p.is_list else np.array(cols[p.name], dtype=p.dtype)
    return out, pos
  except (IndexError, ValueError) as e:
    raise PlyError(f'malformed or truncated ascii data in element "{el.name}": {e}') from None


# binary body ==============================


def _read_binary_element(buf, pos, el, endian):
  props = el.properties
  n = el.count

  def need(upto):
    if upto > len(buf):
      raise PlyError(f'truncated binary data in element "{el.name}"')

  # all scalar: a single structured read
  if not any(p.is_list for p in props):
    dt = np.dtype([(p.name, endian + p.dtype) for p in props])
    end = pos + dt.itemsize * n
    need(end)
    arr = np.frombuffer(buf, dt, n, pos)
    return {p.name: arr[p.name].astype(p.dtype) for p in props}, end

  # single list property with constant length (typical triangle/quad faces): fast path
  if len(props) == 1 and n > 0:
    p = props[0]
    cdt = np.dtype(endian + p.count_dtype)
    need(pos + cdt.itemsize)
    c0 = int(np.frombuffer(buf, cdt, 1, pos)[0])
    if c0 > 0:
      dt = np.dtype([("c", cdt), ("v", endian + p.dtype, (c0,))])
      end = pos + dt.itemsize * n
      if end <= len(buf):
        arr = np.frombuffer(buf, dt, n, pos)
        if (arr["c"] == c0).all():
          return {p.name: arr["v"].astype(p.dtype)}, end

  # general path: variable-length lists and/or mixed properties
  cols = {p.name: [] for p in props}
  for _ in range(n):
    for p in props:
      if p.is_list:
        cdt = np.dtype(endian + p.count_dtype)
        need(pos + cdt.itemsize)
        k = int(np.frombuffer(buf, cdt, 1, pos)[0])
        pos += cdt.itemsize
        idt = np.dtype(endian + p.dtype)
        need(pos + idt.itemsize * k)
        cols[p.name].append(np.frombuffer(buf, idt, k, pos).astype(p.dtype))
        pos += idt.itemsize * k
      else:
        sdt = np.dtype(endian + p.dtype)
        need(pos + sdt.itemsize)
        cols[p.name].append(np.frombuffer(buf, sdt, 1, pos)[0])
        pos += sdt.itemsize
  out = {}
  for p in props:
    out[p.name] = cols[p.name] if p.is_list else np.array(cols[p.name], dtype=p.dtype)
  return out, pos


def parse_body(raw: bytes, header: Header):
  """Returns {element_name: {property_name: column}} for every element in the file."""
  elements = {}
  endian = FORMATS[header.format]

  if endian is None:
    tokens = raw[header.body_offset :].decode("ascii", errors="replace").split()
    pos = 0
    for el in header.elements:
      elements[el.name], pos = _read_ascii_element(tokens, pos, el)
  else:
    pos = header.body_offset
    for el in header.elements:
      elements[el.name], pos = _read_binary_element(raw, pos, el, endian)
  return elements


# ------------------------------------------------------------- mesh building


def _stack(columns, names):
  if all(n in columns for n in names):
    return np.stack([columns[n] for n in names], axis=1)
  return None


def triangulate(faces):
  """Fan-triangulate faces. Accepts a (n, k) array or a list of 1D index arrays."""
  if isinstance(faces, np.ndarray) and faces.ndim == 2:
    k = faces.shape[1]
    if k < 3:
      return np.empty((0, 3), dtype=np.int64)
    tris = np.stack(
      [np.repeat(faces[:, :1], k - 2, axis=1), faces[:, 1 : k - 1], faces[:, 2:k]], axis=2
    )
    return tris.reshape(-1, 3).astype(np.int64)

  out = []
  skipped = 0
  for f in faces:
    if len(f) < 3:
      skipped += 1
      continue
    hub = f[0]
    for i in range(1, len(f) - 1):
      out.append((hub, f[i], f[i + 1]))
  if skipped:
    logger.warning("skipped %d degenerate faces (< 3 vertices)", skipped)
  return np.array(out, dtype=np.int64).reshape(-1, 3)


def fill_data(elements, data):
  vert = elements.get("vertex")
  n_vertices = 0
  if vert:
    pos = _stack(vert, POS_NAMES)
    if pos is not None:
      data["vertices"] = pos.astype(np.float32)
      n_vertices = len(pos)

    for names in COLOR_ALIASES:
      col = _stack(vert, names)
      if col is not None:
        if np.issubdtype(col.dtype, np.integer):  # uchar 0..255 -> 0..1
          col = col.astype(np.float32) / np.iinfo(col.dtype).max
        data["colors"] = col.astype(np.float32)
        break

    nor = _stack(vert, NOR_NAMES)
    if nor is not None:
      data["normals"] = nor.astype(np.float32)

    for names in UV_ALIASES:
      uv = _stack(vert, names)
      if uv is not None:
        data["uvs"] = uv.astype(np.float32)
        break

  face = elements.get("face")
  if face:
    key = next((k for k in FACE_INDEX_NAMES if k in face), None)
    if key is not None:
      tris = triangulate(face[key])
      if tris.size and n_vertices and (tris.min() < 0 or tris.max() >= n_vertices):
        raise PlyError("face index out of range")
      data["indices"] += tris.ravel().tolist()
    else:
      logger.warning("face element has no vertex_indices/vertex_index property")

  return data


def parse(path):
  data = tools.dataStructure()

  file_path = Path(path)
  if not file_path.exists():
    logger.error("file %s does not exist", path)
    return data

  raw = file_path.read_bytes()
  header = parse_header(raw)
  elements = parse_body(raw, header)
  fill_data(elements, data)

  tools.dataToNumpyArray(data)
  if data["normals"].size == 0:
    tools.vertexNeighborNormals(data)
  tools.dataToNumpyArray(data)
  return data


if __name__ == "__main__":
  parse("inputs/ply/test.ply")
