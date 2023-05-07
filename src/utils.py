import sys
import argparse

dfltO = 'main.asm'
dfltLogMask = 'user,error'
dfltDebugMask = ''

def parseArgs():
  parser = argparse.ArgumentParser(
    prog = f'ulang',
    description = '', #TODO: Better description
    epilog = 'Made by Galileo Cappella\nVisit https://dev.galileocap.me/ulang',

    formatter_class = argparse.RawTextHelpFormatter,
  )

  parser.add_argument(
    '-o', default = dfltO,
    help = f'Output path for the compiled file (default: "{dfltO}")',
  )

  parser.add_argument(
    '--logMask', default = dfltLogMask,
    help = f'Comma separated list of masks for logging (default: "{dfltLogMask}")',
  )
  parser.add_argument(
    '--debugMask', default = dfltDebugMask,
    help = f'Comma separated list of masks for debug (default empty)',
  )

  return parser.parse_args()
