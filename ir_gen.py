from sre_constants import OPCODES
from op_gen import op_gen
from op import Opcode, Op
from ir import *

def ir_reallocate(ir_list:list[IR]) -> list[IR]:
  stack=[]
  for i in range(len(ir_list)):
    ir = ir_list[i]
    if ir.ir_type == IRType.JZ:
      stack.append(i)
    elif ir.ir_type == IRType.JNZ:
      jz = stack.pop()
      ir.target = jz+1
      ir_list[jz].target = i+1
  return ir_list

def ir_gen(oplist: list[Op]) -> list[IR]:
  ir_list = []
  state = 0
  fold = None
  for op in oplist:  # 原神怎么你了
    if state == 0:
      if op.opcode in (Opcode.JZ, Opcode.JNZ, Opcode.IN, Opcode.OUT):
        ir_list.append(IR({Opcode.JZ: IRType.JZ, Opcode.JNZ: IRType.JNZ,
                       Opcode.IN: IRType.IN, Opcode.OUT: IRType.OUT}[op.opcode], op.jmptarget))
      elif op.opcode in (Opcode.ADD, Opcode.SUB):
        fold = IR(IRType.ADD, param=(
            1 if op.opcode == Opcode.ADD else -1))
        state = 1
      elif op.opcode in (Opcode.SHR, Opcode.SHL):
        fold = IR(IRType.SHR, param=(
            1 if op.opcode == Opcode.SHR else -1))
        state = 2
    elif state == 1:  # folding add/sub
      if op.opcode == Opcode.ADD:
        fold.param += 1
      elif op.opcode == Opcode.SUB:
        fold.param -= 1
      else:
        ir_list.append(fold)
        if op.opcode in (Opcode.SHR, Opcode.SHL):
          fold = IR(IRType.SHR, param=(
              1 if op.opcode == Opcode.SHR else -1))
          state = 2
        else:
          state = 0
          ir_list.append(IR({Opcode.JZ: IRType.JZ, Opcode.JNZ: IRType.JNZ,
                         Opcode.IN: IRType.IN, Opcode.OUT: IRType.OUT}[op.opcode], op.jmptarget))
    elif state == 2:
      if op.opcode == Opcode.SHR:
        fold.param += 1
      elif op.opcode == Opcode.SHL:
        fold.param -= 1
      else:
        ir_list.append(fold)
        if op.opcode in (Opcode.ADD, Opcode.SUB):
          fold = IR(IRType.ADD, param=1 if op.opcode == Opcode.ADD else -1)
          state = 1
        else:
          state = 0
          ir_list.append(IR({Opcode.JZ: IRType.JZ, Opcode.JNZ: IRType.JNZ,
                         Opcode.IN: IRType.IN, Opcode.OUT: IRType.OUT}[op.opcode], op.jmptarget))
  return ir_reallocate(ir_list)
