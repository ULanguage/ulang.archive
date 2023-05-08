import subprocess

from scope import Scope
from debug import log, error

def Compile(fileExpr, to = 'main.asm'):
  log('[Compile]', fileExpr, to, level = 'debug')

  # TODO: Multiple files
  scope = Scope()
  text = fileExpr.comp(scope, isMain = True)
  
  if to is None:
    print(text)
  else:
    with open(to, 'w') as fout:
      fout.write(text)

  # TODO: Call nasm and ld
