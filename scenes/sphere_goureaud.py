from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType
import numpy as np


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "goureaud"

    sphere, _ = self.add_object("sphere")
    self.update_object(sphere, program_name=self.program_name, model_matrix=np.identity(4))

  name = "sphere goureaud"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
