from expr import *
from utils import log, error

class Var:
  def __init__(self, _type = '', typeless = None):
    self.type = _type
    self.typeless = self.type == '' if typeless is None else typeless

  def __repr__(self):
    return f'var<{self.type}, {self.typeless}>'

  def checkAndReplaceTypes(self, B, Bexpr, scope): # TODO: Rename
    # TODO: Clean
    if isinstance(Bexpr, VarExpr) and self.type != B.type:
      if self.typeless: self.type = B.type
      else: error('[checkAndReplaceTypes] Wrong types:', self, Bexpr, scope = scope)
    elif isinstance(Bexpr, IntrinsicExpr) and self.type != Bexpr.type:
      if self.typeless: self.type = Bexpr.type
      else: error('[checkAndReplaceTypes] Wrong types:', self, Bexpr, scope = scope)
    elif isinstance(Bexpr, CallExpr):
      hack = Expr.construct(('fun', Bexpr.name, '', ())) 
      fun = scope.findFun(hack) # TODO: Use signature
      if self.type != fun.type:
        if self.typeless: self.type = fun.type
        else: error('[checkAndReplaceTypes] Wrong types:', self, Bexpr, scope = scope)
    # elif isinstance(self.value, EmptyExpr): # TODO: URGENT
    # elif isinstance(Bexpr, ): # TODO: Other types

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
