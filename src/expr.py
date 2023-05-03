from copy import deepcopy

class Expr:
  def __init__(self, expr):
    self._expr = expr
  def __repr__(self):
    return f'({self._expr[0]}, ({len(self._expr[1:])})...)'
  def exec(self, scope):
    print('[exec] TODO', self)
    return None
  def define(self, scope):
    print('[define] TODO', self)
    return None

  def construct(expr):
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
    self.exprs = [Expr.construct(_expr) for _expr in expr[2:]]
  def __repr__(self):
    return f'(file, {self.path}, ({len(self.exprs)})...)'

  def exec(self, scope, isMain = False):
    print(self)

    # Define vars, types, funs # TODO: Anything else? options, libname, import
    for expr in self.exprs:
      # TODO: Check types?
      expr.define(scope)

    # TODO: Instance vars with (default) values

    # Begin executing main function
    if isMain:
      main = scope.findMainFun()
      return main.exec(scope.child(), isMain = True)

    return None

class FunExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.exprs = [Expr.construct(_expr) for _expr in expr[2:]]
  def __repr__(self):
    return f'(fun, {self.name}, ({len(self.exprs)})...)'

  def exec(self, scope, isMain = False):
    print(self)
    # TODO: JIT?

    # Execute expressions in order
    for expr in self.exprs:
      # TODO: Check types?
      expr.exec(scope)
      if scope.returned:
        break
  
    return scope.ret

  def define(self, scope):
    return scope.defFun(self)

class ReturnExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = Expr.construct(expr[1])
  def __repr__(self):
    return f'(return, {self.expr})'

  def exec(self, scope):
    scope.ret = self.expr.exec(scope)
    scope.returned = True

class IntrinsicExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.type = expr[0]
    self.value = expr[1]
  def __repr__(self):
    return f'({self.type}, {self.value})'

  def exec(self, scope):
    return self.value

Types = {
  'file': FileExpr,
  'fun': FunExpr,
  'return': ReturnExpr,

  'int64': IntrinsicExpr,
}

