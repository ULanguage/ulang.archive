from scope import Scope

class CScope(Scope):
  def __init__(self, parent = None):
    super().__init__(parent)

def Compile(fileExpr, to = 'main.asm'):
  print('[Compile]', fileExpr, to)

  scope = CScope()

  top = 'global _start\n'
  data = 'section .data\n'
  text = 'section .text\n'

  _data, _text = fileExpr.comp(scope, isMain = True)
  
  data += _data
  text += _text
  
  res = '\n\n'.join([top, data, text])
  if not to is None:
    with open(to, 'w') as fout:
      fout.write(res)

  return res
