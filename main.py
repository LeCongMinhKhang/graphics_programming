from src import parsefile
import argparse


parser = argparse.ArgumentParser(description="3D viewer")
parser.add_argument("--file", type=str, help="Path to file", default= None)
parser.add_argument("--scene", type=str, help="Path to scene.py file", default= None)
args = parser.parse_args()

file_path = args.file
scene_path = args.scene

def entry():
  if file_path is None and scene_path is None:
    return
  
  elif not file_path is None:
    print(parsefile.parseFile(file_path))

if __name__ == "__main__":
  entry()