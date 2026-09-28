import numpy as np
import logging

"""
A camera takes a 1D numpy array of uniforms as input and return an updated version
of the input by adding a `view` and `projection` uniforms.
"""


class Camera:
  logger = logging.getLogger(__name__)

  def _projection_matrix(self):
    """To be overriden in child classes"""
    return np.identity(4, dtype=np.float32)

  def _view_matrix(self):
    """To be overriden in child classes"""
    return np.identity(4, dtype=np.float32)

  def get_uniform_value(self, uniforms, name):
    for uniform in uniforms:
      if uniform["name"] == name:
        return uniform["value"]
    return None

  def update(self, uniforms, mouse, view_matrix=None, projection_matrix=None):
    view = {
      "name": "view",
      "value": view_matrix if view_matrix is not None else self._view_matrix(),
      "type": "mat4",
    }
    projection = {
      "name": "projection",
      "value": projection_matrix if projection_matrix is not None else self._projection_matrix(),
      "type": "mat4",
    }
    view_pos = {
      "name": "view_pos",
      "value": np.array([view["value"][0:3, 3]]),
      "type": "vec3",
    }

    # check for no uniform redefinition
    for uniform in uniforms:
      if uniform["name"] in ("view", "projection", "view_pos"):
        self.logger.error('"%s" is a reserved uniform symbol', uniform["name"])
        exit(1)

    # add view, projection, view_pos uniforms
    return np.concatenate((uniforms, np.array([view, projection, view_pos])))
