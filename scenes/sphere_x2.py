from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "interpolation"

    sphere1, _ = self.add_object("sphere")
    self.update_object(
      sphere1,
      program_name="flat",
      model_matrix=transform.translate(-1, 0, 0),
    )
    sphere2, _ = self.add_object("sphere")
    self.update_object(
      sphere2,
      program_name="interpolation",
      model_matrix=transform.translate(1, 0, 0),
    )

  name = "sphere x2"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
