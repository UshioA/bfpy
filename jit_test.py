from jit import JitVM
from op_gen import op_gen
from time import time
from optimize_gen import *
from io import StringIO
import sys
if __name__ == '__main__':
  if sys.platform == 'win32':
    print("""Sorry you r using win32 platform so IO is not supported. 
Writing assembly with peachpy for Windows turned out to be hard to me.
Fortunately all other functions remains the same.""")
  argv = sys.argv
  if len(argv) > 1:
    with open(argv[1], 'r') as f:
      text = ''.join(f.readlines())
  code = optimize_gen(op_gen(text))
  jitvm = JitVM(code, 4096)
  t1 = time()
  jitvm.exec()
  print()
  print(time() - t1)
