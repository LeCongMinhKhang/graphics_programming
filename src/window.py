from OpenGL import GL
import numpy as np
import glfw
import time
import logging

from src.pipeline import Pipeline
from src.camera.camera import Camera

logger = logging.getLogger(__name__)


def display(data, window_size=(640, 480), camera=Camera):

  # Mouse state, keyed simply
  mouse = {
    "x": 0.0,
    "y": 0.0,
    "mb1_x": 0.0,
    "mb1_y": 0.0,  # current position (GL coords, y-up)
    "mb1_down_x": 0.0,
    "mb1_down_y": 0.0,  # position at last press
    "mb1_down": False,
    "scroll_x": 0.0,
    "scroll_y": 0.0,
    "scroll_delta_x": 0.0,
    "scroll_delta_y": 0.0,
  }

  def cursor_pos_callback(window, xpos, ypos):
    _, height = glfw.get_window_size(window)
    mouse["x"] = xpos
    mouse["y"] = height - ypos
    if mouse["mb1_down"]:  # update mb1 position only when mb1 is pressed
      mouse["mb1_x"] = xpos
      mouse["mb1_y"] = height - ypos  # flip so y=0 is bottom

  def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
      if action == glfw.PRESS:
        mouse["mb1_down"] = True
        mouse["mb1_down_x"] = mouse["x"]
        mouse["mb1_down_y"] = mouse["y"]
        mouse["mb1_x"] = mouse["x"]
        mouse["mb1_y"] = mouse["y"]
      elif action == glfw.RELEASE:
        mouse["mb1_down"] = False

  def scroll_callback(window, xoffset, yoffset):
    mouse["scroll_x"] += xoffset
    mouse["scroll_y"] += yoffset
    mouse["scroll_delta_x"] = xoffset
    mouse["scroll_delta_y"] = yoffset

  # Initialize the library
  if not glfw.init():
    return 1
  # Create a windowed mode window and its OpenGL context
  glfw.window_hint(glfw.RESIZABLE, False)
  window = glfw.create_window(
    window_size[0], window_size[1], "Computer Graphics Viewer", None, None
  )
  if not window:
    glfw.terminate()
    return 1

  # Make the window's context current
  glfw.make_context_current(window)

  GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test
  GL.glDepthFunc(GL.GL_LESS)  # default; fragment passes if depth < stored depth

  # GL.glEnable(GL.GL_CULL_FACE)  # face culling enabled
  # GL.glCullFace(GL.GL_BACK)  # cull back faces, render only front faces
  GL.glFrontFace(GL.GL_CCW)  # winding order: counter clockwise indexing

  # show and resize the window to fix the initial resize of tiling display manager
  glfw.show_window(window)
  glfw.set_window_size(window, window_size[0], window_size[1])

  glfw.set_key_callback(window, key_callback)
  # after creating the window:
  glfw.set_cursor_pos_callback(window, cursor_pos_callback)
  glfw.set_mouse_button_callback(window, mouse_button_callback)
  glfw.set_scroll_callback(window, scroll_callback)

  pipeline = Pipeline()

  default_static_uniforms = np.array(
    [
      {
        "name": "iResolution",
        "value": np.array([window_size[0], window_size[1]], dtype=np.float32),
        "type": "vec2",
      },
    ]
  )

  entries = [
    "vertices",
    "normals",
    "colors",
    "vert_shader",
    "frag_shader",
    "indices",
    "mode",
    "static_uniforms",
    "model_matrix",
    "vao_id",
  ]
  for obj in data:
    obj_data = {}
    for entry in entries:
      if entry in obj.keys():
        obj_data[entry] = obj[entry]
      else:
        obj_data[entry] = None
    pipeline.add_object(
      vertices=obj_data["vertices"],
      normals=obj_data["normals"],
      colors=obj_data["colors"],
      vert_shader=obj_data["vert_shader"],
      frag_shader=obj_data["frag_shader"],
      indices=obj_data["indices"],
      mode=obj_data["mode"],
      static_uniforms=np.concatenate(
        (
          default_static_uniforms,
          (
            obj_data["static_uniforms"] if obj_data["static_uniforms"] is not None else np.array([])
          ),
        )
      ),
      model_matrix=obj_data["model_matrix"],
      vao_id=obj_data["vao_id"],
    )
  logger.debug("All objects added")

  cam = camera()
  logger.debug("Camera initialized")

  start_time = time.time()
  # Loop until the user closes the window
  while not glfw.window_should_close(window):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    # Render here, e.g. using pyOpenGL
    uniforms = np.array(
      [
        {
          "name": "iTime",
          "value": time.time() - start_time,
          "type": "float",
        },
        {
          "name": "iMouse",
          "value": np.array(
            [mouse["mb1_x"], mouse["mb1_y"], mouse["mb1_down_x"], mouse["mb1_down_y"]],
            dtype=np.float32,
          ),
          "type": "vec4",
        },
      ]
    )
    uniforms = cam.update(uniforms=np.concatenate((default_static_uniforms, uniforms)), mouse=mouse)

    pipeline.draw(uniforms)

    glfw.swap_buffers(window)  # Swap front and back buffers
    glfw.poll_events()  # Poll for and process events

  pipeline.destroy()
  glfw.terminate()
  return 0


def key_callback(window, key, scancode, action, mods):
  if action == 1:
    match key:
      case glfw.KEY_W:
        print("Move forwards")
      case glfw.KEY_A:
        print("Move left")
      case glfw.KEY_S:
        print("Move back")
      case glfw.KEY_D:
        print("Move right")
      case glfw.KEY_SPACE:
        print("Move up")
      case glfw.KEY_LEFT_CONTROL:
        print("Move down")
      case n:
        if n >= glfw.KEY_0 and n <= glfw.KEY_9:
          print(f"Num key {n - glfw.KEY_0}")


if __name__ == "__main__":
  display()
