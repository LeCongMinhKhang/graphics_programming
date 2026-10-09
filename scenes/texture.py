from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "interpolation"
    self.color_mode = "texture"

    obj, _ = self.add_object("file", "inputs/obj/swordFishmk2.obj")
    self.update_object(
      obj,
      program_name="interpolation",
      textures={"image": "inputs/textures/rock.png"},
      color_mode="texture",
    )

  name = "plane texture"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
