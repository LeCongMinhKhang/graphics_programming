import tkinter as tk
from tkinter import ttk
from OpenGL import GL
from pyopengltk import OpenGLFrame
import time
import sys
import datetime
import numpy as np
import importlib
import pkgutil

import scenes as scenes_pkg  # the scenes directory

import logging

from src.pipeline import Pipeline
from src.camera.camera import Camera
from src.parsefile import parseFile

from src.shape_generators.two_dee import triangle, trapezoid, rectangle, star, n_gon, arrow
from src.shape_generators.three_dee import cube, cylinder, n_gon_pyramid, surface, uv_sphere, torus
from src.light import Light
import src.transform as transform

from .tkwindowComponents.table import Tablerone
from .tkwindowComponents.stylingHelper import RowTracker as Row, StyleEnum as Ste
from .tkwindowComponents.scrollable import ScrollableList

logger = logging.getLogger(__name__)


def load_all_scenes(gl_app):
  all_scenes = {}
  for module_info in pkgutil.iter_modules(scenes_pkg.__path__):
    module = importlib.import_module(f"{scenes_pkg.__name__}.{module_info.name}")
    if hasattr(module, "scenes"):
      all_scenes.update(module.scenes(gl_app))  # gather every scene
  return all_scenes


class App(tk.Tk):
  ROTATION_PERIOD_MAX = 10.0
  ROTATION_PERIOD_MIN = 0.5

  def __init__(self, data=[], window_size=(640, 480), camera=Camera, lights=None, wireframe=False):
    super().__init__()
    self.title("Graphics")
    self.resizable(True, False)
    w, h = window_size[0] + 500, window_size[1]
    x = (self.winfo_screenwidth() - w) // 2
    y = (self.winfo_screenheight() - h) // 2
    self.geometry(f"{w}x{h}+{x}+{y}")  # centers the window
    self.minsize(window_size[0], window_size[1])

    self.grid_columnconfigure(index=(0), minsize=window_size[0])
    self.grid_columnconfigure(index=(1), weight=1)
    self.diagnostics = Diagnostics(self)
    self.diagnostics.grid(row=0, column=0, sticky="nw")
    self.viewport = AppOgl(
      parent=self,
      # data=data,
      window_size=window_size,
      camera=camera,
      # lights=lights,
      func=self.diagnostics.fps,
    )
    self.viewport.grid(row=0, column=0, sticky="nw")
    self.diagnostics.lift(self.viewport)

    all_scenes = load_all_scenes(self.viewport)
    self.viewport.scenes = all_scenes

    # options
    self.lighting_var = tk.StringVar()
    self.wireframe_var = tk.BooleanVar()
    self.texture_var = tk.BooleanVar()
    self.rotation_var = tk.DoubleVar()
    self.nb_lights_var = tk.IntVar()

    # UI definition
    self.sidebar = ScrollableList(self)
    self.sidebar.grid(row=0, column=1, sticky="nsew")
    self.sidebar.frameframe.grid_columnconfigure(index=(0,), weight=1)

    self.table = Tablerone(self.sidebar.frameframe, col=2)
    self.table.grid(row=0, column=0, sticky="nsew")
    self.table.grid_columnconfigure(index=(0, 1), weight=1)
    self.table.newRow(self.table.label(text="Control Panel"), self.table.none())
    # scene type
    self.table.newRow(
      self.table.label(text="Displaying:"),
      self.table.comboBox(
        id="scenetype",
        values=sorted(["file"] + list(all_scenes.keys())),
        # default=17,
        state="readonly",
        command=self.select_scene,
      ),
    )
    self.table.newRow(
      self.table.label(text="File Path:", id="filePathLabel"),
      self.table.entry(id="filePath"),
    )
    self.table.get(id="filePath").bind("<Return>", lambda event: self.change_scene("file"))
    self.table.get(id="filePathLabel").config(text="", padding=(0, Ste.PAD.value))
    self.table.get(id="filePath").grid_remove()

    # lighting
    self.table.newRow(
      self.table.label(text="Lighting:"),
      self.table.comboBox(
        id="lighting",
        values=list(self.viewport.programs.keys()),
        default=0,
        state="readonly",
        textvariable=self.lighting_var,
        command=self.change_lighting,
      ),
    )
    self.table.newRow(
      self.table.label(text="Number of lights (0-16)"),
      self.table.spinBox(
        id="nb_lights",
        from_=0,
        to=16,
        textvariable=self.nb_lights_var,
        default=1,
        command=self.change_nb_lights,
      ),
    )

    # options
    self.table.newRow(
      self.table.label(text="Wireframe"),
      self.table.checkButton(
        id="wireframe", command=self.change_wireframe, variable=self.wireframe_var, default=False
      ),
    )
    self.table.newRow(
      self.table.label(text="Texture"),
      self.table.checkButton(
        id="texture", command=self.change_color_mode, variable=self.texture_var, default=False
      ),
    )
    self.table.newRow(
      self.table.label(text="Rotation speed"),
      self.table.slider(
        from_=0,
        to=10,
        orient="horizontal",
        command=self.change_rotation,
        variable=self.rotation_var,
      ),
      # self.table.checkButton(
      #   id="rotation", command=self.change_rotation, variable=self.rotation_var
      # ),
    )
    self.after(100, self.viewport.printContext)
    self.protocol("WM_DELETE_WINDOW", self.on_close)
    self.viewport.mainloop()

  def on_close(self):
    self.viewport.animate = 0  # stop the redraw loop
    try:
      self.viewport.tkMakeCurrent()  # GL calls need the context
      self.viewport.pipeline.destroy()
    except Exception:
      logger.exception("error while freeing GL resources")
    self.destroy()

  def change_wireframe(self):
    if self.wireframe_var.get():
      GL.glDisable(GL.GL_CULL_FACE)  # face culling disabled
      GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
      logger.debug("Wireframe mode enabled.")
    else:
      GL.glEnable(GL.GL_CULL_FACE)  # face culling enabled
      GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
      logger.debug("Wireframe mode disabled.")

  def change_color_mode(self):
    color_mode = "texture" if self.texture_var.get() else "color"
    logger.debug("coloring with %s mode selected", "texture" if self.texture_var.get() else "color")
    self.viewport.select_color_mode(color_mode)

  def change_nb_lights(self):
    self.viewport.update_lights(self.nb_lights_var.get())
    self.viewport.update_static_uniforms(update_lights=True)
    logger.debug("%d lights total", self.nb_lights_var.get())

  def showHideFilePathField(self, show=False):
    if show:
      self.table.get(id="filePath").grid()
    else:
      self.table.get(id="filePath").grid_remove()

  def select_scene(self, event):
    value = event.widget.get()
    if value == "file":
      self.table.get(id="filePathLabel").config(text="File path:")
      self.showHideFilePathField(show=True)
    else:
      self.table.get(id="filePathLabel").config(text="")
      self.showHideFilePathField(show=False)
      self.change_scene(value)

  def change_scene(self, value):
    logger.debug("%s scene selected.", value)
    args = self.viewport.set_scene(value, self.table.get(id="filePath").get())
    self.update_widgets(*args)

  def change_lighting(self, event):
    value = event.widget.get()
    logger.debug("%s lighting selected.", value)
    self.viewport.select_program(value)

  def change_rotation(self, _):
    speed = self.rotation_var.get()
    if speed < self.ROTATION_PERIOD_MIN:
      rotation = 0
    else:
      rotation = max(self.ROTATION_PERIOD_MAX - speed, self.ROTATION_PERIOD_MIN)
    # logger.debug("rotation period set to %s s (if 0 then disabled)", rotation)
    self.viewport.set_rotation_period(rotation)

  def update_widgets(self, lighting=None, color_mode=None):
    if lighting is not None:
      self.lighting_var.set(lighting)
    if color_mode is not None:
      if color_mode == "texture":
        self.texture_var.set(True)
      if color_mode == "color":
        self.texture_var.set(False)


