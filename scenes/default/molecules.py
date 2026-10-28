from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType
from src.shape_generators.three_dee import uv_sphere, cylinder
from src.light import Light


def scenes(gl_app: AppOgl):
  scenes = {}
  light_intensity = 3 / 5
  lights = [
    Light((5, 5, 5), intensity=light_intensity),
    Light((-5, 5, 5), intensity=light_intensity),
    Light((5, -5, 5), intensity=light_intensity),
    Light((-5, -5, 5), intensity=light_intensity),
    Light((5, 5, -5), intensity=light_intensity),
    Light((-5, 5, -5), intensity=light_intensity),
    Light((5, -5, -5), intensity=light_intensity),
    Light((-5, -5, -5), intensity=light_intensity),
  ]

  def build_scene_co2(self):
    self.program_name = "phong"

    # Carbon
    carbonId, _ = self.add_object(
      "Carbon", data_f=lambda: uv_sphere.generate(color="hex", hex=0x333333)
    )
    self.update_object(
      carbonId,
      model_matrix=transform.identity(),
      program_name=self.program_name,
      material="shiny",
    )

    # Oxygen1
    obj = lambda: uv_sphere.generate(color="hex", size=0.75, hex=0xFF0000)
    oxygen1Id, _ = self.add_object("Oxide", data_f=obj)
    self.update_object(
      oxygen1Id,
      model_matrix=transform.translate(2, 0, 0),
      program_name=self.program_name,
      material="shiny",
    )
    # Oxygen2
    oxygen2Id, _ = self.add_object("Oxide", data_f=obj)
    self.update_object(
      oxygen2Id,
      model_matrix=transform.translate(-2, 0, 0),
      program_name=self.program_name,
      material="shiny",
    )

    # Bond1
    obj = lambda: cylinder.generate(color="hex", radius=0.1, height=4, hex=0xFFFFFF)
    bond1Id, _ = self.add_object("Bond", data_f=obj)
    self.update_object(
      bond1Id,
      model_matrix=transform.translate(0, 0.15, 0) @ transform.rotate((0, 1, 0), angle=90),
      program_name=self.program_name,
      material="rubber",
    )
    bond2Id, _ = self.add_object("Bond", data_f=obj)
    self.update_object(
      bond2Id,
      model_matrix=transform.translate(0, -0.15, 0) @ transform.rotate((0, 1, 0), angle=90),
      program_name=self.program_name,
      material="rubber",
    )

    # lights
    self.add_lights(lights=lights)

  def build_scene_h2o(self):
    self.program_name = "phong"

    # Oxygen
    oxygenId, _ = self.add_object(
      "Monoxide", data_f=lambda: uv_sphere.generate(color="hex", hex=0xFF0000)
    )
    self.update_object(
      oxygenId, model_matrix=transform.identity(), program_name=self.program_name, material="shiny"
    )

    # Hidrogen1
    obj = lambda: uv_sphere.generate(color="hex", size=0.75, hex=0xFFFFFF)
    oxygen1Id, _ = self.add_object("Dihydrogen", data_f=obj)
    self.update_object(
      oxygen1Id,
      model_matrix=transform.rotate((0, 1, 0), angle=-37.775) @ transform.translate(2, 0, 0),
      program_name=self.program_name,
      material="shiny",
    )
    # Hidrogen2
    oxygen2Id, _ = self.add_object("Dihydrogen", data_f=obj)
    self.update_object(
      oxygen2Id,
      model_matrix=transform.rotate((0, 1, 0), angle=37.775) @ transform.translate(-2, 0, 0),
      program_name=self.program_name,
      material="shiny",
    )

    # Bond1
    obj = lambda: cylinder.generate(color="hex", radius=0.1, height=2, hex=0xFFFFFF)
    bond1Id, _ = self.add_object("BondH2o", data_f=obj)
    self.update_object(
      bond1Id,
      model_matrix=transform.rotate((0, 1, 0), angle=37.775)
      @ transform.translate(-1, 0, 0)
      @ transform.rotate((0, 1, 0), angle=90),
      program_name=self.program_name,
      material="rubber",
    )
    bond2Id, _ = self.add_object("BondH2o", data_f=obj)
    self.update_object(
      bond2Id,
      model_matrix=transform.rotate((0, 1, 0), angle=-37.775)
      @ transform.translate(1, 0, 0)
      @ transform.rotate((0, 1, 0), angle=90),
      program_name=self.program_name,
      material="rubber",
    )

    # lights
    self.add_lights(lights=lights)

  scene_co2 = Scene(gl_app)
  scene_co2.build_scene = MethodType(build_scene_co2, scene_co2)
  scenes["CO2"] = scene_co2
  scene_h2o = Scene(gl_app)
  scene_h2o.build_scene = MethodType(build_scene_h2o, scene_h2o)
  scenes["H2O"] = scene_h2o

  return scenes
