from scope import Var, Scope
from expr import *
from debug import log

class IVar(Var):
  def __init__(self, value, _type):
    super().__init__(_type)
    self.value = value
  def __repr__(self):
    return f'ivar<{self.value}, {self.type}>'
  
  def pointer(self):
    return IVar(self, '*' + self.type)

  def set(self, newValue, selfExpr, valExpr, scope):
    self.checkTypes(newValue, selfExpr, valExpr, scope)

    if isinstance(valExpr, VarExpr) or isinstance(valExpr, RefExpr):
      self.value = newValue.value
    # elif isinstance(valExpr, ): # TODO: Other types? Pointers
    else: self.value = newValue

class IScope(Scope):
  def __init__(self, parent = None):
    super().__init__(parent)

  def newVar(self, _def):
    return IVar(None, _def.type)

def Execute(fileExpr):
  log('[Execute]', fileExpr, level = 'debug')

  scope = IScope()
  ret = fileExpr.exec(scope, isMain = True)
  log(f'Exited with {ret}', level = 'user')
