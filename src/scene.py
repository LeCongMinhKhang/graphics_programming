from src.tkwindow import AppOgl


class Scene:
  def __init__(self, gl_app: AppOgl):
    # self.name = ""
    self.program_name = ""
    self.gl_app = gl_app

  def add_object(self, name):
    """Returns (obj_id, program_name)"""
    return self.gl_app.reserve_object(name)

  def update_object(
    self,
    obj_id,
    program_name=None,
    model_matrix=None,
    mode=None,
    static_uniforms=None,
  ):
    return self.gl_app.update_object(
      obj_id=obj_id,
      program=program_name,
      mode=mode,
      model_matrix=model_matrix,
      static_uniforms=static_uniforms,
    )
