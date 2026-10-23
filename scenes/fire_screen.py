from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "fire"
    self.color_mode = "color"

    self.create_program(
      self.program_name,
      "./shaders/lighting.vert",
      "./shaders/fire.frag",
    )

    obj, _ = self.add_object("rectangle")
    self.update_object(
      obj,
      program_name=self.program_name,
    )

  name = "fire screen"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
