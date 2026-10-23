from src.tkwindow import AppOgl


class Scene:
  def __init__(self, gl_app: AppOgl):
    self.program_name = ""
    self.color_mode = ""
    self.gl_app = gl_app

  def add_object(self, name, filePath=None, data=None):
    """Returns (obj_id, program_name)"""
    return self.gl_app.reserve_object(obj_name=name, filePath=filePath, data=data)

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

  def add_lights(self, nb_lights, uniforms=None):
    return self.gl_app.update_lights(nb_lights=nb_lights, uniforms=uniforms)
