import OpenGL.GL as GL
import numpy as np
import os
import sys
import cv2
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

class Pipeline:
  # buffers
  vaos = []
  programs = []

  # config
  gl_mode = GL.GL_TRIANGLE_STRIP
  color_mode = True  # True for colors, False for UVs
  indices_indexing = False
  data_type = GL.GL_UNSIGNED_INT

  def __init__(self):
    return

  # todo: support other primitives (mode).
  # @colors: shape (n, 3) = colors, shape (n, 2) = uvs
  def load_data(
    self,
    vertices,
    normals,
    colors,
    vert_shader,
    frag_shader,
    indices=None,
    mode=None,
    vao_id=None,
  ):
    logging.debug("Loading data")

    # drawing mode
    if mode is not None:
      self.mode = mode
    else:
      self.mode = GL.GL_TRIANGLES
    logging.debug("Draw mode set to %s", self.mode)

    # ebo presence (TODO: consider using the vao data to discover it, see further in the class)
    if indices is None:
      self.indices_indexing = False
      logging.debug("No index array (no EBO creation)")
    else:
      self.indices_indexing = True
      logging.debug("Index array present (EBO creation)")

    # checking for data arrays dimensions
    match self.mode:
      case GL.GL_TRIANGLES | GL.GL_TRIANGLE_STRIP:
        if vertices.shape[1] != 3:
          print("Invalid vertices format")
          exit(1)

    if normals is not None:
      if vertices.shape[0] != normals.shape[0]:
        print(
          f"vertices and normals vector sizes doesn't match: {vertices.shape[0]} != {normals.shape[0]}"
        )
        exit(1)
      if normals.ndim != 2  and normals.shape[1] != 3:
        print("normals vector should be of shape (n, 3)")
        exit(1)

    if colors is not None:
      if vertices.shape[0] != colors.shape[0]:
        print("vertices and color vector sizes doesn't match")
        exit(1)
      if colors.ndim == 2 and colors.shape[1] == 2:
        self.color_mode = False
      elif colors.ndim == 2 and colors.shape[1] == 3:
        self.color_mode = True
      else:
        print(f"colors vector should be of shape (n, 2) or (n, 3), not {colors.shape}")
        exit(1)

    if indices is not None:
      if indices.ndim != 1:
        print("indices vector should be of dimension 1")
        exit(1)
      id_max = np.max(indices)
      if id_max >= vertices.shape[0]:
        print(f"indices vector contains {id_max} that is out of range")
        exit(1)

    # loading shaders
    vao = None
    shader = Shader(vert_shader, frag_shader)
    if vao_id is None:
      self.programs.append((shader, UManager(shader)))
    else:
      self.programs[vao_id] = (shader, UManager(shader))
    logging.debug("vertex shader: %s loaded\n\tfragment shader: %s loaded", vert_shader, frag_shader)

    # load data to GPU
    # VBOs
    vao = None
    if vao_id is None:
      vao = VAO()
      self.vaos.append(vao)
    else:
      vao = self.vaos[vao_id]
    vao.add_vbo(0, vertices, ncomponents=3, stride=0, offset=None)
    vao.add_vbo(1, colors, ncomponents=(3 if self.color_mode else 2), stride=0, offset=None)
    vao.add_vbo(2, normals, ncomponents=3, stride=0, offset=None)
    logging.debug("VBOs successfully created")

    # EBO
    if self.indices_indexing:
      vao.add_ebo(indices)
      logging.debug("EBO successfully created")
    logging.debug("%d", vao.index_count)

  def load_shaders():
    return

  def draw(self):
    for vao, program in zip(self.vaos, self.programs):
      vao.activate()  # bind VAO
      GL.glUseProgram(program[0].render_idx)
      if self.indices_indexing:
        GL.glDrawElements(self.mode, vao.index_count, self.data_type, None)
      else:
        GL.glDrawArrays(self.mode, 0, vao.vertex_count)
      vao.deactivate()


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

  def __del__(self):
    GL.glDeleteVertexArrays(1, [self.vao])
    GL.glDeleteBuffers(1, list(self.vbo.values()))
    if self.ebo is not None:
      GL.glDeleteBuffers(1, [self.ebo])

  def activate(self):
    GL.glBindVertexArray(self.vao)  # activated

  def deactivate(self):
    GL.glBindVertexArray(0)  # activated


class UManager(object):
  def __init__(self, shader):
    self.shader = shader
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

  def upload_uniform_matrix4fv(self, matrix, name, transpose=True):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniformMatrix4fv(location, 1, transpose, matrix)

  def upload_uniform_matrix3fv(self, matrix, name, transpose=False):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniformMatrix3fv(location, 1, transpose, matrix)

  def upload_uniform_vector4fv(self, vector, name):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniform4fv(location, 1, vector)

  def upload_uniform_vector3fv(self, vector, name):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniform3fv(location, 1, vector)

  def upload_uniform_scalar1f(self, scalar, name):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniform1f(location, scalar)

  def upload_uniform_scalar1i(self, scalar, name):
    GL.glUseProgram(self.shader.render_idx)
    location = GL.glGetUniformLocation(self.shader.render_idx, name)
    GL.glUniform1i(location, scalar)


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
        print(GL.glGetProgramInfoLog(self.render_idx).decode("ascii"))
        sys.exit(1)

  def __del__(self):
    GL.glUseProgram(0)
    if self.render_idx:  # if this is a valid shader object
      GL.glDeleteProgram(self.render_idx)  # object dies => destroy GL object

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
      print("Compile failed for %s\n%s\n%s" % (shader_type, log, src))
      sys.exit(1)
    return shader
