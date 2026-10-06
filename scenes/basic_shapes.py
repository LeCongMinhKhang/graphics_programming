from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}
  names = [
    "triangle",
    "rectangle",
    "pentagon",
    "hexagon",
    "circle",
    "ellipse",
    "trapezoid",
    "star",
    "arrow",
    "cube",
    "cylinder",
    "prism",
    "truncated_cone",
    "cone",
    "tetrahedron",
    "surface",
    "sphere",
    "torus",
  ]

  def make_build_scene(name):
    def build_scene(self):
      obj_id, _ = self.add_object(name)
      self.program_name = "interpolation"
      self.update_object(obj_id, model_matrix=transform.identity(), program_name=self.program_name)

    return build_scene

  for name in names:
    scene = Scene(gl_app)
    scene.build_scene = MethodType(make_build_scene(name), scene)
    scenes[name] = scene

  return scenes
