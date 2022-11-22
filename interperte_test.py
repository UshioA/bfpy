from vm import InterpretVM
from op_gen import op_gen
if __name__=='__main__':
  s = input()
  text = str(s)
  while s:
    s =input()
    text += s
  ivm = InterpretVM(op_gen(text))
  ivm.exec()