import enum

IRType = enum.Enum('IRType', "SHL SHR ADD SUB IN OUT JZ JNZ")


class IR:
  def __init__(self, irtype:IRType, jmptarget=-1, param=-1):
    self.ir_type = irtype
    self.target = jmptarget
    self.param = param

  def __repr__(self):
    return f'IR<{self.ir_type}, {self.target}, {self.param}>'
