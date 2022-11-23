import ctypes
from peachpy import *
from peachpy.x86_64 import *
from ir import *
import sys


class paired_labels:
  def __init__(self, start, end) -> None:
    self.start_label = start
    self.end_label = end


class JitVM:
  def __init__(self, oplist: list[IR], tape_len: int = 1 << 27):
    self.tape_len = tape_len
    self.oplist = oplist
    self.tape_pointer = 0
    self.program_counter = 0
    self.bracket_label_stack = []
    self.abi = peachpy.x86_64.abi.detect()
    self.init_function()

  def init_function(self):
    self.memptr = peachpy.Argument(peachpy.ptr(peachpy.uint8_t))
    with peachpy.x86_64.Function('is_this_one_step', [self.memptr], result_type=None) as exec:
      dataptr = peachpy.x86_64.r13
      off = peachpy.x86_64.r12
      peachpy.x86_64.LOAD.ARGUMENT(dataptr, self.memptr)
      for instr in self.oplist:
        if instr.opcode == IRType.ADD:
          if instr.param > 0:
            peachpy.x86_64.ADD([dataptr + instr.offset], instr.param)
          else:
            peachpy.x86_64.SUB([dataptr + instr.offset], -instr.param)
        elif instr.opcode == IRType.SHR:
          if instr.param > 0:
            peachpy.x86_64.ADD(dataptr, instr.param)
          else:
            peachpy.x86_64.SUB(dataptr, -instr.param)
        elif instr.opcode == IRType.OUT:
          if sys.platform == 'darwin':
            peachpy.x86_64.MOV(peachpy.x86_64.rax, 0x2000004)
          else:
            peachpy.x86_64.MOV(peachpy.x86_64.rax, 1)
          peachpy.x86_64.MOV(peachpy.x86_64.rdi, 0)
          peachpy.x86_64.MOV(off, instr.offset)
          peachpy.x86_64.ADD(off, dataptr)
          peachpy.x86_64.MOV(peachpy.x86_64.rsi, off)
          peachpy.x86_64.MOV(peachpy.x86_64.rdx, 1)
          peachpy.x86_64.SYSCALL()
        elif instr.opcode == IRType.IN:
          if sys.platform == 'darwin':
            peachpy.x86_64.MOV(peachpy.x86_64.rax, 0x2000003)
          else:
            peachpy.x86_64.MOV(peachpy.x86_64.rax, 0)
          peachpy.x86_64.MOV(peachpy.x86_64.rdi, 0)
          peachpy.x86_64.MOV(off, instr.offset)
          peachpy.x86_64.ADD(off, dataptr)
          peachpy.x86_64.MOV(peachpy.x86_64.rsi, off)
          peachpy.x86_64.MOV(peachpy.x86_64.rdx, 1)
        elif instr.opcode == JZ:
          loop_start_label = peachpy.x86_64.Label()
          loop_end_label = peachpy.x86_64.Label()
          peachpy.x86_64.CMP([dataptr], 0)
          peachpy.x86_64.JZ(loop_end_label)
          peachpy.x86_64.LABEL(loop_start_label)
          self.bracket_label_stack.append(
            paired_labels(loop_start_label, loop_end_label))
        elif instr.opcode == JNZ:
          assert len(self.bracket_label_stack), '怎么会是呢'
          label_pair = self.bracket_label_stack.pop()
          peachpy.x86_64.CMP([dataptr], 0)
          peachpy.x86_64.JNZ(label_pair.start_label)
          peachpy.x86_64.LABEL(label_pair.end_label)
      peachpy.x86_64.RETURN()
    self.encoded_exec = exec.finalize(self.abi).encode()
    self.python_exec = self.encoded_exec.load()

  def exec(self):
    memsize = self.tape_len
    MemoryArrayType = ctypes.c_uint8 * memsize
    memory = MemoryArrayType(*([0] * memsize))
    self.python_exec(memory)
