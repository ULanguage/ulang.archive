from copy import deepcopy

#************************************************************
#* Expr *****************************************************

class Expr:
  def __init__(self, expr):
    self._expr = expr
    self.text = None
  def __repr__(self):
    return f'({self._expr[0]}, ({len(self._expr[1:])})...)'
  def define(self, scope):
    # U: Used to define this expression in the current scope
    print('[define] TODO', self)
    return None
  def exec(self, scope):
    # U: Used to execute this expression in the interpreter
    print('[exec] TODO', self)
    return None
  def comp(self, scope):
    # U: Used to compile this expression
    print('[comp] TODO', self)
    self.text = ''
    return self.text

  def compComment(self):
    return f'\n  ; {self}\n'

  def construct(expr):
    # U: Generic constructor for all expressions
    if isinstance(expr, Expr):
      return deepcopy(expr)
    elif len(expr) == 0:
      return EmptyExpr(expr)

    t = expr[0]
    _class = Types.get(t, Expr)
    return _class(expr)

#************************************************************
#* EmptyExpr ************************************************
# ()
# Does nothing

class EmptyExpr(Expr):
  def __repr__(self):
    return '()'

#************************************************************
#* FileExpr *************************************************
# (file, string path, Expr exprs...)
# Defines a file in the project

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
# (fun, string name, Type returnType, Expr exprs...)
# Describes a function, the expressions are it's actual code

class FunExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.exprs = [Expr.construct(_expr) for _expr in expr[3:]]
  def __repr__(self):
    return f'(fun, {self.name}, {self.type}, ({len(self.exprs)})...)'

  def define(self, scope):
    scope.defFun(self)

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

    return self.getText(scope, s, isMain)

  def getText(self, scope, s, isMain):
    # TODO: Simplify
    text = self.compComment()
    text += '_start:\n' if isMain else ''
    text += f'{self.name}:\n'

    text += self.textBuildSF(scope)

    text += s

    text += '\n'
    if isMain:
      text += '  mov rax, 0 ; By default exit with value 0\n'

    text += self.textRet(scope, isMain)
  
    self.text = text
    return self.text

  def textBuildSF(self, scope):
    text = '  ; Build the stack frame\n'
    text += '  push rbp\n'
    text += '  mov rbp, rsp\n'

    l = len(scope.varsWithReg('rsp'))
    if l != 0:
      text += f'  sub rsp, {l * 8} ; {l} stack vars\n' # TODO: Based on each variable's length
    return text

  def textRet(self, scope, isMain):
    l = len(scope.varsWithReg('rsp'))
    text = '.__ret:\n'
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

    return text

#************************************************************
#* DefExpr **************************************************
# (def, string name, Type type, Expr value)
# Defines a variable

class DefExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.value = Expr.construct(expr[3])
  def __repr__(self):
    return f'(def, {self.name}, {self.value})'

  def define(self, scope):
    scope.defVar(self)

    # NOTE: Only for comp
    text = self.compComment()
    text += f'{self.name}: '
    if isinstance(self.value, EmptyExpr):
      return text + 'dq 0\n' # TODO: Reserve space for it's type
    elif isinstance(self.value, IntrinsicExpr):
      return text + f'{self.value.define()}\n'
    # else: pass # TODO: Other types, queue for main to comp it

  def exec(self, scope):
    print(self)

    var = scope.findVar(self.name)
    if not isinstance(self.value, EmptyExpr):
      var.value = self.value.exec(scope)

    return var

  def comp(self, scope):
    print(self)
    text = self.compComment()

    self.define(scope)
    var = scope.findVar(self.name)

    if isinstance(self.value, IntrinsicExpr): # TODO: Not all types
      text += f'  mov qword [{var.reg} + {var.offset}], {self.value.comp(scope)}\n' # TODO: qword depends on size # TODO: Isn't this also a setExpr?
    elif not isinstance(self.value, EmptyExpr):
      raise Exception('[DefExpr.comp] Not yet supported:', self) # TODO: setExpr 

    self.text = text
    return self.text

#************************************************************
#* VarExpr **************************************************
# (var, string name)
# Gets a variable

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
    return scope.findVar(self.name) # NOTE: Special # TODO: Check like in exec?

#************************************************************
#* SetExpr **************************************************
# (set, Expr into, Expr value)
# Sets value into "into"
# NOTE: For now into should be variable

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

    self.checkAndReplaceTypes(A, B, scope)

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

    self.checkAndReplaceTypes(A, B, scope)

    reg = 'rax' # TODO: Alloc a register
    if isinstance(self.B, VarExpr):
      text += f'  mov {reg}, {B.reference()}\n'
    elif isinstance(self.B, CallExpr):
      text += B
      reg = 'rax' # TODO: Multiple returns
    elif isinstance(self.B, IntrinsicExpr): # TODO: Depends on the type
      reg = B
    # elif isinstance(self.B, ): # TODO: Other types
    else:
      text += f'  mov {reg}, {B}\n'

    text += f'  mov qword {A.reference()}, {reg}\n' # TODO: qword depends on type
    
    self.text = text
    return self.text

  def checkAndReplaceTypes(self, A, B, scope): # TODO: Rename
    if not isinstance(self.A, VarExpr):
      raise Exception('[SetExpr] A is not a var:', self)

    # TODO: Clean
    if isinstance(self.B, VarExpr) and A.type != B.type:
      if A.typeless: A.type = B.type
      else: raise Exception('[SetExpr] Wrong types:', self)
    elif isinstance(self.B, IntrinsicExpr) and A.type != self.B.type:
      if A.typeless: A.type = self.B.type
      else: raise Exception('[SetExpr] Wrong types:', self)
    elif isinstance(self.B, CallExpr):
      hack = Expr.construct(('fun', self.B.name, '')) 
      fun = scope.findFun(hack) # TODO: Use signature
      if A.type != fun.type:
        if A.typeless: A.type = fun.type
        else: raise Exception('[SetExpr] Wrong types:', self)
    # elif isinstance(self.B, ): # TODO: Other types

#************************************************************
#* CallExpr *************************************************
# (call, string name)
# Calls a function with that name

class CallExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
  def __repr__(self):
    return f'(call, {self.name})'

  def exec(self, scope):
    print(self)

    hack = Expr.construct(('fun', self.name, '')) 
    fun = scope.findFun(hack) # TODO: Use signature

    sibling = scope.sibling()

    # TODO: Templated types
    # TODO: Params

    return fun.exec(sibling)

  def comp(self, scope):
    print(self)
    text = self.compComment()
  
    hack = Expr.construct(('fun', self.name, '')) 
    fun = scope.findFun(hack) # TODO: Use signature

    # TODO: Templated types? Should've been compiled
    # TODO: Params

    text += f'  call {fun.name}\n'
    
    self.text = text
    return self.text

#************************************************************
#* ReturnExpr ***********************************************
# (return, Expr expr)
# Exits from a function with the value of expr

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
    elif isinstance(self.expr, IntrinsicExpr):
      res = self.expr
    # elif isinstance(self.expr, ): # TODO: Other types

    scope.ret = res
    scope.returned = True

  def comp(self, scope):
    text = self.compComment()

    res = self.expr.exec(scope) # TODO: Shouldn't this be comp? # URGENT
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
# (int64, int64 value), (int32, int32 value)
# Intrinsic types

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

#26, number of lines for the GenericExpr
#************************************************************
#* GenericExpr***********************************************
# ()
# Generic expression used only to copy and paste the skeleton code

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
  'call': CallExpr,
  'return': ReturnExpr,

  'int64': IntrinsicExpr,
  'int32': IntrinsicExpr,
}
