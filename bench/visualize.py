import subprocess
import vm
from op import Opcode, Op
from vm import PlainInterpretVM
from vm import OptimizedInterpretVM
import jit
from jit import JitVM
import ir
from ir import IRType, IR
from op_gen import *
from io import StringIO
from optimize_gen import optimize_gen, fold_gen
import os
import sys
import argparse
import multiprocessing


def do_cli_vm(optimize, jit, ir, _input, _file):
  input_ = _input + '\n'
  text = ''
  if _file:
    with open(_file, 'r') as f:
      text = ''.join(f.readlines())
  code_stream = op_gen(text)
  ir_stream = None
  if optimize:
    ir_stream = optimize_gen(code_stream)
  else:
    ir_stream = fold_gen(code_stream)
  if jit:
    vm = JitVM(ir_stream, 4096)
  elif ir:
    vm = OptimizedInterpretVM(ir_stream, input=input_)
  else:
    vm = PlainInterpretVM(code_stream, input=input_)
  vm.exec()


def do_gui_vm(optimize, ir, _input, _file):
  import pygame
  pygame.init()
  pygame.display.set_caption('brainfuck visualize')
  icon = pygame.image.load('icon.jpg')
  pygame.display.set_icon(icon)
  font = pygame.font.SysFont('monospace', 35, False, False)
  screen = pygame.display.set_mode([1280, 720])
  str_out = StringIO()
  input_ = _input + '\n'
  text = ''
  if _file:
    with open(_file, 'r') as f:
      text = ''.join(f.readlines())
  ir_stream = None
  code_stream = op_gen(text)
  if optimize:
    ir_stream = optimize_gen(code_stream)
  else:
    ir_stream = fold_gen(code_stream)
  if ir:
    pvm = OptimizedInterpretVM(ir_stream, input=input_, output=str_out)
  else:
    pvm = PlainInterpretVM(code_stream, input=input_, output=str_out)
  proceed = False
  i = 0
  while pvm.program_counter < len(pvm.oplist):
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
          proceed = True
        elif event.key == pygame.K_SPACE:
          pvm.one_step()
      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT:
          proceed = False
    if proceed:
      pvm.one_step()
    pygame.draw.line(screen, (0, 0, 0), [960, 0], [960, 720])
    rect = pygame.Rect(960, 0, 320, 40)
    screen.fill(pygame.color.Color(60, 179, 113), rect)
    for i in range(18):
      if pvm.program_counter + i >= len(pvm.oplist):
        break
      screen.blit(font.render(
          f'{pvm.oplist[pvm.program_counter + i].for_human()}', True, (0, 0, 0)), rect)
      rect.update(rect.left, rect.top + 40, rect.width, rect.height)
    box = pygame.Rect(0, 480, 120, 120)
    pygame.draw.line(screen, (0, 0, 0), [0, 478], [960, 478], 2)
    pygame.draw.line(screen, (0, 0, 0), [0, 600], [960, 600], 2)
    for i in range(8):
      pygame.draw.rect(screen, (255, 255, 255), box, 120)
      box.update(box.left + 120, box.top, box.width, box.height)
    screen.fill((60, 179, 113), pygame.Rect(360, 480, 120, 120))
    for i in range(8):
      pygame.draw.line(screen, (0, 0, 0), [
                      (i + 1) * 120, 480], [(i + 1) * 120, 600])
    box = pygame.Rect(0, 480, 120, 120)
    for i in range(8):
      screen.blit(font.render(
          hex(pvm.tape[pvm.tape_pointer - 3 + i]), True, (0, 0, 0)), box)
      box.update(box.left + 120, box.top, box.width, box.height)
    screen.blit(font.render(
        f'mem at {pvm.tape_pointer}', 1, (65, 105, 255)), pygame.Rect(0, 601, 960, 100))
    screen.blit(font.render(f'pc at {pvm.program_counter}', 1, (65, 105, 255)), pygame.Rect(
        0, 601 + font.size(' ')[1], 960, 100))
    c = pvm.out_put.getvalue()
    stdout_rect = pygame.Rect(0, 0, 960, 100)
    if c:
      for i in c:
        i = i.replace('\n', '\\n')
        screen.blit(font.render(i.replace(
            '\n', '\\n'), True, (0, 0, 0)), stdout_rect)
        stdout_rect.update(stdout_rect.left + font.size(i)
                           [0], stdout_rect.top, stdout_rect.width, stdout_rect.height)
        if stdout_rect.left >= 960 - font.size('  ')[0]:
          stdout_rect.update(0, stdout_rect.top + font.size(i)
                             [1], stdout_rect.width, stdout_rect.height)
    pygame.display.flip()
  screen.fill((255, 255, 255))
  c = pvm.out_put.getvalue()
  stdout_rect = pygame.Rect(0, 0, 960, 100)
  if c:
    for i in c:
      i = i.replace('\n', '\\n')
      screen.blit(font.render(i.replace(
          '\n', '\\n'), True, (0, 0, 0)), stdout_rect)
      stdout_rect.update(stdout_rect.left + font.size(i)
                         [0], stdout_rect.top, stdout_rect.width, stdout_rect.height)
      if stdout_rect.left >= 960 - font.size('  ')[0]:
        stdout_rect.update(0, stdout_rect.top + font.size(i)
                           [1], stdout_rect.width, stdout_rect.height)
  bye = pygame.font.SysFont('serif', 200, 0, 0)
  screen.blit(bye.render('Done!', True, (0, 0, 0)),
              pygame.Rect(360, 210, 640, 360))
  bye = pygame.font.SysFont('serif', 30, 0, 0)
  screen.blit(bye.render('press q to exit', True, (0, 0, 0)),
              pygame.Rect(540, 480, 640, 360))
  pygame.display.flip()
  while True:
    for e in pygame.event.get():
      if e.type == pygame.KEYUP and e.key == pygame.K_q:
        pygame.quit()
        exit(0)
      elif e.type == pygame.QUIT:
        pygame.quit()
        exit(0)


if __name__ == '__main__':
  optimize = False
  arg = argparse.ArgumentParser(description='brainfuck visualizer')
  arg.add_argument('-o', '--optimize', action='store_true',
                   help='turn on to enable optimize, note that only if ir was enabled will this option make sense')
  arg.add_argument('-i', '--input', default='',
                   type=str, help='input to the program')
  arg.add_argument('-f', '--file', default='', type=str, help='bf program')
  arg.add_argument('-g', '--graphic', action='store_true',
                   help='turn on to enable visualize')
  arg.add_argument('-j', '--jit', action='store_true',
                   help='turn on to enable jit(NOT compatible with graphic), with this on, you CANNOT pass input by argument, please use a pipe')
  arg.add_argument('-r', '--ir', action='store_true',
                   help='turn on to enable ir')
  args = arg.parse_args()
  graphic = (not args.jit) and args.graphic
  optimize = args.optimize
  if graphic:
    do_gui_vm(optimize, args.ir, args.input, args.file)
  else:
    do_cli_vm(optimize, args.jit, args.ir, args.input, args.file)