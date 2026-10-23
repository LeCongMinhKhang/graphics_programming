from src.scene import Scene, AppOgl
import src.transform as transform
from src.shape_generators.three_dee import surface

from types import MethodType
import numpy as np


def D3_function(x, y):
  return np.cos(np.sqrt(x**2 + y**2))


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "phong"

    data_f = lambda: surface.generate(func=D3_function, n=3)

    obj, _ = self.add_object("function surface", data_f=data_f)
    self.update_object(
      obj,
      program_name=self.program_name,
      model_matrix=transform.identity(),
    )

  name = "function surface"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
