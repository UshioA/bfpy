import ctypes
from peachpy import *
from peachpy.x86_64 import *
from peachpy.x86_64.registers import *
from ir import *
import sys
c_void_p = ctypes.c_void_p
putchar_address = ctypes.cast(ctypes.windll.msvcrt._write, c_void_p).value
getchar_address = ctypes.cast(ctypes.windll.msvcrt._read, c_void_p).value
func_ptr = Argument(ptr())


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
    self.instr = None
    self.init_function()

  def init_function(self):
    memptr = peachpy.Argument(peachpy.ptr(peachpy.uint8_t))
    with Function('this_is_exec', [memptr], result_type=None) as exec:
      dataptr = r12
      off = r11
      LOAD.ARGUMENT(dataptr, memptr)
      for self.instr in self.oplist:
        if self.instr.opcode == IRType.ADD:
          if self.instr.param > 0:
            ADD([dataptr + self.instr.offset], self.instr.param)
          else:
            SUB([dataptr + self.instr.offset], -self.instr.param)
        elif self.instr.opcode == IRType.SHR:
          if self.instr.param > 0:
            ADD(dataptr, self.instr.param)
          else:
            SUB(dataptr, -self.instr.param)
        elif self.instr.opcode == IRType.LOAD:
          MOV([dataptr + self.instr.offset], self.instr.param)
        elif self.instr.opcode == IRType.MUL:
          x, y = self.instr.param
          y = int(y, 2)
          MOV(al, y)
          MUL([dataptr])
          ADD(al, [dataptr + x])
          MOV([dataptr + x], al)
        elif self.instr.opcode == IRType.OUT:
          if sys.platform == 'win32':
            MOV(rax, putchar_address)
            MOV(rcx, 1)
            LEA(rdx, [dataptr + self.instr.offset])
            MOV(r8, 1)
            SUB(rsp, 32)
            CALL(rax)
            ADD(rsp, 32)
          else:
            if sys.platform == 'darwin':
              MOV(rax, 0x2000004)
            else:
              MOV(rax, 1)
            MOV(rdi, 1)
            MOV(off, self.instr.offset)
            ADD(off, dataptr)
            MOV(rsi, off)
            MOV(rdx, 1)
            SYSCALL()
        elif self.instr.opcode == IRType.IN:
          if sys.platform == 'win32':
            MOV(rax, getchar_address)
            MOV(rcx, 0)
            LEA(rdx, [dataptr + self.instr.offset])
            MOV(r8, 1)
            SUB(rsp, 32)
            CALL(rax)
            ADD(rsp, 32)
          else:
            if sys.platform == 'darwin':
              MOV(rax, 0x2000003)
            else:
              MOV(rax, 0)
            MOV(rdi, 0)
            MOV(off, self.instr.offset)
            ADD(off, dataptr)
            MOV(rsi, off)
            MOV(rdx, 1)
            SYSCALL()
        elif self.instr.opcode == IRType.JZ:
          loop_start_label = Label()
          loop_end_label = Label()
          CMP([dataptr], 0)
          JZ(loop_end_label)
          LABEL(loop_start_label)
          self.bracket_label_stack.append(
              paired_labels(loop_start_label, loop_end_label))
        elif self.instr.opcode == IRType.JNZ:
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
