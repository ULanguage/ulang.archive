from expr import *
from debug import log, error

class Var:
  def __init__(self, _type = '', typeless = None):
    self.type = _type
    self.typeless = self.type == '' if typeless is None else typeless
  def __repr__(self):
    return f'var<{self.type}, {self.typeless}>'

  def checkAndReplaceTypes(self, newValue, selfExpr, valExpr, scope):
    # TODO: Clean
    if isinstance(newValue, Var) and self.type != newValue.type:
      if not self.typeless:
        error('[checkAndReplaceTypes] Wrong types:', self, valExpr, scope = scope)
      self.type = newValue.type
    elif isinstance(valExpr, IntrinsicExpr) and self.type != valExpr.type:
      if not self.typeless:
        error('[checkAndReplaceTypes] Wrong types:', self, valExpr, scope = scope)
      self.type = valExpr.type
    elif isinstance(valExpr, CallExpr):
      hack = Expr.construct(('fun', valExpr.name, '', ())) 
      fun = scope.findFun(hack) # TODO: Use signature
      if self.type != fun.type:
        if not self.typeless:
          error('[checkAndReplaceTypes] Wrong types:', self, valExpr, scope = scope)
        self.type = fun.type
    elif isinstance(valExpr, EmptyExpr): # TODO: URGENT
      error('[checkAndReplaceTypes] EmptyExpr', self, valExpr, scope = scope)
    # elif isinstance(valExpr, ): # TODO: Other types

  def isPointer(self):
    return self.type.startswith('*')

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
      error('[defFun]', scope = self, expr = fun)
    self.funs[fun.name] = fun # TODO: Define based on full name/params/resultType

  def findFun(self, fun):
    if fun.name in self.funs: # TODO: Match based on full name/params/resultType
      return self.funs[fun.name]
    if not self.parent is None:
      return self.parent.findFun(fun)
    return None

  def defVar(self, _def, local = False):
    # TODO: Repeated code with defFun
    if not self.findVar(_def.name, localOnly = local) is None:
      error('[defVar]', local, scope = self, expr = _def)
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

  def findMainFun(self):
    if not 'main' in self.funs: # NOTE: Only match based on name
      error('[findMainFun]', scope = self)
    return self.funs['main']
