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
    sys.setrecursionlimit(10000)
    self.tape_len = tape_len
    self.oplist = oplist
    self.tape_pointer = 0
    self.program_counter = 0
    self.bracket_label_stack = []
    self.abi = peachpy.x86_64.abi.detect()
    self.init_function()

  def init_function(self):
    memptr = peachpy.Argument(peachpy.ptr(peachpy.uint8_t))
    with Function('is_this_one_step', [memptr], result_type=None) as exec:
      dataptr = r13
      off = r12
      LOAD.ARGUMENT(dataptr, memptr)
      for instr in self.oplist:
        if instr.opcode == IRType.ADD:
          if instr.param > 0:
            ADD([dataptr + instr.offset], instr.param)
          else:
            SUB([dataptr + instr.offset], -instr.param)
        elif instr.opcode == IRType.SHR:
          if instr.param > 0:
            ADD(dataptr, instr.param)
          else:
            SUB(dataptr, -instr.param)
        elif instr.opcode == IRType.LOAD:
          MOV([dataptr + instr.offset], instr.param)
        elif instr.opcode == IRType.MUL:
          x, y = instr.param
          y = int(y, 2)
          MOV(al, y)
          MUL([dataptr])
          # AND(rax, 0xff)
          ADD(al, [dataptr + x])
          MOV([dataptr + x], al)
        elif instr.opcode == IRType.OUT:
          if sys.platform == 'darwin':
            MOV(rax, 0x2000004)
          else:
            MOV(rax, 1)
          MOV(rdi, 1)
          MOV(off, instr.offset)
          ADD(off, dataptr)
          MOV(rsi, off)
          MOV(rdx, 1)
          SYSCALL()
        elif instr.opcode == IRType.IN:
          if sys.platform == 'darwin':
            MOV(rax, 0x2000003)
          else:
            MOV(rax, 0)
          MOV(rdi, 0)
          MOV(off, instr.offset)
          ADD(off, dataptr)
          MOV(rsi, off)
          MOV(rdx, 1)
          SYSCALL()
        elif instr.opcode == IRType.JZ:
          loop_start_label = Label()
          loop_end_label = Label()
          CMP([dataptr], 0)
          JZ(loop_end_label)
          LABEL(loop_start_label)
          self.bracket_label_stack.append(
              paired_labels(loop_start_label, loop_end_label))
        elif instr.opcode == IRType.JNZ:
          assert len(self.bracket_label_stack), '怎么会是呢'
          label_pair = self.bracket_label_stack.pop()
          CMP([dataptr], 0)
          JNZ(label_pair.start_label)
          LABEL(label_pair.end_label)
      RETURN()
    self.encoded_exec = exec.finalize(self.abi).encode()
    self.python_exec = self.encoded_exec.load()

  def exec(self):
    memsize = self.tape_len
    MemoryArrayType = ctypes.c_uint8 * memsize
    memory = MemoryArrayType(*([0] * memsize))
    self.python_exec(memory)
