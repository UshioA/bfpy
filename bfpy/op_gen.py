from bfpy.op import Op, Opcode


def op_gen(s: str):
  oplist = []
  jmpstack = []
  for i in s:
    if i == '>':
      oplist.append(Op(Opcode.SHR))
    elif i == '<':
      oplist.append(Op(Opcode.SHL))
    elif i == '+':
      oplist.append(Op(Opcode.ADD))
    elif i == '-':
      oplist.append(Op(Opcode.SUB))
    elif i == '.':
      oplist.append(Op(Opcode.OUT))
    elif i == ',':
      oplist.append(Op(Opcode.IN))
    elif i == '[':
      jmpstack.append(len(oplist))
      oplist.append(Op(Opcode.JZ, len(oplist)))
    elif i == ']':
      pair = jmpstack.pop()
      jnz = Op(Opcode.JNZ, pair + 1)
      oplist[pair].jmptarget = len(oplist) + 1
      oplist.append(jnz)
    else:
      continue
  if len(jmpstack):
    raise SyntaxError
  return oplist
