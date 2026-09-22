from src import parsefile
import argparse
from inputs.two_dee import triangle,trapezoid,rectangle,star,n_gon,arrow
from inputs.three_dee import cube, cylinder, n_gon_piramid, surface, uv_sphere, torus
import numpy as np 

parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default=None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default=None)
parser.add_argument("--print3d", action='store_true', help="Prints in 3d coords")
parser.add_argument("--outputfile", action='store_true', help="Output to file")
args = parser.parse_args()

file_path = args.file
scene_path = args.scene
print_3d = args.print3d
outputfile = args.outputfile

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
      # 3d
      case "cube":
        pprint(cube.generate())
      case "cylinder":
        pprint(cylinder.generate())
      case "prism":
        pprint(cylinder.generate(1.0,3))
      case "truncated_cone":
        pprint(cylinder.generate(0.5))
      case "cone":
        pprint(n_gon_piramid.generate("cone"))
      case "tetrahedron":
        pprint(n_gon_piramid.generate("tetrahedron"))
      case "surface":
        pprint(surface.generate(lambda x,y: x**2 + y**2,5,5,1))
      case "sphere":
        pprint(uv_sphere.generate())
      case "torus":
        pprint(torus.generate(n=8))
    # print(parsefile.parseFile(file_path))

# paste this string to desmos calc
def pprint(obj):
  index = 0
  res = []
  if(print_3d):
    for v in obj["v"]:
      res.append(f"P_{"{"+str(index)+"}"} = ({v[0]:.6f},{v[1]:.6f},{v[2]:.6f})")
      index += 1
  else:
    for v in obj["v"]:
      res.append(f"P_{"{"+str(index)+"}"} = ({v[0]:.6f},{v[1]:.6f})")
      index += 1
  for f in obj["f"]:
    res.append(f"\\operatorname{{triangle}}\\left(P_{{{f[0][0]}}},P_{{{f[0][1]}}},P_{{{f[0][2]}}}\\right)")
  if outputfile:
    with open("output.txt", "w", encoding="utf-8") as file:
      file.write("\n".join(res))
  else:
    print("\n".join(res))

if __name__ == "__main__":
  entry()
