from copy import deepcopy

#************************************************************
#* Expr *****************************************************

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

#************************************************************
#* EmptyExpr ************************************************

class EmptyExpr(Expr):
  def __init__(self):
    pass
  def __repr__(self):
    return '()'

#************************************************************
#* FileExpr *************************************************

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

    # Instance vars # TODO: Loops between them: A = B; B = C; C = A;
    for expr in self.exprs:
      if isinstance(expr, DefExpr):
        expr.exec(scope)

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
      _def = expr.define(scope)
      if not _def is None: # TODO: Also put exported functions at the top
        self.data += _def

    # Compile functions # NOTE: The order doesn't matter
    main = scope.findMainFun()
    for expr in self.exprs:
      if isinstance(expr, FunExpr):
        self.text += expr.comp(scope.child(), isMain = expr == main)

    return self.data, self.text

#************************************************************
#* FunExpr **************************************************

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
      if isinstance(expr, DefExpr): # TODO: Check other types? Like functions
        expr.define(scope)

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

    return self.getText(s, isMain, scope)

  def getText(self, s, isMain, scope):
    text = self.compComment()
    text += '_start:\n' if isMain else ''
    text += f'{self.name}:\n'
    text += '  ; Set the stack frame\n'
    text += '  push rbp\n'
    text += '  mov rbp, rsp\n'

    l = len(scope.varsWithReg('rsp'))
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
      text += '  mov rax, 60\n'
      text += '  syscall\n'
    else:
      text += '  ret\n'
  
    self.text = text
    return self.text

  def define(self, scope):
    scope.defFun(self)

#************************************************************
#* DefExpr **************************************************

class DefExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.value = Expr.construct(expr[3]) if len(expr) > 3 else None
  def __repr__(self):
    return f'(def, {self.name}, {self.value})'

  def define(self, scope):
    scope.defVar(self)

    text = self.compComment()
    text += f'{self.name}: '
    if self.value is None:
      return text + 'dq 0\n' # TODO: Reserve space for it's type
    elif isinstance(self.value, IntrinsicExpr):
      return text + f'{self.value.define()}\n'

  def exec(self, scope):
    print(self)

    var = scope.findVar(self.name)
    if not self.value is None:
      var.value = self.value.exec(scope)

    return var

  def comp(self, scope):
    print(self)
    text = self.compComment()

    self.define(scope)
    var = scope.findVar(self.name)

    if isinstance(self.value, IntrinsicExpr): # TODO: Not all types
      text += f'  mov qword [{var.reg} + {var.offset}], {self.value.comp(scope)}\n' # TODO: qword depends on size
    # elif not is None # TODO: setExpr

    self.text = text
    return self.text

#************************************************************
#* VarExpr **************************************************

class VarExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
  def __repr__(self):
    return f'(var, {self.name})'

  def exec(self, scope):
    print(self)

    var = scope.findVar(self.name)
    if var is None:
      raise Exception('[VarExpr.exec]')

    return var

  def comp(self, scope):
    print(self)
    self.text = ''
    return scope.findVar(self.name) # NOTE: Special

#************************************************************
#* SetExpr **************************************************

class SetExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.A = Expr.construct(expr[1])
    self.B = Expr.construct(expr[2])

  def __repr__(self):
    return f'(set, {self.A}, {self.B})'

  def exec(self, scope):
    print(self)

    A = self.A.exec(scope)
    B = self.B.exec(scope)

    self.checkAndReplaceTypes(A, B)

    if isinstance(self.B, VarExpr):
      A.value = B.value
    # elif isinstance(self.expr, ): # TODO: Other types? Pointers
    else: A.value = B

    return A

  def comp(self, scope):
    print(self)
    text = self.compComment()

    # TODO: Does the order matter?
    A = self.A.comp(scope) 
    B = self.B.comp(scope)

    self.checkAndReplaceTypes(A, B)

    reg = 'rax' # TODO: Alloc a register
    if isinstance(self.B, VarExpr):
      text += f'  mov {reg}, {B.reference()}\n'
    elif isinstance(self.B, IntrinsicExpr): # TODO: Depends on the type
      reg = B
    # elif isinstance(self.B, ): # TODO: Other types
    else:
      text += f'  mov {reg}, {B}\n'

    text += f'  mov qword {A.reference()}, {reg}\n' # TODO: qword depends on type
    
    self.text = text
    return self.text

  def checkAndReplaceTypes(self, A, B): # TODO: Rename
    if not isinstance(self.A, VarExpr):
      raise Exception('[SetExpr] A is not a var:', self)

    # TODO: Clean
    if isinstance(self.B, VarExpr) and A.type != B.type:
      if A.typeless: A.type = B.type
      else: raise Exception('[SetExpr] Wrong types:', self)
    elif isinstance(self.B, IntrinsicExpr) and A.type != self.B.type:
      if A.typeless: A.type = self.B.type
      else: raise Exception('[SetExpr] Wrong types:', self)
    # elif isinstance(self.B, ): # TODO: Other types

#************************************************************
#* ReturnExpr ***********************************************

class ReturnExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = Expr.construct(expr[1])
  def __repr__(self):
    return f'(return, {self.expr})'

  def exec(self, scope):
    res = self.expr.exec(scope)
    if isinstance(self.expr, VarExpr): 
      res = res.value
    # elif isinstance(self.expr, ): # TODO: Other types

    scope.ret = res
    scope.returned = True

  def comp(self, scope):
    text = self.compComment()

    res = self.expr.exec(scope)
    if isinstance(self.expr, VarExpr):
      text += f'  mov rax, {res.reference()}\n'
    # elif isinstance(self.expr, ): # TODO: Other types
    else:
      text += f'  mov rax, {res}\n'

    text += '  jmp .__ret\n'

    self.text = text
    return self.text

#************************************************************
#* IntrinsicExpr ********************************************

class IntrinsicExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.type = expr[0]
    self.value = expr[1]
  def __repr__(self):
    return f'({self.type}, {self.value})'

  def define(self):
    return f'dq {self.value}' # TODO: Depends on the actual type
  def exec(self, scope):
    return self.value
  def comp(self, scope):
    return self.value # TODO: Depends on the actual type

#24
#************************************************************
#* GenericExpr***********************************************

class GenericExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
  def __repr__(self):
    return f'(GENERIC, )'

  # def define(self, scope):
    # pass

  def exec(self, scope):
    print(self)

    return None

  def comp(self, scope):
    print(self)
    text = self.compComment()
    
    self.text = text
    return self.text

#************************************************************
#* Utils ****************************************************

Types = {
  'file': FileExpr,

  'fun': FunExpr,
  'def': DefExpr,
  'var': VarExpr,

  'set': SetExpr,
  'return': ReturnExpr,

  'int64': IntrinsicExpr,
  'int32': IntrinsicExpr,
}
