from src import parsefile
import argparse
import logging


parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default=None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default=None)
parser.add_argument("--debug", action="store_true", help="Enable debug logging")

args = parser.parse_args()

logging.basicConfig(
  level=logging.DEBUG if args.debug else logging.INFO,
  format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)
file_path = args.file
scene_path = args.scene

logger.info("Starting app")


def entry():
  if file_path is None and scene_path is None:
    parser.print_help()
    return

  elif file_path is not None:
    print(parsefile.parseFile(file_path))


if __name__ == "__main__":
  entry()