class Diagnostics(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)

    self.live = True
    self.records = []
    self.low = 999999
    self.lowRecords = []
    self.lowCount = 0

    self.table = Tablerone(self, col=2)
    self.table.grid(row=0, column=0, sticky="nsew")
    self.table.newRow(self.table.label(text="FPS:"), self.table.label(text="n/a", id="fps"))
    self.table.newRow(self.table.label(text="1%:"), self.table.label(text="n/a", id="low"))

  def fps(self, val):
    self.low = min(self.low, val)
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

  def export(self, table):
    with open(
      f"./{datetime.datetime.now(datetime.UTC).strftime('%d-%m-%y_%H-%M-%S')}.csv",
      "w",
      encoding="utf8",
    ) as file:
      file.writelines(
        "\n".join(
          [
            ",".join([table.get(r, c)["text"] for c in range(len(table.table))])
            for r in range(len(table.table[0]))
          ]
        )
      )


class AppOgl(OpenGLFrame):
  def __init__(
    self,
    /,
    *args,
    parent=None,
    # data=[],
    window_size=(640, 480),
    camera=Camera,
    # lights=None,
    func=lambda a: None,
    **kw,
  ):
    root = parent if parent is not None else tk.Tk()
    # self.data = data
    self.func = func
    self.scenes = {}

    self.objects = {}  # associates the name of an object (eg "cube") to a pair of (<used_objects>, <index_array_of_objects_loaded>)
    self.objects_rendered = (
      set()
    )  # set containing the indices of the pipeline objects to be rendered

    self.nb_lights = 1
    self.update_lights(self.nb_lights)

    self.mouse = {
      "x": 0.0,
      "y": 0.0,
      "mb_x": 0.0,
      "mb_y": 0.0,  # current position (GL coords, y-up)
      "mb_press_x": 0.0,
      "mb_press_y": 0.0,  # position at last press
      "mb1_down": False,
      "mb2_down": False,
      "scroll_x": 0.0,
      "scroll_y": 0.0,
      "scroll_delta_x": 0.0,
      "scroll_delta_y": 0.0,
    }
    self.pipeline = Pipeline()
    self.programs = {
      "flat": -1,
      "interpolation": -1,
      "phong": -1,
    }

    self.default_static_uniforms = np.array(
      [
        {
          "name": "iResolution",
          "value": np.array([window_size[0], window_size[1]], dtype=np.float32),
          "type": "vec2",
        },
        {
          "name": "iRotation",
          "value": 0.0,
          "type": "float",
        },
      ]
    )

    self.cam = camera()
    logger.debug("Camera initialized")
    self.start_time = time.time()
    self.old_time = self.start_time
    self.new_time = self.old_time
    super().__init__(root, *args, width=window_size[0], height=window_size[1], **kw)
    self.bind("<Motion>", self.on_drag)
    self.bind("<Button-1>", self.on_mouse)
    self.bind("<ButtonRelease-1>", self.on_mouse)
    self.bind("<Button-3>", self.on_mouse)  # on linux mb2
    self.bind("<ButtonRelease-3>", self.on_mouse)  # on linux mb2
    match sys.platform:
      case "win32" | "darwin":
        self.bind("<MouseWheel>", self.on_mouse)
        logger.debug("Bound mousewheel on Windows platform")
      case "linux":
        self.bind("<Button-4>", self.on_mouse)
        self.bind("<Button-5>", self.on_mouse)
      case _:
        logger.error("system platform %s not recognized", sys.platform)
        exit(1)
    self.animate = 1

  def on_drag(self, event):
    self.cursor_pos_callback(event.x, event.y)

  def on_mouse(self, event):
    if event.type == tk.EventType.MouseWheel:
      self.scroll_callback(0, 5 * np.sign(event.delta))
    else:
      match event.num:
        case 1:
          self.mb1_callback(event.type)
        case 3:
          self.mb2_callback(event.type)
        case 4:
          self.scroll_callback(0, 5)
        case 5:
          self.scroll_callback(0, -5)
        case _:
          logger.debug(f"no button action registered for: {event.type}, {event.num}")

  def cursor_pos_callback(self, xpos, ypos):
    height = self.winfo_height()
    self.mouse["x"] = xpos
    self.mouse["y"] = height - ypos
    # update mb position only when a button is pressed
    if self.mouse["mb1_down"] or self.mouse["mb2_down"]:
      self.mouse["mb_x"] = xpos
      self.mouse["mb_y"] = int(height) - ypos  # flip so y=0 is bottom

  def mb1_callback(self, action):
    if action == tk.EventType.ButtonPress:
      self.mouse["mb1_down"] = True
      self.mouse["mb_press_x"] = self.mouse["x"]
      self.mouse["mb_press_y"] = self.mouse["y"]
      self.mouse["mb_x"] = self.mouse["x"]
      self.mouse["mb_y"] = self.mouse["y"]
    elif action == tk.EventType.ButtonRelease:
      self.mouse["mb1_down"] = False

  def mb2_callback(self, action):
    if action == tk.EventType.ButtonPress:
      self.mouse["mb2_down"] = True
      self.mouse["mb_press_x"] = self.mouse["x"]
      self.mouse["mb_press_y"] = self.mouse["y"]
      self.mouse["mb_x"] = self.mouse["x"]
      self.mouse["mb_y"] = self.mouse["y"]
    elif action == tk.EventType.ButtonRelease:
      self.mouse["mb2_down"] = False

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

    GL.glEnable(GL.GL_CULL_FACE)  # face culling enabled
    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)  # wireframe disabled

  def update_lights(self, nb_lights, uniforms=None):
    self.nb_lights = nb_lights
    if uniforms is not None:
      self.light_uniforms = uniforms
      return
    lights = {
      "name": "lights",
      "type": "lights",
      "value": np.array(
        [
          Light(
            position=(
              10 * np.cos(2 * np.pi * i / self.nb_lights),
              10 * np.sin(2 * np.pi * i / self.nb_lights),
              10,
            ),
            color=(1, 1, 1),
            intensity=1 / (i + 1),
          )
          for i in range(self.nb_lights)
        ]
      ),
    }
    num_lights = {"name": "num_lights", "type": "int", "value": lights["value"].shape[0]}

    # material / ambient (static: they don't change between frames)
    ambient_color = {
      "name": "ambient_color",
      "type": "vec3",
      "value": np.array([0.1, 0.1, 0.1], dtype=np.float32),
    }
    k_ambient = {"name": "k_ambient", "type": "float", "value": 1.0}
    k_diffuse = {"name": "k_diffuse", "type": "float", "value": 1.0}
    k_specular = {"name": "k_specular", "type": "float", "value": 0.5}
    shininess = {"name": "shininess", "type": "float", "value": 32.0}

    uniforms = np.array(
      [lights, num_lights, ambient_color, k_ambient, k_diffuse, k_specular, shininess],
      dtype=object,
    )
    self.light_uniforms = uniforms
    logger.debug("changed lights uniforms")

  def select_program(self, name):
    # for each rendered object, update it with correct shaders/program
    for idx in self.objects_rendered:
      if self.programs[name] == -1:
        self.create_program(name)  # updates self.programs[name]
      self.update_object(idx, program_id=self.programs[name])
    self.update_static_uniforms(update_lights=True)

  def select_color_mode(self, color_mode):
    if color_mode not in ("texture", "color"):
      logger.error('color_mode must be "texture" or "color"')
      exit(1)
    for obj_id in self.objects_rendered:
      self.update_object(obj_id, color_mode=color_mode)
    self.update_static_uniforms()

  def create_program(self, name: str):
    program_id = self.programs[name]
    if program_id >= 0:  # program already created, nothing to do
      return
    logger.debug("---------- Adding new program (%s) ----------", name)
    match name:
      case "flat":
        vert_shader = "./shaders/flat.vert"
        frag_shader = "./shaders/flat.frag"
      case "interpolation":
        vert_shader = "./shaders/interp.vert"
        frag_shader = "./shaders/interp.frag"
      case "phong":
        vert_shader = "./shaders/lighting.vert"
        frag_shader = "./shaders/phong.frag"
      case _:
        logger.error('program "%s" not recognized', name)
        exit(1)
    self.programs[name] = self.pipeline.update_program(
      program_id, vert_shader=vert_shader, frag_shader=frag_shader
    )
    logger.debug("%s program created", name)

  def update_static_uniforms(self, update_lights=False):
    additional_uniforms = self.light_uniforms if update_lights else np.array([])
    for obj_id in self.objects_rendered:
      self.pipeline.upload_static_uniforms(obj_id, additional_uniforms)

  def set_scene(self, name, filePath=None):
    self.free_all_objects()
    scene = self.scenes.get(name if filePath is not None else filePath)
    if scene is None and name != "file":
      logger.error('no scene name corresponding to "%s"', name)
      exit(1)

    program_name = ""
    color_mode = ""
    if scene is None and name == "file":
      self.reserve_object("file", filePath)
      program_name = "interpolation"  # default shader program for obj files
      color_mode = "texture"  # default coloring mode for obj files
    else:
      scene.build_scene()
      program_name = scene.program_name
      color_mode = scene.color_mode

    self.update_static_uniforms()
    return program_name, color_mode

  def create_object(self, obj_name, filePath=None):
    obj = {}
    obj_program_name = "interpolation"
    match obj_name:
      case "file":
        obj = parseFile(filePath)
      # 2d
      case "triangle":
        obj = triangle.generate()
      case "rectangle":
        obj = rectangle.generate()
      case "pentagon":
        obj = n_gon.generate("pentagon")
      case "hexagon":
        obj = n_gon.generate("hexagon")
      case "circle":
        obj = n_gon.generate("circle")
      case "ellipse":
        obj = n_gon.generate("ellipse")
      case "trapezoid":
        obj = trapezoid.generate(size=1, size_wide=2)
      case "star":
        obj = star.generate()
      case "arrow":
        obj = arrow.generate()
      # 3d
      case "cube":
        obj = cube.generate()
      case "cylinder":
        obj = cylinder.generate()
      case "prism":
        obj = cylinder.generate(n=3)
      case "truncated_cone":
        obj = cylinder.generate(top_mult=0.5)
      case "cone":
        obj = n_gon_pyramid.generate("cone")
      case "tetrahedron":
        obj = n_gon_pyramid.generate("tetrahedron")
      case "surface":
        obj = surface.generate(func=lambda x, y: np.sin(x) + np.sin(y), n=3)
      case "sphere":
        obj = uv_sphere.generate(n=16)
      case "torus":
        obj = torus.generate(n=16)
      case _:
        logger.error('no object name corresponding to "%s"', obj_name)
        exit(1)
    self.create_program(obj_program_name)
    obj["program_id"] = self.programs[obj_program_name]
    obj_id = self.add_object(obj_name, obj)
    logger.debug("%s object created", obj_name)
    return obj_id, obj_program_name

  def update_object(self, obj_id: int, program: str = None, **kwargs):
    if program is not None:
      self.create_program(program)
      return self.pipeline.update_object(obj_id, program_id=self.programs[program], **kwargs)
    return self.pipeline.update_object(obj_id, **kwargs)

  def add_object(self, obj_name, obj):
    idx = self.pipeline.add_object(
      vertices=obj.get("vertices"),
      normals=obj.get("normals"),
      colors=obj.get("colors"),
      uvs=obj.get("uvs"),
      color_mode=obj.get("color_mode", "color"),
      program_id=obj.get("program_id"),
      indices=obj.get("indices"),
      mode=obj.get("gl_mode"),
      textures=obj.get("textures"),
      specific_static_uniforms=np.concatenate(
        (
          self.default_static_uniforms,
          (obj.get("static_uniforms") if "static_uniforms" in obj.keys() else np.array([])),
        )
      ),
    )
    if obj_name in self.objects.keys():
      self.objects[obj_name][1].append(idx)
    else:
      self.objects[obj_name] = [0, [idx]]
    return idx

  def free_object(self, obj_name):
    entry = self.objects.get(obj_name)
    if entry is None:
      logger.error('cannot free object type "%s", not in memory', obj_name)
      exit(1)
    if entry[0] == 0:
      logger.debug("nothing to free, nothing reserved")
      return
    self.objects_rendered.remove(entry[1][entry[0] - 1])
    self.objects[obj_name][0] -= 1
    if obj_name == "file":
      self.pipeline.free_object(self.objects["file"][1][-1])
      self.objects["file"][1].pop()
      logger.debug("deleting file import object")

  def free_object_category(self, obj_name):
    entry = self.objects.get(obj_name)
    if entry is None:
      logger.error('cannot free object type "%s", not in memory', obj_name)
      exit(1)
    for i in range(entry[0]):
      self.free_object(obj_name)

  def free_all_objects(self):
    for name in self.objects.keys():
      self.free_object_category(name)

  def reserve_object(self, obj_name, filePath=None):
    entry = self.objects.get(obj_name)
    obj_program_name = ""
    # if there is no more objects to reserve, create a new one
    if (entry is None) or (entry[0] >= len(entry[1])):
      _, obj_program_name = self.create_object(obj_name, filePath)
      self.objects[obj_name][0] += 1
    else:
      obj_program_name = self.get_program_name(entry[1][entry[0] - 1])
      self.objects[obj_name][0] += 1

    entry = self.objects[obj_name]  # update the entry if object created
    obj_id = entry[1][entry[0] - 1]
    self.objects_rendered.add(obj_id)
    return obj_id, obj_program_name

  def get_program_name(self, program_id):
    """Returns the name associated with the program id (linear search)."""
    for name, idx in self.programs.items():
      if idx == program_id:
        return name  # idx are assumed unique

  def set_rotation_period(self, period):
    self.default_static_uniforms[1]["value"] = period

  def redraw(self):
    """Render a single frame"""
    self.old_time = self.new_time
    self.new_time = time.time()
    self.func(
      int(1 / (self.new_time - self.old_time)) if self.new_time != self.old_time else 999999
    )
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    uniforms = np.concatenate(
      (
        np.array(
          [
            {
              "name": "iTime",
              "value": time.time() - self.start_time,
              "type": "float",
            },
            {
              "name": "iMouse",
              "value": np.array(
                [
                  self.mouse["mb_x"],
                  self.mouse["mb_y"],
                  self.mouse["mb_press_x"],
                  self.mouse["mb_press_y"],
                ],
                dtype=np.float32,
              ),
              "type": "vec4",
            },
          ]
        ),
        # self.light_uniforms,
      )
    )
    uniforms = self.cam.update(
      uniforms=np.concatenate((self.default_static_uniforms, uniforms)), mouse=self.mouse
    )
    self.pipeline.draw(uniforms=uniforms, to_draw=self.objects_rendered)


def display(data=[], window_size=(640, 480), camera=Camera, lights=None, wireframe=False):
  App(data=data, window_size=window_size, camera=camera)
  return 0
