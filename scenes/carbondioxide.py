from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType
from src.shape_generators.three_dee import cube, uv_sphere, cylinder, n_gon_pyramid, torus, surface
import numpy as np


def scenes(gl_app: AppOgl):
  scenes = {}
  def build_scene(self):
    self.program_name = "interpolation"
    self.gl_app.create_program("interpolation")

    # Carbon
    carbonId, _ = self.add_object("Carbon", data=uv_sphere.generate(color="hex", hex=0x777777))
    self.update_object(carbonId, model_matrix=transform.identity(), program_name="interpolation")


    # Oxygen1
    obj = uv_sphere.generate(color="hex",size=0.75, hex=0xff0000)
    oxygen1Id, _ = self.add_object("Oxide", data=obj)
    self.update_object(oxygen1Id, model_matrix=transform.translate(2,0,0), program_name="interpolation")
    # Oxygen2
    oxygen2Id, _ = self.add_object("Oxide", data=obj)
    self.update_object(oxygen2Id, model_matrix=transform.translate(-2,0,0), program_name="interpolation")

    # Bond1
    # print(transform.translate(0,0.15,0))
    # print(transform.rotate((0,1,0),angle = 90))
    # print(transform.translate(0,0.15,0)*transform.rotate((0,1,0),angle = 90))
    obj = cylinder.generate(color="hex",radius=0.1,height=4, hex=0xffffff)
    bond1Id, _ = self.add_object("Bond", data=obj)
    self.update_object(bond1Id, model_matrix=transform.translate(0,0.15,0) @ transform.rotate((0,1,0),angle = 90), program_name="interpolation")
    bond2Id, _ = self.add_object("Bond", data=obj)
    self.update_object(bond2Id, model_matrix=transform.translate(0,-0.15,0) @ transform.rotate((0,1,0),angle = 90), program_name="interpolation")

    
  name = "!!carbondioxide"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
