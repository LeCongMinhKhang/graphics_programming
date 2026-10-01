import tkinter as tk
from tkinter import ttk
from OpenGL import GL
from pyopengltk import OpenGLFrame
import time
import datetime
import numpy as np

import logging

from src.pipeline import Pipeline
from src.camera.camera import Camera

from .tkwindowComponents.table import Tablerone
from .tkwindowComponents.stylingHelper import RowTracker as Row, StyleEnum as Ste
from .tkwindowComponents.scrollable import ScrollableList 

logger = logging.getLogger(__name__)

class App(tk.Tk):
  def __init__(self, data = [], window_size=(640, 480), camera=Camera, lights=None, wireframe=False):
    super().__init__()
    self.title("Graphics")
    self.resizable(True,False)
    self.geometry(f"{window_size[0]}x{window_size[1]}")
    self.minsize(window_size[0],window_size[1])
    self.grid_columnconfigure(index=(0),minsize = window_size[1])
    self.grid_columnconfigure(index=(1),weight=1)
    self.diagnostics = Diagnostics(self)    
    self.diagnostics.grid(row=0 , column=0,sticky="nw")
    self.viewport = AppOgl(parent=self, data = data, window_size=window_size, camera=camera, lights=lights, wireframe=wireframe, 
                           func= self.diagnostics.fps
                          ) 
    self.viewport.grid(row = 0,column=0,sticky="nw")
    self.diagnostics.lift(self.viewport)
    
    self.sidebar = ScrollableList(self)
    self.sidebar.grid(row=0,column=1,sticky="nsew")
    self.sidebar.frameframe.grid_columnconfigure(index=0,weight=1)

    self.table = Tablerone(self.sidebar.frameframe,col=3)
    self.table.grid(row=0,column=0,sticky="nsew")
    self.table.grid_columnconfigure(index=(0,1,2),weight=1)
    self.table.newRow(
      self.table.label(text="Control Panel"),
      self.table.none(),
      self.table.button(text="Apply")
    )
    self.table.newRow(
      self.table.label(text="Displaying:"),
      self.table.comboBox(id = "scenetype",values=[
        "file","triangle","rectangle","pentagon","hexagon","circle","ellipse","trapezoid","star","arrow","cube","cylinder","prism","truncated_cone","cone","tetrahedron","surface","sphere","torus",], 
        state="readonly"),
      self.table.entry()
    )

    self.after(100, self.viewport.printContext) 
    self.viewport.mainloop()


class Diagnostics(ttk.Frame):
  def __init__(self,parent):
    super().__init__(parent)

    self.live = True
    self.records = []
    self.low = 999999
    self.lowRecords = []
    self.lowCount = 0
    
    self.table = Tablerone(self,col = 2)
    self.table.grid(row=0,column=0,sticky="nsew")
    self.table.newRow(
      self.table.label(text="FPS:"),
      self.table.label(text="n/a", id="fps")
    )
    self.table.newRow(
      self.table.label(text="1%:"),
      self.table.label(text="n/a", id="low")
    )

  def fps(self,val):
    self.low = min(self.low,val)
    self.records.append(val)
    if len(self.records) >= 100:
      self.table.get("low").config(text=str(int(self.low)))
      self.low = val
      avg = self.records[0]
      for data in self.records[1:]:
        avg += data
      avg /= len(self.records)
      self.table.get("fps").config(text=str(int(avg)))
      self.records = []

  def export(self,table):
    with open(f"./{datetime.datetime.now(datetime.UTC).strftime("%d-%m-%y_%H-%M-%S")}.csv","w",encoding="utf8") as file:
      file.writelines("\n".join([",".join([table.get(r,c)["text"] for c in range(len(table.table))]) for r in range(len(table.table[0]))]))



