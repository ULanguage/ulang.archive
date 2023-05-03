from copy import deepcopy

class Expr:
  def __init__(self, expr):
    self._expr = expr
    self.text = None
  def __repr__(self):
    return f'({self._expr[0]}, ({len(self._expr[1:])})...)'
  def exec(self, scope):
    print('[exec] TODO', self)
    return None
  def comp(self, scope):
    print('[comp] TODO', self)
    self.text = ''
    return self.text
  def define(self, scope):
    print('[define] TODO', self)
    return None

  def compComment(self):
    return f'\n  ; {self}\n'

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
    self.data = ''
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

  def comp(self, scope, isMain = False):
    print(self)
    self.data = ''
    self.text = ''

    # Define vars, types, funs # TODO: Anything else? options, libname, import
    for expr in self.exprs:
      # TODO: Check types?
      expr.define(scope)

    # Compile functions # NOTE: The order doesn't matter
    main = scope.findMainFun()
    for expr in self.exprs:
      if isinstance(expr, FunExpr):
        self.text += expr.comp(scope.child(), isMain = expr == main)

    return self.data, self.text

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

  def comp(self, scope, isMain = False):
    print(self)
    s = ''

    # TODO: If isMain instance global vars with (default) values
    # TODO: Params

    # Compile expressions in order
    for expr in self.exprs:
      # TODO: Check types?
      s += expr.comp(scope)

    return self.getText(s, isMain)

  def getText(self, s, isMain):
    text = self.compComment()
    text += '_start:\n' if isMain else ''
    text += f'{self.name}:\n'
    text += '  ; Set the stack frame\n'
    text += '  push rbp\n'
    text += '  mov rbp, rsp\n'

    l = 0 # TODO: Stack
    if l != 0:
      text += f'  sub rsp, {l * 8} ; {l} stack vars\n' # TODO: Based on each variable's length

    text += s

    text += '\n'
    if isMain:
      text += '  mov rax, 0 ; By default exit with value 0\n'
    text += '.__ret:\n'
    text += '  ; Remove the stack frame\n'
    if l != 0:
      text += f'  add rsp, {l * 8}\n' # TODO: Based on each variable's length
    text += '  pop rbp\n'

    if isMain:
      text += '  ; Exit\n'
      text += '  mov rdi, rax\n' 
      text += '  mov rax, 0\n'
      text += '  syscall\n'
    else:
      text += '  ret\n'
  
    self.text = text
    return self.text

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

  def comp(self, scope):
    text = self.compComment()

    res = self.expr.exec(scope) # TODO: Depends on it's type

    text += f'  mov rax, {res}\n'
    text += '  jmp .__ret\n'

    self.text = text
    return self.text

class IntrinsicExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.type = expr[0]
    self.value = expr[1]
  def __repr__(self):
    return f'({self.type}, {self.value})'

  def exec(self, scope):
    return self.value
  def comp(self, scope):
    return self.value # TODO: Depends on the actual type

Types = {
  'file': FileExpr,
  'fun': FunExpr,
  'return': ReturnExpr,

  'int64': IntrinsicExpr,
}

