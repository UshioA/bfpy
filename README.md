# bfpy

**bfpy** is a Brainfuck Jit Interpreter written in python.

## Usage

```text
usage: bfpy.py [-h] [-o] [-i INPUT] [-f FILE] [-g] [-j] [-r]

brainfuck visualizer

optional arguments:
  -h, --help            show this help message and exit
  -o, --optimize        turn on to enable optimize, note that only if ir was enabled will this option make sense
  -i INPUT, --input INPUT
                        input to the program
  -f FILE, --file FILE  bf program
  -g, --graphic         turn on to enable visualize
  -j, --jit             turn on to enable jit(NOT compatible with graphic), with this on, you CANNOT pass input by argument, please use a pipe
  -r, --ir              turn on to enable ir
```

### On graphic mode

Hold key `left` to continuously execute step by step, release to stop;Keys `up` and `down` to scroll the output.Key `space` to execute one_step, if you are curious.Press key `j`, and input some `number`, and press `j` again to execute `number` steps before display current status. While executing, screen won't be freshed so it's much faster than holding key `left`. If you input nothing between two pressing `j`, then vm will execute until end. Backspace in `j` mode is supported.

Note that the graphic part is written with pygame, quick-and-dirty, by me **drunk**. You cannot expect too much from it.

## License

**bfpy** is under **LGPLv3**, which is chosen by asking [this web site](https://ufal.github.io/public-license-selector/), for I am not good at licensing. If I made things wrong, please let me know.

## Requirements

This thing uses `peachpy` and `pygame`. `pygame` can be installed directly via pip, while `peachpy` needs **manual** installation(i don't know why but pip just didn't work as expected), the installation guide can be found [here](https://github.com/Maratyszcza/PeachPy/blob/master/README.rst#installation).
