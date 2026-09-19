import glfw
from OpenGL import GL


def main():
  # Initialize the library
  if not glfw.init():
    return 1
  # Create a windowed mode window and its OpenGL context
  glfw.window_hint(glfw.RESIZABLE, False)
  window = glfw.create_window(640, 480, "Hello World", None, None)
  if not window:
    glfw.terminate()
    return 1

  # Make the window's context current
  glfw.make_context_current(window)
  glfw.set_key_callback(window, key_callback)

  newhope = {"r": 0.0, "dr": 1, "g": 2.0 / 3, "dg": 1, "b": 2.0 / 3, "db": -1}
  newage = glfw.get_time()

  # Loop until the user closes the window
  while not glfw.window_should_close(window):
    # Render here, e.g. using pyOpenGL
    # im guessing doing the draw loop here

    # rainbow temp
    newhope, newage = hopeAndDreams(newhope, newage)
    # Swap front and back buffers
    glfw.swap_buffers(window)

    # Poll for and process events
    glfw.poll_events()

  glfw.terminate()
  return 0


def hopeAndDreams(old, oldT):
  # r,g,b,a,dr,dg,db
  posd = 1
  negd = -1
  new = old
  now = glfw.get_time()
  GL.glClearColor(old["r"], old["g"], old["b"], 1)
  GL.glClear(GL.GL_COLOR_BUFFER_BIT)

  for c in ["r", "g", "b"]:
    tmp = old[c] + old["d" + c] * (now - oldT)
    if tmp < 0:
      new[c] = 0
      new["d" + c] = posd
    elif tmp > 1:
      new[c] = 1
      new["d" + c] = negd
    else:
      new[c] = tmp

  return new, now


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
  main()
