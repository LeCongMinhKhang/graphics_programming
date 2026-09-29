class Light:
  def __init__(
    self,
    position,
    color=(1, 1, 1),
    intensity=1.0,
    # dtype=1,
    # constant=1.0,
    # linear=0.09,
    # quadratic=0.032,
  ):
    self.position = position
    self.color = color
    self.intensity = intensity
    # self.dtype = dtype
    # self.constant = constant
    # self.linear = linear
    # self.quadratic = quadratic
