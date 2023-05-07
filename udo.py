# SEE: https://dev.galileocap.me/udo
############################################################
# UTILS ####################################################

import os
from pathlib import Path

UDOConfig = {
  'version': (1, 3, 0)
}

SRCD = './src'
BUILDD = './build'

BIN = os.path.join(BUILDD, 'main')
ASMSRC = os.path.join(BUILDD, 'main.asm')

def filesWithExtension(extension):
  return [ str(fpath) for fpath in list(Path(SRCD).rglob(f'*{extension}')) ]

PYSRC = filesWithExtension('.py')
USRC = filesWithExtension('.u')

############################################################
# Tasks ####################################################

def Taskcomp():
  oPath = ASMSRC[:-3] + "o"

  return {
    'deps': PYSRC + USRC,
    'outs': [BUILDD, ASMSRC, oPath, BIN],
    'capture': 1,

    'actions': [
      f'mkdir -p {BUILDD}',
      f'python {SRCD}/main.py -o {ASMSRC}',
      f'nasm -felf64 {ASMSRC}',
      f'gcc -o {BIN} {oPath}',
    ],
  }

def TaskrunComp():
  return {
    'deps': [BIN],
    'capture': 1,

    'actions': [
      BIN,
      'echo Exited with $?',
    ],
  }
