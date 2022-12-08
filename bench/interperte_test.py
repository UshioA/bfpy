from vm import PlainInterpretVM
from op_gen import op_gen
from time import time
import sys
if __name__ == '__main__':
  argv = sys.argv
  if len(argv) > 1:
    with open(argv[1], 'r') as f:
      text = ''.join(f.readlines())
  t1 = time()
  i = ''
  if len(argv) > 2:
    i = '\n'.join(argv[2:] + ['\n'])
  ivm = PlainInterpretVM(op_gen(text), input=i)
  ivm.exec()
  print(time() - t1)
