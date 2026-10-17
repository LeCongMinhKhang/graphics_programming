from src.scene import Scene, AppOgl
import src.transform as transform
from src.shape_generators.three_dee import cube
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "interpolation"
    self.gl_app.create_program("interpolation")
    self.color_mode = "texture"

    obj = cube.generate()
    
    objId, _ = self.add_object(name, data=obj)
    self.update_object(
      objId,
      program_name="interpolation",
      textures={"image": "inputs/textures/test_texture.jpg"},
      color_mode="texture",
    )

  name = "!shape_texture_test"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
