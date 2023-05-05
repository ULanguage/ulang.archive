import sys
import argparse

logMask = [
  'error',
  'user',
  'debug',
  # 'deepDebug',
]

dfltO = 'main.asm'
dfltComp = False

def parseArgs():
  parser = argparse.ArgumentParser(
    prog = f'ulang',
    description = '', #TODO: Better description
    epilog = 'Made by Galileo Cappella\nVisit https://dev.galileocap.me/ulang',

    formatter_class = argparse.RawTextHelpFormatter,
  )

  parser.add_argument(
    '--compile', default = dfltComp, action = 'store_true',
    help = f'Should compile the file (default: "{dfltComp}")',
  )
  parser.add_argument(
    '-o', default = dfltO,
    help = f'Output path for the compiled file (default: "{dfltO}")',
  )

  return parser.parse_args()

def log(*args, level):
  if level in logMask:
    print(*args)

def error(*args, scope = None, expr = None):
  log('ERROR:', *args, scope, expr, level = 'error')
  sys.exit(1)
