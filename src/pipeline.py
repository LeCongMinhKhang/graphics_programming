import OpenGL.GL as GL
import numpy as np
import os
import sys
import cv2
import logging

logger = logging.getLogger(__name__)
MAX_LIGHTS = 16


class Pipeline:
  # buffers
  # contains object dict {
  #     "vao": <VAO>,
  #     "program_id": program_idx,
  #     "gl_mode": gl_mode,
  #     "color_mode": "uv" or "color",
  #     "uniforms": [<object-specific uniform dict>, ...],
  #     "indexing": <bool>     // whether or not there is an EBO
  # }
  objects = []
  programs = []  # list of programs (<Shader>, <Umanager>)

  def update_program(self, program_id, vert_shader=None, frag_shader=None, static_uniforms=None):
    """
    Update a program or create one if program_id is -1
    :return: program_id (the new one if a program has been created)
    """
    if vert_shader is None and frag_shader is None and static_uniforms is None:
      logger.debug("all data parameter are None, no update performed")
      return

    if program_id == -1:
      if vert_shader is None or frag_shader is None:
        logger.error("need both vert_shader and frag_shader files when creating a program")
        exit(1)
      self.programs.append((None, None))
      program_id = len(self.programs) - 1

    # shaders
    if vert_shader is not None and frag_shader is not None:
      logger.debug("Loading shaders")
      shader = Shader(vert_shader, frag_shader)
      uma = UManager(shader)
      self.programs[program_id] = (shader, uma)
      logger.debug(
        "Vertex shader: %s loaded\n\tFragment shader: %s loaded", vert_shader, frag_shader
      )
    elif vert_shader is not None or frag_shader is not None:
      logger.debug("both shader files must be given at the same time, no update performed")

    # Uniforms
    if static_uniforms is not None:
      for uniform in static_uniforms:
        if (
          type(uniform) is not type({})
          or "name" not in uniform.keys()
          or "value" not in uniform.keys()
          or "type" not in uniform.keys()
        ):
          logger.error('static_uniforms vector should contain dict("name": n, "value": v)')
        else:
          if "transpose" in uniform.keys():
            uma.upload_uniform(
              uniform["value"], uniform["name"], uniform["type"], uniform["transpose"]
            )
          else:
            uma.upload_uniform(uniform["value"], uniform["name"], uniform["type"])
          logger.debug("Static uniform %s added", uniform["name"])

    return program_id

  # @colors: shape (n, 3) = colors, shape (n, 2) = uvs
  def update_object(
    self,
    obj_id,
    program_id=None,
    mode=None,
    static_uniforms=None,
    model_matrix=None,
  ):
    if obj_id >= len(self.objects):
      logger.error("invalid object index: %d >= %d", obj_id, len(self.objects))
      exit(1)
    obj = self.objects[obj_id]

    # program id
    if program_id is not None:
      obj["program_id"] = program_id

    # drawing mode
    if mode is not None:
      self.objects[obj_id]["gl_mode"] = mode
      logger.debug("Draw mode set to %s", mode)

    # updating specific uniforms
    if model_matrix is not None or static_uniforms is not None:
      static_uniforms = static_uniforms if static_uniforms is not None else np.array([])
      model_uniform = np.array([])
      if model_matrix is not None:
        if model_matrix.shape != (4, 4):
          logger.error(f"model matrix should be of shape (4, 4), not {model_matrix.shape}")
          exit(1)
        model_uniform = np.array([{"name": "model", "value": model_matrix, "type": "mat4"}])

      uniforms = np.concatenate((static_uniforms, model_uniform))
      to_add = []
      for uniform in uniforms:
        updated = False
        for old_unif in self.objects[obj_id]["uniforms"]:
          if old_unif["name"] == uniform["name"]:
            if old_unif["type"] != uniform["type"]:
              logger.warning(
                "changing the %s uniform type from %s to %s",
                old_unif["name"],
                old_unif["type"],
                uniform["type"],
              )
            old_unif["value"] = uniform["value"]
            updated = True
            break
        if not updated:
          to_add.append(uniform)

      self.objects[obj_id]["uniforms"] = np.concatenate((self.objects[obj_id]["uniforms"], to_add))

  def add_object(
    self,
    vertices,
    normals,
    colors,
    program_id,
    indices=None,
    mode=None,
    specific_static_uniforms=None,
    model_matrix=None,
  ):
    """
    (vert_shader, frag_shader) XOR shader must be provided.

    :param shader: a Shader class instance
    """
    logger.debug("---------- Adding new object ----------")

    if vertices is None:
      logger.error("None vertices parameter not accepted ")
      exit(1)
    if normals is None:
      logger.error("None normals parameter not accepted ")
      exit(1)
    if colors is None:
      logger.error("None colors parameter not accepted ")
      exit(1)
    if program_id is None:
      logger.error("None program_id parameter not accepted")
      exit(1)

    obj = {}
    self.objects.append(obj)

    # drawing mode
    mode = mode if mode is not None else GL.GL_TRIANGLES
    obj["gl_mode"] = mode
    logger.debug("Draw mode set to %s", mode)

    # checking for data arrays dimensions
    # vertices
    if vertices.shape[1] != 3:
      logger.error("Invalid vertices format")
      exit(1)

    # normals
    if vertices.shape[0] != normals.shape[0]:
      logger.error(
        f"vertices and normals vector sizes doesn't match: {vertices.shape[0]} != {normals.shape[0]}"
      )
      exit(1)
    if normals.ndim != 2 or normals.shape[1] != 3:
      logger.error("normals vector should be of shape (n, 3)")
      exit(1)

    # colors
    if vertices.shape[0] != colors.shape[0]:
      logger.error("vertices and color vector sizes doesn't match")
      exit(1)
    if colors.ndim == 2 and colors.shape[1] == 2:
      obj["color_mode"] = "uv"
    elif colors.ndim == 2 and colors.shape[1] == 3:
      obj["color_mode"] = "color"
    else:
      logger.error(f"colors vector should be of shape (n, 2) or (n, 3), not {colors.shape}")
      exit(1)

    # indices
    if indices is None:
      obj["indexing"] = False
      logger.debug("No index array (no EBO creation)")
    else:
      obj["indexing"] = True
      logger.debug("Index array present (EBO creation)")

      if indices.ndim != 1:
        logger.error("indices vector should be of dimension 1")
        exit(1)
      id_max = np.max(indices)
      if id_max >= vertices.shape[0]:
        logger.error(f"indices vector contains {id_max} that is out of range")
        exit(1)

    # model matrix
    if model_matrix is None:
      model_matrix = np.identity(4)
    else:
      if model_matrix.shape != (4, 4):
        logger.error(f"model matrix should be of shape (4, 4), not {model_matrix.shape}")

    # shaders
    if program_id >= len(self.programs) or program_id < 0:
      logger.error("out of bound program_id: %d not in  [0, %d[", program_id, len(self.programs))
      exit(1)
    obj["program_id"] = program_id

    # load data to GPU
    # VBOs
    vao = VAO()
    obj["vao"] = vao
    vao.add_vbo(0, vertices, ncomponents=3, stride=0, offset=None)
    vao.add_vbo(
      1, colors, ncomponents=(3 if obj["color_mode"] == "color" else 2), stride=0, offset=None
    )
    vao.add_vbo(2, normals, ncomponents=3, stride=0, offset=None)
    logger.debug("VBOs successfully created")

    # EBO
    if obj["indexing"]:
      vao.add_ebo(indices)
      logger.debug("EBO successfully created, %d indices", vao.index_count)

    # Uniforms
    static_uniforms = np.concatenate(
      (
        specific_static_uniforms,
        np.array([{"name": "model", "value": model_matrix, "type": "mat4"}]),
      )
    )
    obj["uniforms"] = static_uniforms
    return len(self.objects) - 1

  def draw(self, uniforms=np.array([]), to_draw=None):
    """
    Draws objects with OpenGL.
    The objects to be rendered are indexed by loading order.

    :param uniforms: uniforms to upload for this draw call (dynamic ones)
    :param to_draw: index list of objects to be rendered.
                    All objects are rendered when parameter not provided.
    """

    def draw_object(obj):
      vao = obj["vao"]
      (shader, uma) = self.programs[obj["program_id"]]
      gl_mode = obj["gl_mode"]
      specific_uniforms = obj["uniforms"]
      indexing = obj["indexing"]
      vao.activate()  # bind VAO
      GL.glUseProgram(shader.render_idx)
      # upload non-static uniforms
      for uniform in np.concatenate((uniforms, np.array(specific_uniforms))):
        if "transpose" in uniform.keys():
          uma.upload_uniform(
            uniform["value"], uniform["name"], uniform["type"], uniform["transpose"]
          )
        else:
          uma.upload_uniform(uniform["value"], uniform["name"], uniform["type"])
      if indexing:
        GL.glDrawElements(gl_mode, vao.index_count, GL.GL_UNSIGNED_INT, None)
      else:
        GL.glDrawArrays(gl_mode, 0, vao.vertex_count)
      vao.deactivate()

    if to_draw is None:
      for obj in self.objects:
        draw_object(obj)
    else:
      for idx in to_draw:
        draw_object(self.objects[idx])

  def destroy(self):
    for obj in self.objects:
      obj["vao"].destroy()
    for shader, uma in self.programs:
      if uma is not None:
        uma.destroy()
      if shader is not None:
        shader.destroy()
    self.objects.clear()
    self.programs.clear()
    logger.debug("Allocated buffers freed")


