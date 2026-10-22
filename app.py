import src.tkwindow
from src.camera.trackball import Trackball

import logging
import argparse

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--init_scene", type=str, help="Init with scene name", default=None)
args = parser.parse_args()

init_scene = args.init_scene

if __name__ == "__main__":
  src.tkwindow.display(init_scene=init_scene, camera=Trackball)
