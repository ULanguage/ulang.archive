from scope import Var, Scope
from expr import *
from debug import log

class CVar(Var):
  def __init__(self, reg, offset, _type = '', typeless = None):
    super().__init__(_type, typeless)
    self.reg = reg
    self.offset = offset 
  def __repr__(self):
    return f'cvar<{self.reg}, {self.offset}, {self.type}, {self.typeless}>'

  def pointer(self):
    return CVar(self.reg, self.offset, '*' + self.type, False)

  def reference(self):
    reg, offset = self.reg, self.offset # Rename
    if reg == 'global': return f'{offset}'
    else: return f'{reg} + {offset}'

  def set(self, newValue, selfExpr, newExpr, scope, asArg = False):
    self.checkAndReplaceTypes(newValue, selfExpr, newExpr, scope)

    text = ''
    reg = 'rax' # TODO: Alloc a register
    if isinstance(newExpr, VarExpr) or isinstance(newExpr, DerefExpr):
      text += f'  mov {reg}, [{newValue.reference()}]\n'
    elif isinstance(newExpr, RefExpr):
      text += f'  mov {reg}, {newValue.reference()}\n'
    elif isinstance(newExpr, CallExpr):
      text += newValue
      reg = 'rax' # TODO: Multiple returns
    elif isinstance(newExpr, IntrinsicExpr): # TODO: Depends on the type
      reg = newValue
    # elif isinstance(newExpr, EmptyExpr): # TODO: URGENT
    # elif isinstance(newExpr, ): # TODO: Other types
    else:
      text += f'  mov {reg}, {newValue}\n'

    if asArg:
      text += f'  push {reg}\n'
    elif isinstance(selfExpr, DerefExpr):
      reg2 = 'rbx' # TODO: Alloc register
      text += f'  mov qword {reg2}, [{self.reference()}]\n' # TODO: qword depends on type
      text += f'  mov qword [{reg2}], {reg}\n' # TODO: qword depends on type
    else:
      text += f'  mov qword [{self.reference()}], {reg}\n' # TODO: qword depends on type

    # TODO: Free reg?

    return text

class CScope(Scope):
  def __init__(self, parent = None):
    super().__init__(parent)

  def newVar(self, _def):
    reg = 'rsp' if isinstance(_def, DefExpr) else 'rbp'
    offset = (len(self.varsWithReg(reg)) + 2 * int(reg == 'rbp')) * 8 # TODO: 8 depends on each var's size
    if self.parent is None:
      reg = 'global'
      offset = _def.name

    return CVar(reg, offset, _def.type)

  def varsWithReg(self, reg):
    return [var for _, var in self.vars.items() if var.reg == reg]

def Compile(fileExpr, to = 'main.asm'):
  log('[Compile]', fileExpr, to, level = 'debug')

  scope = CScope()

  top = 'global _start\n'
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
