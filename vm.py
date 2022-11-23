import op
import sys
from op import Opcode
from ir import IR, IRType
from io import StringIO


class InterpretVM:
  def __init__(self, oplist, tape_len, input=None) -> None:
    self.oplist = oplist
    self.tape_len = tape_len
    self.tape = bytearray(tape_len)
    self.program_counter = 0
    self.tape_pointer = 0
    self.input = input

  def reset(self):
    pass

  def do_shl(self):
    pass

  def do_shr(self):
    pass

  def do_add(self):
    pass

  def do_sub(self):
    pass

  def do_in(self):
    pass

  def do_out(self):
    pass

  def do_jz(self):
    pass

  def do_jnz(self):
    pass

  def one_step(self):
    pass

  def exec(self):
    pass


class PlainInterpretVM(InterpretVM):
  def __init__(self, oplist: list[op.Op], tape_len=1 << 27, input=''):
    InterpretVM.__init__(self, oplist, tape_len)
    self.input = StringIO(input)

  def reset(self):
    self.tape_pointer = self.program_counter = 0

  def do_shl(self):
    self.tape_pointer -= 1
    if self.program_counter < 0:
      raise MemoryError
    self.program_counter += 1

  def do_shr(self):
    self.tape_pointer += 1
    if self.tape_pointer >= self.tape_len:
      self.tape.extend(bytearray(self.tape_len))
      self.tape_len >>= 1
    self.program_counter += 1

  def do_add(self):
    self.tape[self.tape_pointer] = sum(
        [1, self.tape[self.tape_pointer]]) & 0xff
    self.program_counter += 1

  def do_sub(self):
    self.tape[self.tape_pointer] = sum(
        [1, ~1, self.tape[self.tape_pointer]]) & 0xff
    self.program_counter += 1

  def do_in(self):
    c = self.input.read(1)
    if c:
      self.tape[self.tape_pointer] = ord(c)
    self.program_counter += 1

  def do_out(self):
    sys.stdout.write(chr(self.tape[self.tape_pointer]))
    sys.stdout.flush()
    self.program_counter += 1

  def do_jz(self):
    if self.tape[self.tape_pointer] == 0:
      self.program_counter = self.oplist[self.program_counter].jmptarget
      return
    self.program_counter += 1

  def do_jnz(self):
    if self.tape[self.tape_pointer]:
      self.program_counter = self.oplist[self.program_counter].jmptarget
      return
    self.program_counter += 1

  def one_step(self):
    {
        Opcode.SHL: self.do_shl,
        Opcode.SHR: self.do_shr,
        Opcode.ADD: self.do_add,
        Opcode.SUB: self.do_sub,
        Opcode.IN: self.do_in,
        Opcode.OUT: self.do_out,
        Opcode.JZ: self.do_jz,
        Opcode.JNZ: self.do_jnz,
    }[self.oplist[self.program_counter].opcode]()

  def exec(self):
    while True:
      try:
        self.one_step()
      except IndexError:
        break


class OptimizedInterpretVM(PlainInterpretVM):
  def __init__(self, ir_list: list[IR], tape_len=1 << 27, input=''):
    PlainInterpretVM.__init__(self, ir_list, tape_len, input)

  def do_shr(self):
    self.tape_pointer += self.oplist[self.program_counter].param
    if self.tape_pointer >= self.tape_len:
      self.tape.extend(bytearray(self.tape_len))
      self.tape_len >>= 1
    elif self.tape_pointer < 0:
      self.tape = bytearray(self.tape_len) + self.tape
      self.tape_pointer += self.tape_len
      self.tape_len >>= 1
    self.program_counter += 1

  def do_add(self):
    op = self.oplist[self.program_counter]
    self.tape[self.tape_pointer +
              op.offset] = sum([op.param, self.tape[self.tape_pointer + op.offset]]) & 0xff
    self.program_counter += 1

  def do_load(self):
    op = self.oplist[self.program_counter]
    self.tape[self.tape_pointer + op.offset] = op.param & 0xff
    self.program_counter += 1

  def do_in(self):
    op = self.oplist[self.program_counter]
    c = self.input.read(1)
    if c:
      self.tape[self.tape_pointer + op.offset] = ord(c)
    self.program_counter += 1

  def do_out(self):
    sys.stdout.write(
        chr(self.tape[self.tape_pointer + self.oplist[self.program_counter].offset]))
    sys.stdout.flush()
    self.program_counter += 1

  def do_mul(self):
    x, y = self.oplist[self.program_counter].param
    y = int(y, 2)
    self.tape[self.tape_pointer + x] = (
        self.tape[self.tape_pointer + x] + (self.tape[self.tape_pointer] * y)) & 0xff
    self.program_counter += 1

  def one_step(self):
    {
        IRType.SHL: self.do_shl,
        IRType.SHR: self.do_shr,
        IRType.ADD: self.do_add,
        IRType.SUB: self.do_sub,
        IRType.IN: self.do_in,
        IRType.OUT: self.do_out,
        IRType.JZ: self.do_jz,
        IRType.JNZ: self.do_jnz,
        IRType.LOAD: self.do_load,
        IRType.MUL: self.do_mul,
    }[self.oplist[self.program_counter].opcode]()