class VAO(object):
  # consider dropping this and getting the info from the buffers themselves
  index_count = 0
  vertex_count = 0

  def __init__(self):
    self.vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(self.vao)
    GL.glBindVertexArray(0)
    self.vbo = {}
    self.ebo = None
    self._destroyed = False

  def add_vbo(
    self, location, data, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None
  ):
    self.vertex_count = data.shape[0]
    self.activate()  # VAO
    buffer_idx = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer_idx)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
    # location = GL.glGetAttribLocation(self.shader.render_idx, name)
    GL.glVertexAttribPointer(location, ncomponents, dtype, normalized, stride, offset)
    GL.glEnableVertexAttribArray(location)
    self.vbo[location] = buffer_idx
    self.deactivate()  # VAO

  def add_ebo(self, indices):
    self.index_count = indices.shape[0]
    self.activate()
    self.ebo = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices, GL.GL_STATIC_DRAW)
    self.deactivate()

  def destroy(self):
    if self._destroyed:
      return
    self._destroyed = True
    GL.glDeleteVertexArrays(1, np.array([self.vao], dtype=np.uint32))
    if self.vbo:
      GL.glDeleteBuffers(len(self.vbo), np.array(list(self.vbo.values()), dtype=np.uint32))
    if self.ebo is not None:
      GL.glDeleteBuffers(1, np.array([self.ebo], dtype=np.uint32))
    self.vbo = {}
    self.ebo = None

  def activate(self):
    GL.glBindVertexArray(self.vao)  # activated

  def deactivate(self):
    GL.glBindVertexArray(0)  # activated


