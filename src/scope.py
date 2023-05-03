class Scope:
  def __init__(self, parent = None):
    self.parent = parent

    self.funs = dict()
    self.vars = dict()

    self.res = None
    self.returned = False

  def __repr__(self):
    return f'Scope<{not self.parent is None}, {list(self.funs.keys())}>'

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

  def defVar(self, name):
    # TODO: Repeated code with defFun
    if not self.findVar(name) is None:
      raise Exception('[defVar]')
    self.vars[name] = None # TODO: var_t

  def findVar(self, name):
    if name in self.vars:
      return self.vars[name]
    if not self.parent is None:
      return self.parent.findVar(name)
    return None

  def findMainFun(self):
    if not 'main' in self.funs: # NOTE: Only match based on name
      raise Exception('[findMainFun]')
    return self.funs['main']
