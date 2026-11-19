from pathlib import Path
import logging

import src.obj_loader as obj_loader
import src.ply_loader as ply_loader
import src.shape_generators.tools as tools

logger = logging.getLogger(__name__)


def parseFile(path):
  ext = Path(path).suffix.lower()
  match ext:
    case ".obj":
      data = obj_loader.parseFile(path)
    case ".ply":
      data = ply_loader.parse(path)
    case _:
      logger.error('extension "%s" not recognized', ext)
      exit(1)

  if data["colors"] is None and data["uvs"] is None:
    tools.normalColoring(data)
  return data
