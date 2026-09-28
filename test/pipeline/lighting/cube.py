import sys
import os
import numpy as np

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SAMPLE_DIR)))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window  # noqa: E402 (disabling ruff warning)
from src.camera.trackball import Trackball  # noqa: E402
from src.light import Light  # noqa: E402
import src.transform  # noqa: E402
from test.pipeline.cube import setup  # noqa: E402

if __name__ == "__main__":
  data = setup()

  lights = {
    "name": "lights",
    "type": "lights",
    "value": np.array([Light(position=(10, 10, 10), color=(1, 0, 0), intensity=1)]),
  }
  num_lights = {"name": "num_lights", "type": "int", "value": lights["value"].shape[0]}

  # material / ambient (static: they don't change between frames)
  ambient_color = {
    "name": "ambient_color",
    "type": "vec3",
    "value": np.array([0.1, 0.1, 0.1], dtype=np.float32),
  }
  k_ambient = {"name": "k_ambient", "type": "float", "value": 1.0}
  k_diffuse = {"name": "k_diffuse", "type": "float", "value": 1.0}
  k_specular = {"name": "k_specular", "type": "float", "value": 0.5}
  shininess = {"name": "shininess", "type": "float", "value": 32.0}

  data[0]["static_uniforms"] = np.array(
    [lights, num_lights, ambient_color, k_ambient, k_diffuse, k_specular, shininess],
    dtype=object,
  )
  data[0]["vert_shader"] = "shaders/light.vert"
  data[0]["frag_shader"] = "shaders/phong.frag"
  src.window.display(data, camera=Trackball)
