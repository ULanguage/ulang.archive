from copy import deepcopy
from debug import log, error

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
    log('[define] TODO', self, level = 'error')
    return None
  def exec(self, scope):
    # U: Used to execute this expression in the interpreter
    log('[exec] TODO', self, level = 'error')
    return None
  def comp(self, scope):
    # U: Used to compile this expression
    log('[comp] TODO', self, level = 'error')
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
    _class = ExprTypes.get(t, Expr)
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
    log(self, level = 'deepDebug')

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
    log(self, level = 'deepDebug')
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
# (fun, string name, Type returnType, (Param params...), Expr exprs...)
# Describes a function, the expressions are it's actual code

class FunExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.params = [Expr.construct(_expr) for _expr in expr[3]]
    self.exprs = [Expr.construct(_expr) for _expr in expr[4:]]
  def __repr__(self):
    return f'(fun, {self.name}, {self.type}, {tuple(self.params)}, ({len(self.exprs)})...)'

  def define(self, scope):
    scope.defFun(self)

  def exec(self, scope, isMain = False):
    log(self, level = 'deepDebug')
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
    log(self, level = 'deepDebug')
    s = ''

    # TODO: If isMain instance global vars with (default) values

    # NOTE: Assumes params exist
    for param in self.params:
      param.define(scope)

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
    log(self, level = 'deepDebug')

    var = scope.findVar(self.name)
    if not isinstance(self.value, EmptyExpr):
      var.value = self.value.exec(scope)

    return var

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()

    self.define(scope)
    var = scope.findVar(self.name)

    if isinstance(self.value, IntrinsicExpr): # TODO: Not all types
      text += f'  mov qword [{var.reg} + {var.offset}], {self.value.comp(scope)}\n' # TODO: qword depends on size # TODO: Isn't this also a setExpr?
    elif not isinstance(self.value, EmptyExpr):
      error('[DefExpr.comp] Not yet supported:', scope = scope, expr = self) # TODO: setExpr 

    self.text = text
    return self.text

#************************************************************
#* ParamExpr ************************************************
# (param, string name, Type type, Expr defaultValue)
# Function parameter

class ParamExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.value = Expr.construct(expr[3])
  def __repr__(self):
    return f'(param, {self.name}, {self.type}, {self.value})'

  def define(self, scope):
    return scope.defVar(self, local = True)

  def exec(self, scope):
    log(self, level = 'deepDebug')

    var = scope.findVar(self.name, localOnly = True)
    if var is None:
      var = self.define(scope)
      value = self.value.exec(scope)
      var.set(value, self.value, scope)

    if var.value is None:
      error('[ParamExpr.exec]', scope = scope, expr = self)

    return var

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = ''

    var = scope.findVar(self.name, localOnly = True)
    if var is None:
      var = self.define(scope)
      value = self.value.comp(scope)
      text += var.set(value, self.value, scope, asArg = True)
    
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
    log(self, level = 'deepDebug')
    return self.find(scope)

  def comp(self, scope):
    log(self, level = 'deepDebug')
    self.text = ''
    return self.find(scope) # NOTE: Special within comp, doesn't return any text

  def find(self, scope):
    var = scope.findVar(self.name)
    if var is None:
      error('[VarExpr.find]', scope = scope, expr = self)
    return var

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
    log(self, level = 'deepDebug')

    A = self.A.exec(scope)
    B = self.B.exec(scope)
    A.set(B, self.B, scope)

    return A

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()

    # TODO: Does the order matter?
    A = self.A.comp(scope) 
    B = self.B.comp(scope)

    text += A.set(B, self.B, scope)
    
    self.text = text
    return self.text

#************************************************************
#* CallExpr *************************************************
# (call, string name)
# Calls a function with that name

class CallExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.args = [Expr.construct(arg) for arg in expr[2:]]
  def __repr__(self):
    args = ', '.join([str(arg) for arg in self.args])
    if args != '':
      args = ', ' + args

    return f'(call, {self.name}{args})' 

  def exec(self, scope):
    log(self, level = 'deepDebug')

    hack = Expr.construct(('fun', self.name, '', ())) 
    fun = scope.findFun(hack) # TODO: Use signature

    sibling = scope.sibling()

    # TODO: Templated types

    # Pass args
    if len(self.args) > len(fun.params):
      error('[CallExpr.exec] Too many args:', scope = scope, expr = self)

    # TODO: Named args
    for idx, arg in enumerate(self.args):
      param = fun.params[idx]
      # TODO: Exec a set ; URGENT
  
      # NOTE: The following is just a hack
      # hack = Expr.construct(('param', param.name, param.type, arg))
      # text += hack.exec(sibling)

      var = param.define(sibling)
      value = arg.exec(scope)
      var.set(value, arg, scope)

    # Make sure all params are defined
    for param in fun.params:
      param.exec(sibling)

    return fun.exec(sibling)

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
  
    hack = Expr.construct(('fun', self.name, '', ())) 
    fun = scope.findFun(hack) # TODO: Use signature

    sibling = scope.sibling()

    # TODO: Templated types? Should've been compiled

    # Pass args
    if len(self.args) > len(fun.params):
      error('[CallExpr.comp] Too many args:', scope = scope, expr = self)

    # TODO: Named args
    for idx, arg in enumerate(reversed(self.args)): # NOTE: Params are passed on the stack, thus they're reversed # TDOO: But I'm not doing it right!! URGENT
      param = fun.params[idx] # TODO: Reversed and enumerate cause wrong idx!! URGENT
      # TODO: Exec a set ; URGENT

      var = param.define(sibling)
      value = arg.comp(scope)

      text += var.set(value, arg, scope, asArg = True)

    # Make sure all params are defined
    for param in reversed(fun.params): # NOTE: Params are passed on the stack, thus they're reversed
      text += param.comp(sibling)

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
    # elif isinstance(self.value, EmptyExpr): # TODO: URGENT
    # elif isinstance(self.expr, ): # TODO: Other types

    scope.ret = res
    scope.returned = True

  def comp(self, scope):
    text = self.compComment()

    res = self.expr.comp(scope) # TODO: Shouldn't this be comp? # URGENT
    if isinstance(self.expr, VarExpr):
      text += f'  mov rax, {res.reference()}\n'
    # elif isinstance(self.value, EmptyExpr): # TODO: URGENT
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
    log(self, level = 'deepDebug')

    return None

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
    
    self.text = text
    return self.text

#************************************************************
#* Utils ****************************************************

ExprTypes = {
  'file': FileExpr,

  'fun': FunExpr,
  'def': DefExpr,
  'param': ParamExpr,
  'var': VarExpr,

  'set': SetExpr,
  'call': CallExpr,
  'return': ReturnExpr,

  'int64': IntrinsicExpr,
  'int32': IntrinsicExpr,
}
