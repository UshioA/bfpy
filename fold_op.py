import enum

IRType = enum.Enum('IRType', "SHL SHR ADD SUB IN OUT JZ JNZ LOAD MUL")


class IR:
  def __init__(self, type: IRType, jmptarget=-1, param=-1, offset=0):
    self.opcode = type
    self.jmptarget = jmptarget
    self.param = param
    self.offset = offset

  def __repr__(self):
    return f'FoldOp<{self.opcode}, {self.jmptarget}, {self.param},{self.offset}>'