class AppOgl(OpenGLFrame):
  def __init__(self,/,*args,parent = None, data = [], window_size=(640, 480), camera=Camera, lights=None, wireframe=False, func = lambda a : None, **kw):
    root = parent if parent is not None else tk.Tk()
    self.data = data
    self.func = func
    self.mouse = {
      "x": 0.0,
      "y": 0.0,
      "mb1_x": 0.0,
      "mb1_y": 0.0,  # current position (GL coords, y-up)
      "mb1_down_x": 0.0,
      "mb1_down_y": 0.0,  # position at last press
      "mb1_down": False,
      "scroll_x": 0.0,
      "scroll_y": 0.0,
      "scroll_delta_x": 0.0,
      "scroll_delta_y": 0.0,
    }
    self.wireframe = wireframe
    self.lights = lights
    self.pipeline = Pipeline()
    
    self.default_static_uniforms = np.array(
      [
        {
          "name": "iResolution",
          "value": np.array([window_size[0], window_size[1]], dtype=np.float32),
          "type": "vec2",
        },
      ]
    )
    self.entries = ["vertices","normals","colors","vert_shader","frag_shader","indices","mode","static_uniforms","model_matrix","vao_id",]

    self.cam = camera()
    logger.debug("Camera initialized")
    self.start_time = time.time()
    self.old_time = self.start_time
    self.new_time = self.old_time
    self.pipeline.destroy()
    super().__init__(root,*args,width = window_size[0],height = window_size[1], **kw)
    self.bind("<Motion>", self.on_drag)
    self.bind("<Button-1>", self.on_mouse)
    self.bind("<MouseWheel>", self.on_mouse)
    self.bind("<ButtonRelease-1>", self.on_mouse)
    self.animate = 1
  # glfw.set_cursor_pos_callback(window, cursor_pos_callback)
  # glfw.set_mouse_button_callback(window, mouse_button_callback)
  # glfw.set_scroll_callback(window, scroll_callback)

  
  def on_drag(self, event):
    self.cursor_pos_callback(event.x, event.y)
  
  def on_mouse(self,event):
    match event.type:
      case tk.EventType.ButtonPress:
        self.mouse_button_callback("press")
      case tk.EventType.ButtonRelease:
        self.mouse_button_callback("release")
      case tk.EventType.MouseWheel:
        self.scroll_callback(0, event.delta/10)


  def cursor_pos_callback(self, xpos, ypos):
    height = self.winfo_height()
    self.mouse["x"] = xpos
    self.mouse["y"] = height - ypos
    if self.mouse["mb1_down"]:  # update mb1 position only when mb1 is pressed
      self.mouse["mb1_x"] = xpos
      self.mouse["mb1_y"] = int(height) - ypos  # flip so y=0 is bottom

  def mouse_button_callback(self, action):
    if action == "press":
      self.mouse["mb1_down"] = True
      self.mouse["mb1_down_x"] = self.mouse["x"]
      self.mouse["mb1_down_y"] = self.mouse["y"]
      self.mouse["mb1_x"] = self.mouse["x"]
      self.mouse["mb1_y"] = self.mouse["y"]
    elif action == "release":
      self.mouse["mb1_down"] = False

  def scroll_callback(self, xoffset, yoffset):
    self.mouse["scroll_x"] += xoffset
    self.mouse["scroll_y"] += yoffset
    self.mouse["scroll_delta_x"] = xoffset
    self.mouse["scroll_delta_y"] = yoffset

  def initgl(self):
    """Initalize gl states when the frame is created"""
    GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test
    GL.glDepthFunc(GL.GL_LESS)  # default; fragment passes if depth < stored depth

    GL.glFrontFace(GL.GL_CCW)  # winding order: counter clockwise indexing
    GL.glCullFace(GL.GL_BACK)  # when face culling enabled, render only front faces

    # wireframe mode toggle (affects backface culling)
    if self.wireframe:
      GL.glDisable(GL.GL_CULL_FACE)  # face culling disabled
      GL.glPolygonMode(GL.GL_FRONT, GL.GL_LINE)
      GL.glPolygonMode(GL.GL_BACK, GL.GL_LINE)
      logger.debug("Wireframe mode enabled.")
    else:
      GL.glEnable(GL.GL_CULL_FACE)  # face culling enabled
      GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
      GL.glPolygonMode(GL.GL_BACK, GL.GL_FILL)

      
    for obj in self.data:
      obj_data = {}
      for entry in self.entries:
        if entry in obj.keys():
          obj_data[entry] = obj[entry]
        else:
          obj_data[entry] = None
      self.pipeline.add_object(
        vertices=obj_data["vertices"],
        normals=obj_data["normals"],
        colors=obj_data["colors"],
        vert_shader=obj_data["vert_shader"],
        frag_shader=obj_data["frag_shader"],
        indices=obj_data["indices"],
        mode=obj_data["mode"],
        static_uniforms=np.concatenate(
          (
            self.default_static_uniforms,
            (
              obj_data["static_uniforms"] if obj_data["static_uniforms"] is not None else np.array([])
            ),
          )
        ),
        model_matrix=obj_data["model_matrix"],
        vao_id=obj_data["vao_id"],
      )
    logger.debug("---------- All objects added (%d) ----------", len(self.data))

  def redraw(self):
    """Render a single frame"""
    self.old_time = self.new_time
    self.new_time = time.time()
    self.func(int(1/(self.new_time - self.old_time)) if self.new_time != self.old_time else 999999)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    uniforms = np.array(
      [{  "name": "iTime",  "value": time.time() - self.start_time,  "type": "float",},]
      + ([ self.lights ] if self.lights is not None else [])
    )
    uniforms = self.cam.update(uniforms=np.concatenate((self.default_static_uniforms, uniforms)), mouse=self.mouse)

    self.pipeline.draw(uniforms)




def display(data, window_size=(640, 480), camera=Camera, lights=None, wireframe=False):
  app = App(data = data,window_size=window_size,camera=camera,lights=lights,wireframe=wireframe)
  return 0


# if __name__ == "__main__":
#   display()