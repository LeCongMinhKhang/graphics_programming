from src.scene import Scene, AppOgl
from src.light import Light
import src.transform as transform

import numpy as np
from types import MethodType


def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "phong"
    self.color_mode = "texture"

    # lights
    radius = 60.0
    height = 50.0
    nb_lights = 3
    lights = [
      Light(
        position=(
          radius * np.cos(i * 2 * np.pi / nb_lights),
          height,
          np.sin(i * 2 * np.pi / nb_lights),
        ),
        color=(1, 1, 1),
        intensity=1 / nb_lights,
      )
      for i in range(nb_lights)
    ]
    self.add_lights(lights=lights)

    # ground
    obj, _ = self.add_object("rectangle", label="ground")
    self.update_object(
      obj,
      program_name="phong",
      textures={"image": "inputs/textures/grass.jpg"},
      material="matte",
      model_matrix=transform.translate(10.0, -0.001, 0.0)
      @ transform.rotate((0, 1.0, 0.0), 90)
      @ transform.rotate((1.0, 0.0, 0.0), -90)
      @ transform.scale(45),
      color_mode="texture",
    )

    # castle
    obj, _ = self.add_object("file", "inputs/obj/hogwarts/Hogwarts.obj", label="castle")
    self.update_object(
      obj,
      program_name="phong",
      # textures={"image": "inputs/textures/rock.png"},
      model_matrix=transform.translate(10.0, 0.0, 0.0) @ transform.scale(0.001),
      color_mode="color",
      material="rubber",
    )

    # trees
    obj, _ = self.add_object("file", "inputs/obj/maple_tree/MapleTree.obj")
    self.update_object(
      obj,
      program_name="phong",
      model_matrix=transform.translate(0.0, 0.0, -1.0) @ transform.scale(0.1),
      color_mode="color",
      material="matte",
    )

    # penguins
    obj, _ = self.add_object("file", "inputs/obj/penguin/PenguinBaseMesh.obj", label="penguin")
    self.update_object(
      obj,
      program_name="phong",
      textures={"image": "inputs/obj/penguin/Penguin Diffuse Color.png"},
      model_matrix=transform.translate(1.0, 0.0, 5.0) @ transform.rotate((0, 1, 0), 30),
      color_mode="texture",
      material="skin",
    )

    obj, _ = self.add_object("file", "inputs/obj/penguin/PenguinBaseMesh.obj", label="penguin")
    self.update_object(
      obj,
      program_name="phong",
      textures={"image": "inputs/obj/penguin/Penguin Diffuse Color.png"},
      model_matrix=transform.translate(-1.0, 0.0, 3.0) @ transform.rotate((0, 1, 0), 0),
      color_mode="texture",
      material="skin",
    )

    obj, _ = self.add_object("file", "inputs/obj/penguin/PenguinBaseMesh.obj", label="penguin")
    self.update_object(
      obj,
      program_name="phong",
      textures={"image": "inputs/obj/penguin/Penguin Diffuse Color.png"},
      model_matrix=transform.rotate((0, 1, 0), 180),
      color_mode="texture",
      material="skin",
    )

  name = "castle"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
