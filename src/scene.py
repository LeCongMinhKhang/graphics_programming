from src.tkwindow import AppOgl
import numpy as np


class Scene:
  def __init__(self, gl_app: AppOgl):
    self.program_name = "interpolation"
    self.color_mode = "color"
    self.gl_app = gl_app

  def add_object(self, name: str, filePath: str = None, data_f: lambda: dict = None):
    """Returns (obj_id, program_name)"""
    return self.gl_app.reserve_object(obj_name=name, filePath=filePath, data_f=data_f)

  def update_object(
    self,
    obj_id,
    program_name=None,
    model_matrix=None,
    mode=None,
    static_uniforms=None,
    textures=None,
    color_mode=None,
    material=None,
  ):
    return self.gl_app.update_object(
      obj_id=obj_id,
      program=program_name,
      mode=mode,
      model_matrix=model_matrix,
      static_uniforms=static_uniforms,
      textures=textures,
      color_mode=color_mode,
      material=material,
    )

  def create_program(self, name, vert_shader=None, frag_shader=None):
    return self.gl_app.create_program(name=name, vert_shader=vert_shader, frag_shader=frag_shader)

  def add_lights(self, nb_lights=None, lights=None):
    uniforms = None
    if lights is not None:
      lights = np.array(lights)
      nb_lights = lights.shape[0]
      uniforms = np.array(
        [
          {
            "name": "lights",
            "type": "lights",
            "value": lights,
          },
          {"name": "num_lights", "type": "int", "value": nb_lights},
        ]
      )
    return self.gl_app.update_lights(nb_lights=nb_lights, uniforms=uniforms)
