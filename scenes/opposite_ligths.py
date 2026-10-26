from src.scene import Scene, AppOgl
import src.transform as transform
from src.light import Light
from types import MethodType

import numpy as np


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "phong"
    self.color_mode = "color"

    # self.create_program(
    #   self.program_name,
    #   "./shaders/lighting.vert",
    #   "./shaders/water.frag",
    # )

    # objects
    obj, _ = self.add_object("sphere")
    self.update_object(
      obj,
      program_name=self.program_name,
      model_matrix=transform.identity(),
    )

    # lights
    lights = [
      Light(position=(10, 0.0, 0.0), color=(1, 1, 1), intensity=1),
      Light(position=(-10, 0.0, 0.0), color=(1, 1, 1), intensity=1),
    ]
    self.add_lights(lights=lights)

  name = "opposite lights"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes


# from src.scene import Scene, AppOgl
# import src.transform as transform
# from src.light import Light
# from types import MethodType

# import numpy as np


# def scenes(gl_app: AppOgl):
#   scenes = {}

#   def build_scene(self):
#     self.program_name = "phong"
#     self.color_mode = "color"

#     # self.create_program(
#     #   self.program_name,
#     #   "./shaders/lighting.vert",
#     #   "./shaders/water.frag",
#     # )

#     # objects
#     obj, _ = self.add_object("sphere")
#     self.update_object(
#       obj,
#       program_name=self.program_name,
#       model_matrix=transform.identity(),
#     )

#     # lights
#     lights = {
#       "name": "lights",
#       "type": "lights",
#       "value": np.array(
#         [
#           Light(position=(10, 0.0, 0.0), color=(1, 1, 1), intensity=1),
#           Light(position=(-10, 0.0, 0.0), color=(1, 1, 1), intensity=1),
#         ],
#       ),
#     }
#     num_lights = {"name": "num_lights", "type": "int", "value": lights["value"].shape[0]}

#     # material / ambient (static: they don't change between frames)
#     ambient_color = {
#       "name": "ambient_color",
#       "type": "vec3",
#       "value": np.array([1, 1, 1], dtype=np.float32),
#     }
#     k_ambient = {"name": "k_ambient", "type": "float", "value": 0.1}
#     k_diffuse = {"name": "k_diffuse", "type": "float", "value": 1.0}
#     k_specular = {"name": "k_specular", "type": "float", "value": 0.5}
#     shininess = {"name": "shininess", "type": "float", "value": 32.0}

#     uniforms = np.array(
#       [lights, num_lights, ambient_color, k_ambient, k_diffuse, k_specular, shininess],
#       dtype=object,
#     )
#     self.add_lights(num_lights["value"], uniforms)

#   name = "opposite lights"
#   scene = Scene(gl_app)
#   scene.build_scene = MethodType(build_scene, scene)
#   scenes[name] = scene

#   return scenes
