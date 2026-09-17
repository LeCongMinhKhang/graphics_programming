import sys
import os

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

from src.pipeline import Pipeline
import OpenGL.GL as GL
import numpy as np
import glfw

if __name__ == "__main__":
  glfw.init()
  window = glfw.create_window(800, 600, "demo", None, None)
  if not window:
    glfw.terminate()
    raise RuntimeError("Failed to create window")

  glfw.make_context_current(window)

  vertices = np.array(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32
  )
  colors = np.array([[1, 0, 0], [0, 1, 0]] * int(vertices.shape[0] / 2), dtype=np.float32)
  normals = np.array([[0, 0, 1]] * vertices.shape[0], dtype=np.float32)
  # vert_shader = "./shaders/flat.vert"
  # frag_shader = "./shaders/flat.frag"
  vert_shader = "./shaders/interp.vert"
  frag_shader = "./shaders/interp.frag"
  indices = np.array([0, 1, 2, 4, 5, 0], dtype=np.int32)

  renderer = Pipeline()
  renderer.load_data(
    vertices, normals, colors, vert_shader, frag_shader, indices=indices, mode=GL.GL_TRIANGLES
  )

  while not glfw.window_should_close(window):
    GL.glClearColor(0.1, 0.1, 0.1, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    renderer.draw()
    glfw.swap_buffers(window)
    glfw.poll_events()
  # while not glfw.window_should_close(window):
  #   renderer.draw()
  #   glfw.swap_buffers(window)

  glfw.terminate()
