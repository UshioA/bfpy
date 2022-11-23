from vm import OptimizedInterpretVM
from op_gen import op_gen
from time import time
from optimize_gen import *
from io import StringIO
import sys
if __name__ == '__main__':
  argv = sys.argv
  if len(argv) > 1:
    with open(argv[1], 'r') as f:
      text = ''.join(f.readlines())
  code = optimize_gen(op_gen(text))
  # for i, j in enumerate(code):
  #   print(i, j)
  i = ''
  if len(argv) > 2:
    i = '\n'.join(argv[2:] + ['\n'])
  irvm = OptimizedInterpretVM(code, input=i)
  t1 = time()
  irvm.exec()
  print()
  print(time() - t1)
