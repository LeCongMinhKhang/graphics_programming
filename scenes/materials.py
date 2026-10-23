from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType

import numpy as np


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "phong"

    # self.add_material

    materials = [
      "default",
      "shiny",
      "matte",
      "rubber",
      "metal",
      "gold",
      "copper",
      "ceramic",
      "glass",
      "skin",
    ]
    n = len(materials)
    x_min, x_max = -2, 2
    size = (x_max - x_min) / n
    x_coord = np.linspace(x_min, x_max, n, endpoint=False)

    for y, program in zip(np.array([1, -1]) * size / 2, ("phong", "goureaud")):
      for x, material in zip(x_coord, materials):
        obj, _ = self.add_object("sphere")
        self.update_object(
          obj,
          program_name=program,
          model_matrix=transform.translate(x + size / 2, y, 0) @ transform.scale(size / 2),
          material=material,
        )

    self.add_lights(2)

  name = "materials"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
