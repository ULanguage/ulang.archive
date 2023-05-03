from copy import deepcopy

class Expr:
  def __init__(self, expr):
    self._expr = expr
  def __repr__(self):
    return f'({self._expr[0]}, ({len(self._expr[1:])})...)'

  def generic(expr):
    if isinstance(expr, Expr):
      return deepcopy(expr)
    elif len(expr) == 0:
      return EmptyExpr()

    t = expr[0]
    _class = Types.get(t, Expr)
    return _class(expr)

class EmptyExpr(Expr):
  def __init__(self):
    pass
  def __repr__(self):
    return '()'

class FileExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.path = expr[1]
    self.exprs = [Expr.generic(_expr) for _expr in expr[2:]]
  def __repr__(self):
    return f'(file, {self.path}, ({len(self.exprs)})...)'

class FunExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.exprs = [Expr.generic(_expr) for _expr in expr[2:]]
  def __repr__(self):
    return f'(file, {self.name}, ({len(self.exprs)})...)'

class ReturnExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = expr[1]
  def __repr__(self):
    return f'(return, {self.expr})'

Types = {
  'file': FileExpr,
  'fun': FunExpr,
  'return': ReturnExpr,
}