class UManager(object):
  def __init__(self, shader):
    self.shader = shader
    self.textures = {}

  def destroy(self):
    ids = [t["id"] for t in self.textures.values()]
    if ids:
      GL.glDeleteTextures(len(ids), np.array(ids, dtype=np.uint32))
    self.textures = {}

  @staticmethod
  def load_texture(filename):
    # Keep 4 channels when present. Always RGBA so each row is 4-byte aligned
    # (GL_UNPACK_ALIGNMENT defaults to 4; odd-width RGB uploads scramble colors).
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    if img is None:
      raise FileNotFoundError(filename)
    if img.ndim == 2:
      img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    elif img.shape[2] == 4:
      img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    else:
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    return np.ascontiguousarray(img)

  def _get_texture_loc(self):
    if not bool(self.textures):
      return 0
    else:
      locs = list(self.textures.keys())
      locs.sort(reverse=True)
      ret_id = locs[0] + 1
      return ret_id

  """
    * first call to setup_texture: activate GL.GL_TEXTURE0
        > use GL.glUniform1i to associate the activated texture to the texture in shading program (see fragment shader)
    * second call to setup_texture: activate GL.GL_TEXTURE1
        > use GL.glUniform1i to associate the activated texture to the texture in shading program (see fragment shader)
    * second call to setup_texture: activate GL.GL_TEXTURE2
        > use GL.glUniform1i to associate the activated texture to the texture in shading program (see fragment shader)
    and so on

    """

  def setup_texture(self, sampler_name, image_file):
    rgba_image = UManager.load_texture(image_file)

    GL.glUseProgram(self.shader.render_idx)  # must call before calling to GL.glUniform1i
    texture_idx = GL.glGenTextures(1)
    binding_loc = self._get_texture_loc()
    self.textures[binding_loc] = {}
    self.textures[binding_loc]["id"] = texture_idx
    self.textures[binding_loc]["name"] = sampler_name

    GL.glActiveTexture(
      GL.GL_TEXTURE0 + binding_loc
    )  # activate texture GL.GL_TEXTURE0, GL.GL_TEXTURE1, ...
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_idx)
    GL.glUniform1i(GL.glGetUniformLocation(self.shader.render_idx, sampler_name), binding_loc)

    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexImage2D(
      GL.GL_TEXTURE_2D,
      0,
      GL.GL_RGBA,
      rgba_image.shape[1],
      rgba_image.shape[0],
      0,
      GL.GL_RGBA,
      GL.GL_UNSIGNED_BYTE,
      rgba_image,
    )
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

  def upload_uniform(self, value, name, dtype, transpose=None):
    program = self.shader.render_idx
    GL.glUseProgram(program)
    location = GL.glGetUniformLocation(program, name)
    match dtype:
      # scalars
      case "bool":
        GL.glUniform1i(location, value)
      case "int":
        GL.glUniform1i(location, np.int32(value))
      case "uint":
        GL.glUniform1ui(location, np.uint32(value))
      case "float":
        GL.glUniform1f(location, np.float32(value))
      case "double":
        GL.glUniform1d(location, np.float64(value))

      # vectors
      # bool, int, uint
      case "bvec2" | "ivec2":
        GL.glUniform2iv(location, 1, value)
      case "bvec3" | "ivec3":
        GL.glUniform3iv(location, 1, value)
      case "bvec4" | "ivec4":
        GL.glUniform4iv(location, 1, value)
      # int
      case "uvec2":
        GL.glUniform2uv(location, 1, value)
      case "uvec3":
        GL.glUniform3uv(location, 1, value)
      case "uvec4":
        GL.glUniform4uv(location, 1, value)
      # float
      case "vec2" | "fvec2":
        GL.glUniform2fv(location, 1, value)
      case "vec3" | "fvec3":
        GL.glUniform3fv(location, 1, value)
      case "vec4" | "fvec4":
        GL.glUniform4fv(location, 1, value)
      # double
      case "dvec2":
        GL.glUniform2fv(location, 2, value)
      case "dvec3":
        GL.glUniform3fv(location, 2, value)
      case "dvec4":
        GL.glUniform4fv(location, 2, value)

      # matrices
      case "mat2" | "mat2x2":
        GL.glUniformMatrix2fv(location, 1, True if transpose is None else transpose, value)
      case "mat3" | "mat3x3":
        GL.glUniformMatrix3fv(location, 1, True if transpose is None else transpose, value)
      case "mat4" | "mat4x4":
        GL.glUniformMatrix4fv(location, 1, True if transpose is None else transpose, value)

      # lights
      case "lights":
        n = min(len(value), MAX_LIGHTS)
        for i, light in enumerate(value[:n]):

          def loc(name):
            return GL.glGetUniformLocation(program, f"lights[{i}].{name}")

          GL.glUniform3f(loc("position"), *light.position)
          GL.glUniform3f(loc("color"), *light.color)
          GL.glUniform1f(loc("intensity"), light.intensity)

      # invalid type
      case _:
        logger.error("No uniform type matching %s", dtype)
        exit(1)


