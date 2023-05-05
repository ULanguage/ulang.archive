from scope import Var, Scope
from expr import *
from debug import log

class IVar(Var):
  def __init__(self, value = None, _type = '', typeless = None):
    super().__init__(_type, typeless)
    self.value = value
  def __repr__(self):
    return f'ivar<{self.value}, {self.type}, {self.typeless}>'
  
  def pointer(self):
    return IVar(self, '*' + self.type, False)

  def set(self, newValue, selfExpr, valExpr, scope):
    self.checkAndReplaceTypes(newValue, selfExpr, valExpr, scope)

    if isinstance(valExpr, VarExpr) or isinstance(valExpr, RefExpr):
      self.value = newValue.value
    # elif isinstance(valExpr, ): # TODO: Other types? Pointers
    else: self.value = newValue

class IScope(Scope):
  def __init__(self, parent = None):
    super().__init__(parent)

  def newVar(self, _def):
    return IVar(_type = _def.type)

def Execute(fileExpr):
  log('[Execute]', fileExpr, level = 'debug')

  scope = IScope()
  ret = fileExpr.exec(scope, isMain = True)
  log(f'Exited with {ret}', level = 'user')
