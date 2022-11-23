from peachpy import *
from peachpy.x86_64 import *
from io import StringIO
from ir import *


class JitVM:
  def __init__(self, oplist: list[IR], tape_len: int = 1 << 27, input: str = ''):
    self.tape_len = tape_len
    self.oplist = oplist
    self.tape = bytearray(tape_len)
    self.input = StringIO(input)
    self.tape_pointer = 0
    self.program_counter = 0
  