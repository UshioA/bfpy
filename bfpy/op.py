from bfpy import *
import enum

Opcode = enum.Enum("Opcode", "SHL SHR ADD SUB OUT IN JZ JNZ")

text_table = {
    Opcode.SHL: 'pointer left',
    Opcode.SHR: 'pointer right',
    Opcode.ADD: 'increase',
    Opcode.SUB: 'decrease',
    Opcode.OUT: 'putchar',
    Opcode.IN: 'getchar',
    Opcode.JZ: 'jump if zero',
    Opcode.JNZ: 'jump if nonzero'
}


class Op:
  def __init__(self, opcode: Opcode, jmptarget: int = -1):
    self.opcode = opcode
    self.jmptarget = jmptarget

  def for_human(self):
    return text_table[self.opcode]
