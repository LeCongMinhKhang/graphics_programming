import src.tkwindow
from src.camera.trackball import Trackball

import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
  src.tkwindow.display(camera=Trackball)
