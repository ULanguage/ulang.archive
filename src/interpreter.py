from scope import Var, Scope

class IVar(Var):
  def __init__(self, value = None, _type = '', typeless = False):
    super().__init__(_type, typeless)
    self.value = value
  def __repr__(self):
    return f'ivar<{self.value}, {self.type}, {self.typeless}>'

class IScope(Scope):
  def __init__(self, parent = None):
    super().__init__(parent)

  def newVar(self, _def):
    return IVar(_type = _def.type)

def Execute(fileExpr):
  print('[Execute]', fileExpr)

  scope = IScope()
  ret = fileExpr.exec(scope, isMain = True)
  print(f'Exited with {ret}')
