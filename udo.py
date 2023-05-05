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

def Taskexec():
  return {
    'deps': PYSRC + USRC,
    'capture': 1,

    'actions': [
      f'python {SRCD}/main.py',
    ],
  }

def Taskcomp():
  oPath = ASMSRC[:-3] + "o"

  return {
    'deps': PYSRC + USRC,
    'outs': [BUILDD, ASMSRC, oPath, BIN],
    'capture': 1,

    'actions': [
      f'mkdir -p {BUILDD}',
      f'python {SRCD}/main.py --compile -o {ASMSRC}',
      f'nasm -felf64 {ASMSRC}',
      f'ld {oPath} -o {BIN}',
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
