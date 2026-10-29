from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType
from src.parsefile import parseFile
from src.light import Light

def scenes(gl_app: AppOgl):
  scenes = {}

  def build_scene(self):
    self.program_name = "phong"

    tableId, _ = self.add_object(
      "table", data_f=lambda: parseFile(path="inputs/obj/Table And Chairs.obj")
    )
    self.update_object(
      tableId,
      program_name="phong",
      model_matrix=transform.scale(1/16, 1/16, 1/16),
    )
    teaId, _ = self.add_object(
      "tea", data_f=lambda: parseFile(path="inputs/obj/utahTeaPot.obj")
    )
    self.update_object(
      teaId,
      program_name="phong",
      model_matrix=transform.translate(y=21/8)@transform.scale(3/16, 3/16, 3/16),
    )
    planeId, _ = self.add_object(
      "plane", data_f=lambda: parseFile(path="inputs/obj/swordFishmk2.obj")
    )
    self.update_object(
      planeId,
      program_name="phong",
      model_matrix=transform.translate(z=7,y = -1) @ transform.scale(16/3)@ transform.rotate((0,0,1),angle = 15.0),
    )
    lights = [
      Light(position=(0.0, 10.0, 0.0), color=(1, 1, 1), intensity=1),
    ]
    self.add_lights(lights=lights)

  name = "tea_and_table"
  scene = Scene(gl_app)
  scene.build_scene = MethodType(build_scene, scene)
  scenes[name] = scene

  return scenes
