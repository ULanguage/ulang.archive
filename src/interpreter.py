from scope import Var, Scope
from expr import *
from utils import log

class IVar(Var):
  def __init__(self, value = None, _type = '', typeless = None):
    super().__init__(_type, typeless)
    self.value = value
  def __repr__(self):
    return f'ivar<{self.value}, {self.type}, {self.typeless}>'

  def set(self, B, Bexpr, scope):
    self.checkAndReplaceTypes(B, Bexpr, scope)

    if isinstance(Bexpr, VarExpr):
      self.value = B.value
    # elif isinstance(Bexpr, ): # TODO: Other types? Pointers
    else: self.value = B

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
