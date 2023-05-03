from compiler import Compile
from interpreter import Execute
from expr import Expr

class var_t:
  def __init__(self, t, reg, offset):
    self.type = t
    self.reg = reg
    self.offset = offset 

  def reference(self):
    reg, offset = self.reg, self.offset # Rename
    if reg == 'global': return f'[{offset}]'
    else: return f'[{reg} + {offset}]'

class var_t:
  def __init__(self, value, t):
    self.value = value
    self.type = t
    self.typeless = t == ''
  
  def __repr__(self):
    return f'var<{self.value}, {self.type}, {self.typeless}>'

  def __str__(self):
    t = self.type
    if t in utils.intrinsic: return f'{self.value}'
    else: return repr(self)

if __name__ == '__main__':
  main = Expr.construct(('file', 'main.u',
    ('def', 'globA'),
    ('def', 'globB', ('int64', 1)),
    ('fun', 'getGlob',
      ('return', ('int64', 1)),
    ),
    ('fun', 'setGlob',
      ('return', ('int64', 1)),
    ),
    ('fun', 'main',
      ('def', 'ing', ('int64', 1)),
      ('return', ('int64', 0)),
    ),
  ))

  Execute(main)
  Compile(main, 'main.asm')
