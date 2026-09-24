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
    add_view = True
    add_projection = True
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

    # update view and projection entries if they already exist in uniforms array
    for i, uniform in enumerate(uniforms):
      if uniform["name"] == "view":
        if not add_view:
          self.logger.error('At least 2 entries for "view" uniform')
          exit(1)
        uniform[i] = view
        add_view = False
      if uniform["name"] == "projection":
        if not add_projection:
          self.logger.error('At least 2 entries for "projection" uniform')
          exit(1)
        uniform[i] = projection
        add_projection = False

    # add view and projection uniforms if they are not already in uniforms array
    uniforms_to_add = []
    if add_view:
      uniforms_to_add.append(view)
    if add_projection:
      uniforms_to_add.append(projection)
    return np.concatenate((uniforms, np.array(uniforms_to_add)))
