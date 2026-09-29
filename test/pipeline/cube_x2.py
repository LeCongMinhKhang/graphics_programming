import sys
import os

_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_SAMPLE_DIR))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)

import src.window  # noqa: E402
from src.camera.trackball import Trackball  # noqa: E402
from cube import setup  # noqa: E402
import src.transform  # noqa: E402


if __name__ == "__main__":
  cube = setup()
  data = [cube[0], cube[0].copy()]
  data[1]["model_matrix"] = src.transform.translate(1, 0, 0)

  src.window.display(data, camera=Trackball)
