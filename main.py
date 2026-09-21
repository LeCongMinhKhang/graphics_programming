from src import parsefile
import argparse
from inputs import triangle,trapezoid,rectangle,star,n_gon,arrow


parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default=None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default=None)
parser.add_argument("--print3d", action='store_true', help="Prints in 3d coords")
args = parser.parse_args()

file_path = args.file
scene_path = args.scene
print_3d = args.print3d

def entry():
  if file_path is None and scene_path is None:
    parser.print_help()
    return

  elif file_path is not None:
    print(parsefile.parseFile(file_path))
  elif scene_path is not None:
    match scene_path:
      case "triangle":
        pprint(triangle.generate())
      case "rectangle":
        pprint(rectangle.generate())
      case "pentagon":
        pprint(n_gon.generate("pentagon"))
      case "hexagon":
        pprint(n_gon.generate("hexagon"))
      case "circle":
        pprint(n_gon.generate("circle"))
      case "ellipse":
        pprint(n_gon.generate("ellipse"))
      case "trapezoid":
        pprint(trapezoid.generate())
      case "star":
        pprint(star.generate())
      case "arrow":
        pprint(arrow.generate())
    # print(parsefile.parseFile(file_path))

# paste this string to desmos calc
def pprint(obj):
  res = []
  if(print_3d):
    for v in obj["v"]:
      res.append(f"({v[0]:.6f},{v[1]:.6f},{v[2]:.6f})")
  else:
    for v in obj["v"]:
      res.append(f"({v[0]:.6f},{v[1]:.6f})")

  print(",".join(res))

if __name__ == "__main__":
  entry()