class Shader:
  """Helper class to create and automatically destroy shader program"""

  def __init__(self, vertex_source, fragment_source):
    """Shader can be initialized with raw strings or source file names"""
    self.render_idx = None
    vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
    frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
    if vert and frag:
      self.render_idx = GL.glCreateProgram()  # pylint: disable=E1111
      GL.glAttachShader(self.render_idx, vert)
      GL.glAttachShader(self.render_idx, frag)
      GL.glLinkProgram(self.render_idx)
      GL.glDeleteShader(vert)
      GL.glDeleteShader(frag)
      status = GL.glGetProgramiv(self.render_idx, GL.GL_LINK_STATUS)
      if not status:
        logger.error(GL.glGetProgramInfoLog(self.render_idx).decode("ascii"))
        sys.exit(1)

  def destroy(self):
    if self.render_idx:
      GL.glUseProgram(0)
      GL.glDeleteProgram(self.render_idx)
      self.render_idx = None

  @staticmethod
  def _compile_shader(src, shader_type):
    src = open(src, "r").read() if os.path.exists(src) else src
    src = src.decode("ascii") if isinstance(src, bytes) else src
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, src)
    GL.glCompileShader(shader)
    status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    src = ("%3d: %s" % (i + 1, line) for i, line in enumerate(src.splitlines()))
    if not status:
      log = GL.glGetShaderInfoLog(shader).decode("ascii")
      GL.glDeleteShader(shader)
      src = "\n".join(src)
      logger.error("Compile failed for %s\n%s\n%s" % (shader_type, log, src))
      sys.exit(1)
    return shader
