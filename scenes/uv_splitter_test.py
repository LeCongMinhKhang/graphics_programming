from src.scene import Scene, AppOgl
import src.transform as transform
from types import MethodType
from src.shape_generators.two_dee import rectangle, star
from src.shape_generators.three_dee import uv_sphere, surface
from src.shape_generators.tools import uvSlicer
import numpy as np
def scenes(gl_app: AppOgl):
  scenes = {}
  name = "!uvSplitterTest"
  def make_build_scene(name):
    def build_scene(self):
      # obj_id, _ = self.add_object(name)
      # self.program_name = "interpolation"
      # self.color_mode = "color"
      # self.update_object(
      #   obj_id,
      #   model_matrix=transform.identity(),
      #   program_name=self.program_name,
      #   color_mode=self.color_mode,
      # )
      self.program_name = "interpolation"
      self.gl_app.create_program("interpolation")
      # core
      limx = 5
      limy = 5
      n = 3
      index = lambda x,y: ((y+limy) % (2*limy * 2**n + 1)) * (2*limx * 2**n + 1) + (x+limx) % (2*limx * 2**n + 1)
      obj = surface.generate(n = n, limx=limx, limy=limy, func = lambda x,y: 0,color="hex", hex=0xffffff)
      print(uvSlicer(obj,[
        # 2 different seams on top of eachother
        {"splits":[index(0,x) for x in range(limx* 2**n ,-limx* 2**n -1,-1 )],"tears":[None,None]},
        {"splits":[index(x,0) for x in range(limx* 2**n ,-limx* 2**n - 1,-1 )],"tears":[None,None]},

        # seam goes through itself
        # {"splits":[index(0,x) for x in range(limx* 2**n ,-limx* 2**n -1,-1 )]
        #         + [index(x,0) for x in range(limx* 2**n ,-limx* 2**n -1,-1 )],"tears":[None,None]},
        
        # seam goes through itself 2
        # {"splits":[index(0,0),index(1,0),index(1,1),index(0,1),index(0,0)],"tears":[index(-1,0),index(0,-1)]},

        # one seam acting like 2 seams
        # {"splits":[index(x,0) for x in range(limx* 2**n ,-limx* 2**n -1,-1 )]
        #         + [index(x,1) for x in range(-limx* 2**n ,limx* 2**n+1,1 )],"tears":[None,None]},
      ],True))
      groups = []
      for i in range(0,len(obj["indices"]),3):
        triangle = obj["indices"][i:i+3]
        flag = False
        for [v,f] in groups:
          if len(list(filter(lambda p: p not in v,triangle))) < 3:
            [v.add(p) for p in triangle]
            f.add(i)
            flag = True
        if not flag:
          groups.append([{p for p in triangle},{i}])
      print("len groups",len(groups))

      # print(index(0,0))
      # obj = star.generate(color="normal")
      # print(uvSlicer(obj,[
      #   [None]+list(range(0,10,2))+[None],
      #   # [None]+[index(i,i) for i in range(-limy* 2**n,limy* 2**n+1)]+[None],
      # ],True))


      coreId, _ = self.add_object(name, data=obj)
      self.update_object(coreId, model_matrix=transform.identity(), program_name="interpolation")

    return build_scene

  scene = Scene(gl_app)
  scene.build_scene = MethodType(make_build_scene(name), scene)
  scenes[name] = scene

  return scenes
