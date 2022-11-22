import enum

Opcode = enum.Enum("Opcode", "SHL SHR ADD SUB OUT IN JZ JNZ")


class Op:
  def __init__(self, opcode: Opcode, jmptarget: int = -1):
    self.opcode = opcode
    self.jmptarget = jmptarget
