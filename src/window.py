import glfw
from OpenGL import GL
from src.pipeline import Pipeline
import numpy as np


def display(data, window_size=(640, 480)):
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

  # show and resize the window to fix the initial resize of tiling display manager
  glfw.show_window(window)
  glfw.set_window_size(window, window_size[0], window_size[1])

  glfw.set_key_callback(window, key_callback)

  pipeline = Pipeline()

  default_uniforms = np.array(
    [
      {
        "name": "iResolution",
        "value": np.array([window_size[0], window_size[1]], dtype=np.int32),
        "type": "ivec2",
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
    "static_uniforms",
    "mode",
    "vao_id",
  ]
  for object in data:
    obj_data = {}
    for entry in entries:
      if entry in object.keys():
        obj_data[entry] = object[entry]
      else:
        obj_data[entry] = None
    pipeline.load_data(
      obj_data["vertices"],
      obj_data["normals"],
      obj_data["colors"],
      obj_data["vert_shader"],
      obj_data["frag_shader"],
      obj_data["indices"],
      np.concatenate(
        (
          default_uniforms,
          (
            obj_data["static_uniforms"] if obj_data["static_uniforms"] is not None else np.array([])
          ),
        )
      ),
      obj_data["mode"],
      obj_data["vao_id"],
    )

  # Loop until the user closes the window
  while not glfw.window_should_close(window):
    GL.glClearColor(0, 0, 0, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    # Render here, e.g. using pyOpenGL
    pipeline.draw()

    glfw.swap_buffers(window)  # Swap front and back buffers
    glfw.poll_events()  # Poll for and process events

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
