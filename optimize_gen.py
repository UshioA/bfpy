from copy import deepcopy
from op_gen import op_gen
from op import Opcode, Op
from ir import *


def fold_reallocate(ir_list: list[IR]) -> list[IR]:
  stack = []
  for i in range(len(ir_list)):
    ir = ir_list[i]
    if ir.opcode == IRType.JZ:
      stack.append(i)
    elif ir.opcode == IRType.JNZ:
      jz = stack.pop()
      ir.jmptarget = jz + 1
      ir_list[jz].jmptarget = i + 1
  return ir_list


def offset_optimize(ir_list: list[IR]) -> list[IR]:
  ir = ir_list[:]
  i = 0
  block_type = (IRType.ADD, IRType.SHR, IRType.OUT,
                IRType.IN, IRType.LOAD, IRType.MUL)
  while i < len(ir):
    while i < len(ir) and ir[i].opcode not in block_type:
      i += 1
    if i >= len(ir):
      break
    j = i
    while j < len(ir) and ir[j].opcode in block_type:
      j += 1
    instr_pack = []
    offset_pack = {}
    order = []
    p = 0
    for op in ir[i:j]:
      if op.opcode == IRType.SHR:
        p += op.param
      elif op.opcode in (IRType.IN, IRType.OUT, IRType.LOAD):
        l = offset_pack.get(p, [])
        for ii in l:
          ii.offset = p
        instr_pack.extend(l)
        op.offset = p
        instr_pack.append(op)
        offset_pack[p] = []
      else:
        if not offset_pack.get(p, []):
          offset_pack[p] = []
        offset_pack[p].append(op)
        order.append(p)

    for off in order:
      l = offset_pack.get(off, [])
      for ii in l:
        ii.offset = off
      instr_pack.extend(l)
      offset_pack[off] = []
    if p:
      instr_pack.append(IR(IRType.SHR, param=p))
    ir = ir[:i] + instr_pack + ir[j:]
    i += len(instr_pack) + 1
  return ir


def mul_optimize(ir_list: list[IR]) -> list[IR]:
  ir = ir_list[:]
  i = 0
  while True:
    while i < len(ir):
      if ir[i].opcode == IRType.JZ:
        break
      i += 1
    else:
      break
    j = i + 1
    while j < len(ir):
      if ir[j].opcode == IRType.JNZ:
        break
      if ir[j].opcode == IRType.JZ:
        i = j
      j += 1
    else:
      break
    if set(op.opcode for op in ir[i + 1:j]) - set([IRType.ADD, IRType.SHR]) != set():
      i = j
      continue
    mem, p = {}, 0
    for op in ir[i + 1:j]:
      if op.opcode == IRType.ADD:
        mem[p + op.offset] = mem.get(p + op.offset, 0) + op.param
      elif op.opcode == IRType.SHR:
        p += op.param
    if p != 0 or mem.get(0, 0) != -1:
      i = j
      continue
    mem.pop(0)
    optblock = [IR(IRType.MUL, param=(p, bin(mem[p])))
                for p in mem]
    ir = ir[:i] + optblock + \
        [IR(IRType.LOAD, param=0)] + ir[j + 1:]
    i += len(optblock) + 2
  return ir


def redundant_optimize(ir_list: list[IR]) -> list[IR]:
  lst = []
  for i in range(len(ir_list)):
    ir = ir_list[i]
    if ir.opcode == IRType.LOAD:
      while i < len(ir_list) and ir_list[i].opcode == IRType.LOAD:
        end = ir_list[i]
        i += 1
      if i < len(ir_list) and ir_list[i].opcode == IRType.IN:
        lst.append(ir_list[i])
        i += 1
      else:
        lst.append(end)
    elif ir.opcode == IRType.ADD:
      if i + 1 < len(ir_list) and ir_list[i + 1].opcode == IRType.IN:
        lst.append(ir_list[i + 1])
        i += 2
      else:
        lst.append(ir)
        i += 1
    else:
      lst.append(ir)
      i += 1
  return lst


def load_optimize(ir_list: list[IR]) -> list[IR]:
  lst = []
  i = 0
  while i < len(ir_list):
    ir = ir_list[i]
    if i + 2 < len(ir_list) and ir.opcode == IRType.JZ and (ir_list[i + 1].opcode == IRType.ADD) and ir_list[i + 2].opcode == IRType.JNZ:
      load_val = 0
      if i + 3 < len(ir_list) and ir_list[i + 3].opcode == IRType.ADD:
        load_val = ir_list[i + 3].param
        i += 1
      i += 3
      lst.append(IR(IRType.LOAD, param=load_val))
    else:
      lst.append(ir)
      i += 1
  return lst


def dead_loop(ir_list: list[IR]) -> list[IR]:
  i = 0
  lst = []
  if not ir_list:
    return lst

  def head_loop():
    nonlocal i
    if ir_list[i].opcode == IRType.JZ:
      skip()

  def _loop():
    dup = False
    nonlocal i
    while i < len(ir_list):
      ir = ir_list[i]
      if ir.opcode == IRType.JZ:
        skip(not dup)
        if not dup:
          dup = True
      else:
        dup = False
        lst.append(ir)
        i += 1

  def skip(push: bool = False):
    nonlocal i
    counter = 0
    if push:
      lst.append(ir_list[i])
    i += 1
    counter += 1
    while counter > 0 and i < len(ir_list):
      if ir_list[i].opcode == IRType.JNZ:
        counter -= 1
      elif ir_list[i].opcode == IRType.JZ:
        counter += 1
      if push:
        lst.append(ir_list[i])
      i += 1
  head_loop()
  _loop()
  return lst


def fold_gen(oplist: list[Op]) -> list[IR]:
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
        if fold.param:
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
        if fold.param:
          ir_list.append(fold)
        if op.opcode in (Opcode.ADD, Opcode.SUB):
          fold = IR(IRType.ADD,
                    param=1 if op.opcode == Opcode.ADD else -1)
          state = 1
        else:
          state = 0
          ir_list.append(IR({Opcode.JZ: IRType.JZ, Opcode.JNZ: IRType.JNZ,
                         Opcode.IN: IRType.IN, Opcode.OUT: IRType.OUT}[op.opcode], op.jmptarget))
  return fold_reallocate(ir_list)


def optimize_gen(oplist: list[Op]) -> list[IR]:
  return fold_reallocate(mul_optimize(offset_optimize(redundant_optimize(load_optimize(dead_loop(fold_gen(oplist)))))))
