from expr import *
from debug import log, error

class Var:
  def __init__(self, _type):
    self.type = _type
    self.isPointer = _type.startswith('*')
  def __repr__(self):
    return f'var<{self.type}>'

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

class Scope:
  def __init__(self, parent = None):
    self.parent = parent

    self.funs = dict()
    self.vars = dict()

    self.ret = None
    self.returned = False
    self.broke = False

    self.labels = dict()

  def __repr__(self):
    return f'Scope<{not self.parent is None}, {list(self.funs.keys())}, {list(self.vars.keys())}>'

  def child(self):
    return type(self)(parent = self)
  def sibling(self):
    return type(self)(parent = self.parent)

  def defFun(self, fun):
    if not self.findFun(fun.name) is None:
      error(f'[defFun] A function with the name "{fun.name}" already exists', scope = self, expr = fun)
    self.funs[fun.name] = fun

  def findFun(self, name):
    if name in self.funs:
      return self.funs[name]
    if not self.parent is None:
      return self.parent.findFun(name)
    return None

  def defVar(self, _def, local = False):
    if not self.findVar(_def.name, localOnly = local) is None:
      error(f'[defVar] A variable with the name "{_def.name}" already exists', local, scope = self, expr = _def)
    var = self.newVar(_def)
    self.vars[_def.name] = var
    return var

  def findVar(self, name, localOnly = False):
    # TODO: Repeated code with findFun
    if name in self.vars:
      return self.vars[name]
    if not localOnly and not self.parent is None:
      return self.parent.findVar(name)
    return None

  def getLabel(self, label):
    if self.parent is not None and self.parent.parent is not None: # Go upstreams until the function scope # TODO: Simplify
      return self.parent.getLabel(label)

    count = self.labels.get(label, 0)
    self.labels[label] = count + 1
    return f'{label}_{count}'
