from bfpy import *
import enum

IRType = enum.Enum('IRType', "SHL SHR ADD SUB IN OUT JZ JNZ LOAD MUL")

text_table = {
    IRType.SHL: 'pointer left',
    IRType.SHR: 'pointer right',
    IRType.ADD: 'increase',
    IRType.SUB: 'decrease',
    IRType.OUT: 'putchar',
    IRType.IN: 'getchar',
    IRType.JZ: 'jump if zero',
    IRType.JNZ: 'jump if nonzero',
    IRType.LOAD: 'load value',
    IRType.MUL: 'multiple'
}


class IR:
  def __init__(self, type: IRType, jmptarget=-1, param=-1, offset=0):
    self.opcode = type
    self.jmptarget = jmptarget
    self.param = param
    self.offset = offset

  def __repr__(self):
    return f'IR<{self.opcode}, {self.jmptarget}, {self.param},{self.offset}>'

  def for_human(self):
    return text_table[self.opcode]
