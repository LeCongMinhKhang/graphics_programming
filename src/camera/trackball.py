from src.camera.camera import Camera
import math  # mainly for trigonometry functions

# external module
import numpy as np  # matrices, vectors & quaternions are numpy arrays
import logging
from src.transform import (
  quaternion_from_euler,
  vec,
  quaternion_mul,
  translate,
  perspective,
  quaternion_matrix,
  normalized,
  quaternion_from_axis_angle,
)


class Trackball(Camera):
  """Virtual trackball for 3D scene viewing. Independent of windows system."""

  logger = logging.getLogger(__name__)

  def __init__(self, yaw=0.0, roll=0.0, pitch=0.0, distance=5.0, radians=None):
    """Build a new trackball with specified view, angles in degrees"""
    self.rotation = quaternion_from_euler(yaw, roll, pitch, radians)
    self.distance_init = max(distance, 0.001)
    self.pos2d = vec(0.0, 0.0)

    self.mouse_old = (0, 0)

  def drag(self, old, new, winsize):
    """Move trackball from old to new 2d normalized windows position"""
    old, new = ((2 * vec(pos) - winsize) / winsize for pos in (old, new))
    self.rotation = quaternion_mul(self._rotate(old, new), self.rotation)

  def zoom(self, zoom, size):
    """Zoom trackball to a factor normalized by windows size"""
    self.distance = max(0.001, self.distance_init * (1 - 50 * zoom / size))

  def pan(self, old, new):
    """Pan in camera's reference by a 2d vector factor of (new - old)"""
    self.pos2d += (vec(new) - old) * 0.001 * self.distance

  def _view_matrix(self):
    """View matrix transformation, including distance to target point"""
    return translate(*self.pos2d, -self.distance) @ self.matrix()

  def _projection_matrix(self, winsize):
    """Projection matrix with z-clipping range adaptive to distance"""
    z_range = vec(0.1, 100) * self.distance  # proportion to dist
    return perspective(35, winsize[0] / winsize[1], *z_range)

  def matrix(self):
    """Rotational component of trackball position"""
    return quaternion_matrix(self.rotation)

  def _project3d(self, position2d, radius=0.8):
    """Project x,y on sphere OR hyperbolic sheet if away from center"""
    p2, r2 = sum(position2d * position2d), radius * radius
    zcoord = math.sqrt(r2 - p2) if 2 * p2 < r2 else r2 / (2 * math.sqrt(p2))
    return vec(*position2d, zcoord)

  def _rotate(self, old, new):
    """Rotation of axis orthogonal to old & new's 3D ball projections"""
    old, new = (normalized(self._project3d(pos)) for pos in (old, new))
    phi = 2 * math.acos(np.clip(np.dot(old, new), -1, 1))
    return quaternion_from_axis_angle(np.cross(old, new), radians=phi)

  def update(self, uniforms, mouse):
    winsize = self.get_uniform_value(uniforms, "iResolution")

    if mouse["mb1_down"] or mouse["mb2_down"]:
      if (mouse["mb_x"] == mouse["mb_press_x"]) and (mouse["mb_y"] == mouse["mb_press_y"]):
        # if new click, reinit old position and dont move
        self.mouse_old = (mouse["mb_press_x"], mouse["mb_press_y"])
      else:
        if mouse["mb1_down"]:
          self.drag(self.mouse_old, (mouse["mb_x"], mouse["mb_y"]), winsize)
        elif mouse["mb2_down"]:
          self.pan(self.mouse_old, (mouse["mb_x"], mouse["mb_y"]))
        self.mouse_old = (mouse["mb_x"], mouse["mb_y"])

    self.zoom(mouse["scroll_y"], winsize[1])
    return super().update(
      uniforms,
      mouse,
      view_matrix=self._view_matrix(),
      projection_matrix=self._projection_matrix(winsize),
    )

  # def update(self, uniforms, mouse):
  #   winsize = self.get_uniform_value(uniforms, "iResolution")
  #   if (mouse["mb1_x"] == mouse["mb1_down_x"]) and (
  #     mouse["mb1_y"] == mouse["mb1_down_y"]
  #   ):  # if new click, reinit old position and dont move
  #     self.mouse_old = (mouse["mb1_down_x"], mouse["mb1_down_y"])
  #   else:
  #     self.drag(self.mouse_old, (mouse["mb1_x"], mouse["mb1_y"]), winsize)
  #     self.mouse_old = (mouse["mb1_x"], mouse["mb1_y"])

  #   if (mouse["mb2_down"]):
  #     self.pan()
  #   self.zoom(mouse["scroll_y"], winsize[1])
  #   return super().update(
  #     uniforms,
  #     mouse,
  #     view_matrix=self._view_matrix(),
  #     projection_matrix=self._projection_matrix(winsize),
  #   )
