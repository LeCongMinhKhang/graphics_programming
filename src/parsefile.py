from pathlib import Path
import logging

import src.obj_loader as obj_loader
import src.ply_loader as ply_loader

logger = logging.getLogger(__name__)


def parseFile(path):
  ext = Path(path).suffix.lower()
  match ext:
    case ".obj":
      return obj_loader.parseFile(path)
    case ".ply":
      return ply_loader.parse(path)
    case _:
      logger.error('extension "%s" not recognized', ext)
      exit(1)
