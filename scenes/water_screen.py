from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "water"
    self.color_mode = "color"

    self.create_program(
      self.program_name,
      "./shaders/lighting.vert",
      "./shaders/water.frag",
    )
    # // no light uniforms!
    obj, _ = self.add_object("rectangle")
    self.update_object(
      obj,
      program_name=self.program_name,
      model_matrix=transform.identity(),
    )

  name = "water screen"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
