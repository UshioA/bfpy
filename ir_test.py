from vm import IRVM
from op_gen import op_gen
from ir_gen import *
if __name__=='__main__':
  s = input()
  text = str(s)
  while s:
    s =input()
    text += s
  # for i,j in enumerate(ir_gen(op_gen(text))):
  #   print(i,j)
  irvm = IRVM(ir_gen(op_gen(text)))
  irvm.exec()