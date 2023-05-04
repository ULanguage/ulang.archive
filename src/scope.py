class Var:
  def __init__(self, _type = '', typeless = False):
    self.type = _type
    self.typeless = typeless or _type == ''
  def __repr__(self):
    return f'var<{self.type}, {self.typeless}>'

class Scope:
  def __init__(self, parent = None):
    self.parent = parent

    self.funs = dict()
    self.vars = dict()

    self.ret = None
    self.returned = False

  def __repr__(self):
    return f'Scope<{not self.parent is None}, {list(self.funs.keys())}, {list(self.vars.keys())}>'

  def child(self):
    return type(self)(parent = self)
  def sibling(self):
    return type(self)(parent = self.parent)

  def defFun(self, fun):
    if not self.findFun(fun) is None:
      raise Exception('[defFun]')
    self.funs[fun.name] = fun # TODO: Define based on full name/params/resultType

  def findFun(self, fun):
    if fun.name in self.funs: # TODO: Match based on full name/params/resultType
      return self.funs[fun.name]
    if not self.parent is None:
      return self.parent.findFun(fun)
    return None

  def defVar(self, _def):
    # TODO: Repeated code with defFun
    if not self.findVar(_def.name) is None:
      raise Exception('[defVar]')
    var = self.newVar(_def)
    self.vars[_def.name] = var
    return var

  def findVar(self, name):
    # TODO: Repeated code with findFun
    if name in self.vars:
      return self.vars[name]
    if not self.parent is None:
      return self.parent.findVar(name)
    return None

  def findMainFun(self):
    if not 'main' in self.funs: # NOTE: Only match based on name
      raise Exception('[findMainFun]')
    return self.funs['main']
