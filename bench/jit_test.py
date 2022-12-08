from jit import JitVM
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
  jitvm = JitVM(code, 4096)
  jitvm.exec()
