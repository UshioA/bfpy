import op
import sys
from op import Opcode

class VM:
    def __init__(self):
        pass


class InterpretVM(VM):
    def __init__(self, oplist: list[op.Op], tape_len=1 << 27):
        self.oplist = oplist
        self.tape = bytearray(tape_len)
        self.program_counter = 0
        self.tape_pointer = 0
        self.tape_len = tape_len

    def reset(self):
        self.tape_pointer = self.program_counter = 0

    def do_shl(self):
        self.tape_pointer -= 1
        if self.program_counter < 0:
            raise MemoryError
        self.program_counter+=1

    def do_shr(self):
        self.tape_pointer += 1
        if self.tape_pointer >= self.tape_len:
            self.tape.extend(bytearray(self.tape_len))
            self.tape_len <<= 1
        self.program_counter+=1

    def do_add(self):
        self.tape[self.tape_pointer] = sum([1, self.tape[self.tape_pointer]]) & 0xff
        self.program_counter+=1
        

    def do_sub(self):
        self.tape[self.tape_pointer] = sum([1, ~1, self.tape[self.tape_pointer]])&0xff
        self.program_counter+=1

    def do_in(self):
        c = sys.stdin.read(1)
        if c:
          self.tape[self.tape_pointer] = ord(c)
        self.program_counter+=1

    def do_out(self):
        sys.stdout.write(chr(self.tape[self.tape_pointer]))
        sys.stdout.flush()
        self.program_counter+=1

    def do_jz(self):
        if self.tape[self.tape_pointer] == 0:
            self.program_counter = self.oplist[self.program_counter].jmptarget
            return
        self.program_counter+=1

    def do_jnz(self):
        if self.tape[self.tape_pointer]:
            self.program_counter = self.oplist[self.program_counter].jmptarget
            return
        self.program_counter+=1
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