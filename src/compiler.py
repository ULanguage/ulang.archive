from scope import Scope
from debug import log, error

def Compile(fileExpr, to = 'main.asm'):
  log('[Compile]', fileExpr, to, level = 'debug')

  scope = Scope()

  top = 'global main\n' # TODO: Multiple files
  data = 'section .data\n'
  text = 'section .text\n'

  _data, _text = fileExpr.comp(scope, isMain = True)
  
  data += _data
  text += _text
  
  res = '\n'.join([top, data, text])
  if not to is None:
    with open(to, 'w') as fout:
      fout.write(res)

  return res
