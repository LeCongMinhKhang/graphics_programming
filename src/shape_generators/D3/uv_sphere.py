import numpy as np
import logging
import OpenGL.GL as GL

logger = logging.getLogger(__name__)


def generate(radius=1.0, n=3):
  """
  radius: sphere radius
  n: n is number of rings, 2n is the number of divisions per ring
  """
  if radius <= 0:
    logger.error("radius should be > 0.")
    exit(1)
  if n < 2:
    logger.error("n should be >= 2.")
    exit(1)

  rings = n  # latitude samples, pole to pole
  segments = 2 * n  # longitude samples per ring (seam vertex duplicated)

  vertices = []
  normals = []
  indices = []

  for i in range(rings):
    phi = i * np.pi / (rings - 1)
    z = -radius * np.cos(phi)  # scaled by radius
    sub_radius = radius * np.sin(phi)

    for k in range(segments):
      theta = k * 2 * np.pi / (segments - 1)  # last vertex lands on 2*pi (seam)
      point = np.array([sub_radius * np.cos(theta), sub_radius * np.sin(theta), z])
      vertices.append(point)
      normals.append(point / radius)  # unit length, and safe at the poles

      if i != rings - 1 and k != segments - 1:
        i1 = i * segments + k
        i2 = i1 + 1
        i3 = (i + 1) * segments + k
        i4 = i3 + 1
        indices += [i1, i2, i3, i3, i2, i4]

  vertices = np.array(vertices, dtype=np.float32)
  indices = np.array(indices, dtype=np.uint32)
  normals = np.array(normals, dtype=np.float32)
  colors = ((vertices / np.abs(vertices).max()) * 0.5 + 0.5).astype(np.float32)

  return {
    "vertices": vertices,
    "indices": indices,
    "normals": normals,
    "colors": colors,
    "mode": GL.GL_TRIANGLES,
  }
