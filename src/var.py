from expr import *
from debug import log, error

class Var:
  def __init__(self, place, reference, _type):
    self.place = place
    self.reference = reference
    self.type = _type
    self.isPointer = _type.startswith('*')
  def __repr__(self):
    return f'var<{self.place}, {self.reference}, {self.type}>'

  def pointer(self):
    return Var(self.place, self.reference, '*' + self.type) # TODO: Place? Think of passing as argument

  def set(self, newValue, selfExpr, newExpr, scope, asArg = False):
    self.checkTypes(newValue, selfExpr, newExpr, scope)

    text = ''
    reg = 'rax' # TODO: Alloc a register
    if isinstance(newExpr, VarExpr) or isinstance(newExpr, DerefExpr):
      text += f'  mov {reg}, [{newValue.reference}]\n'
    elif isinstance(newExpr, RefExpr):
      text += f'  lea {reg}, [{newValue.reference}]\n'
    elif isinstance(newExpr, CallExpr):
      text += newValue
      reg = 'rax'
    elif isinstance(newExpr, IntrinsicExpr): # TODO: Depends on the type
      reg = newValue
    # elif isinstance(newExpr, EmptyExpr): # TODO: URGENT
    # elif isinstance(newExpr, ): # TODO: Other types
    else:
      text += f'  mov {reg}, {newValue}\n'

    size = ''
    if self.isPointer:
      size = 'qword'
    else:
      match self.type:
        case 'bool' | 'char' | 'int8': size = 'byte'
        case 'int16': size = 'word'
        case 'int32': size = 'dword'
        case 'int64': size = 'qword'

    if asArg:
      text += f'  push {size} {reg}\n'
    elif isinstance(selfExpr, DerefExpr):
      reg2 = 'rbx' # TODO: Alloc register
      text += f'  mov {size} {reg2}, [{self.reference}]\n'
      text += f'  mov {size} [{reg2}], {reg}\n'
    else:
      text += f'  mov {size} [{self.reference}], {reg}\n'

    # TODO: Free reg?

    return text

  def checkTypes(self, newValue, selfExpr, valExpr, scope):
    # TODO: Clean
    theirType = None
    if isinstance(newValue, Var):
      theirType = newValue.type
    elif isinstance(valExpr, IntrinsicExpr):
      theirType = valExpr.type
    elif isinstance(valExpr, CallExpr):
      fun = scope.findFun(valExpr.name)
      theirType = fun.type
    # elif isinstance(valExpr, ): # TODO: Other types of expressions
    else:
      error('[checkTypes] Unhandled expression:', selfExpr, valExpr, scope = scope)

    if self.type != theirType:
      error('[checkTypes] Wrong types:', selfExpr, valExpr, scope = scope)

