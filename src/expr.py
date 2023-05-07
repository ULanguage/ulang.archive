from copy import deepcopy
from debug import log, error, debugStep

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
    _class = getExprType(t)
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
    main = scope.findFun('main')
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
      if isinstance(expr, ArithmExpr): # TODO: Temporary, clean
        _s, _ = expr.comp(scope)
        s += _s
      else:
        s += expr.comp(scope)

    return self.getText(scope, s, isMain)

  def getText(self, scope, s, isMain):
    # TODO: Simplify
    text = self.compComment()
    # text += '_start:\n' if isMain else ''
    text += f'{self.name}:\n'

    # TODO: If isMain, receive C args

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

    l = len(scope.varsWithPlace('def'))
    if l != 0:
      text += f'  sub rsp, {l * 8} ; {l} stack vars\n' # TODO: Based on each variable's length
    return text

  def textRet(self, scope, isMain):
    l = len(scope.varsWithPlace('def'))
    text = '.__ret:\n'
    text += '  ; Remove the stack frame\n'
    if l != 0:
      text += f'  add rsp, {l * 8}\n' # TODO: Based on each variable's length
    text += '  pop rbp\n'

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

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()

    self.define(scope)
    var = scope.findVar(self.name)

    if isinstance(self.value, IntrinsicExpr): # TODO: Not all types
      value = self.value.comp(scope)
      hack = Expr.construct(('var', self.name)) # TODO
      text += var.set(value, hack, self.value, scope)
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

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = ''

    var = scope.findVar(self.name, localOnly = True)
    if var is None:
      var = self.define(scope)
      value = self.value.comp(scope)
      text += var.set(value, self, self.value, scope, asArg = True)
    
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

  def comp(self, scope):
    log(self, level = 'deepDebug')
    return self.find(scope) # NOTE: Special within comp, doesn't return any text

  def find(self, scope):
    var = scope.findVar(self.name)
    if var is None:
      error('[VarExpr.find]', scope = scope, expr = self)
    return var

#************************************************************
#* RefExpr **************************************************
# (ref, Expr expr)
# Returns a pointer to whatever is returned by expr (only variables for now)

class RefExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = Expr.construct(expr[1])
  def __repr__(self):
    return f'(ref, {self.expr})'

  def comp(self, scope):
    log(self, level = 'deepDebug')
    var = self.expr.comp(scope)
    return var.pointer()

#************************************************************
#* DerefExpr **************************************************
# (deref, Expr expr)
# Returns the value pointed to by a pointer

class DerefExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = Expr.construct(expr[1])
  def __repr__(self):
    return f'(deref, {self.expr})'

  def comp(self, scope):
    log(self, level = 'deepDebug')

    var = self.expr.comp(scope)
    if not var.isPointer:
      error('[DerefExpr.comp] Var is not a pointer:', var, scope = scope, expr = self)

    res = deepcopy(var)
    res.type = var.type[1:]

    return res

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

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()

    # TODO: Does the order matter?
    A = self.A.comp(scope) 
    B = self.B.comp(scope)

    text += A.set(B, self.A, self.B, scope)
    
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

    for _idx, param in enumerate(reversed(fun.params)): # NOTE: Params are passed on the stack, thus they're reversed
      idx = len(fun.params) - 1 - _idx # Also in reverse
      if idx < len(self.args): # This param is provided
        arg = self.args[idx]

        var = param.define(sibling)
        value = arg.comp(scope)

        text += var.set(value, param, arg, scope, asArg = True)
      else:
        text += param.comp(sibling)

    text += f'  call {fun.name}\n'
    text += f'  add rsp, {len(fun.params) * 8}\n' # Restore the stack # TODO: Depends on the size of the params
    
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

  def comp(self, scope):
    text = self.compComment()

    res = self.expr.comp(scope)
    if isinstance(self.expr, VarExpr):
      text += f'  mov rax, [{res.reference}]\n'
    elif isinstance(self.expr, RefExpr):
      text += f'  lea rax, [{res.reference}]\n'
    # elif isinstance(self.value, EmptyExpr): # TODO: URGENT
    # elif isinstance(self.expr, ): # TODO: Other types
    elif isinstance(self.expr, ArithmExpr):
      text += res[0]
      text += f'  mov rax, {res[1]}\n'
    else:
      text += f'  mov rax, {res}\n'

    text += '  jmp .__ret\n'

    self.text = text
    return self.text

#************************************************************
#* IfExpr ***************************************************
# (if, Expr cond, (Expr truePath...), (Expr falsePath...))

class IfExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.cond = Expr.construct(expr[1])
    self.truePath = [Expr.construct(subexpr) for subexpr in expr[2]]
    self.falsePath = [Expr.construct(subexpr) for subexpr in expr[3]]
  def __repr__(self):
    return f'(if, {self.cond}, ({len(self.truePath)})..., ({len(self.falsePath)}...))'

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
    
    child = scope.child()

    res = self.cond.comp(child) # TODO: Repeated code with ReturnExpr
    if isinstance(self.cond, VarExpr):
      text += f'  mov rax, [{res.reference}]\n'
    # elif isinstance(self.value, EmptyExpr): # TODO: URGENT
    # elif isinstance(self.cond, ): # TODO: Other types
    elif isinstance(self.cond, ArithmExpr):
      text += res[0]
      text += f'  mov rax, {res[1]}\n'
    else:
      text += f'  mov rax, {res}\n'

    trueLabel = child.getLabel('.__true')
    falseLabel = child.getLabel('.__else')
    endLabel = child.getLabel('.__end')

    false = Expr.construct(('bool', False)).comp(scope)
    text += f'  cmp rax, {false}\n' 
    text += f'  je {falseLabel}\n'

    text += f'{trueLabel}:\n'

    for expr in self.truePath:
      text += expr.comp(child)

    text += f'  jmp {endLabel}\n'
    text += f'{falseLabel}:\n'

    for expr in self.falsePath:
      text += expr.comp(child)

    text += f'{endLabel}:\n'

    self.text = text
    return self.text

#************************************************************
#* ArithmExpr ***********************************************
# (+, Expr x, Expr y)
# (-, Expr x, Expr y)
# (*, Expr x, Expr y)
# (/, Expr x, Expr y)
# (%, Expr x, Expr y)
# (&&, Expr x, Expr y)
# (||, Expr x, Expr y)
# (!, Expr x, EmptyExpr)

class ArithmExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.action = expr[0]
    self.x = Expr.construct(expr[1])
    self.y = Expr.construct(expr[2])
  def __repr__(self):
    return f'({self.action}, {self.x}, {self.y})'

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
    
    x = self.fooComp(self.x, scope)
    y = self.fooComp(self.y, scope)

    # TODO: Check they have the same type
    reg = 'rax' # TODO: Alloc register
    text += self.compAction(x, y, reg, scope)

    # TODO: Free register?
    self.text = text
    return self.text, reg

  def compAction(self, x, y, reg, scope):
    text = ''

    match self.action:
      case '+':
        text += f'  mov {reg}, {x}\n'
        text += f'  add {reg}, {y}\n'
      case '-':
        text += f'  mov {reg}, {x}\n'
        text += f'  sub {reg}, {y}\n'
      case '*':
        text += f'  mov {reg}, {x}\n'
        text += f'  imul {reg}, {y}\n' # TODO: unsigned
        text += f'  mov {reg}, rax\n' # TODO: High part
      case '/':
        text += f'  mov {reg}, {x}\n'
        text += f'  idiv qword {y}\n' # TODO: unsigned # TODO: qword depends on size
        text += f'  mov {reg}, rax\n'
      case '%':
        text += f'  mov {reg}, {x}\n'
        text += f'  idiv qword {y}\n' # TODO: unsigned # TODO: qword depends on size
        text += f'  mov {reg}, rdx\n'
      case '&&':
        text += f'  mov {reg}, {x}\n'
        text += f'  and {reg}, {y}\n'
      case '||':
        text += f'  mov {reg}, {x}\n'
        text += f'  or {reg}, {y}\n'
      case '!':
        text += f'  mov {reg}, {x}\n'
        text += f'  not {reg}\n'

    return text

  def fooComp(self, expr, scope):
    x = expr.comp(scope)
    if isinstance(expr, VarExpr) or isinstance(expr, DerefExpr):
      return f'[{x.reference}]'
    elif isinstance(expr, IntrinsicExpr) or (isinstance(expr, EmptyExpr) and expr == self.y and self.action == '!'):
      return x
    # elif isinstance(expr, ): # TODO: Other types
    else:
      error('[ArithmExpr] Type not supported', x, expr, scope = scope, expr = self)

#************************************************************
#* IntrinsicExpr ********************************************
# (int, int value), (bool, bool value)
# Intrinsic types

class IntrinsicExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.type = expr[0]
    self.value = expr[1]
  def __repr__(self):
    return f'({self.type}, {self.value})'

  def define(self):
    # NOTE: Only for compilation
    match self.type:
      case 'bool': return f'db {int(self.value)}'
      case 'char' | 'int8': return f'db {self.value}'
      case 'int16': return f'dw {self.value}'
      case 'int32': return f'dd {self.value}'
      case 'int64': return f'dq {self.value}'
      case _: return f'dq {self.value}' # Pointer

  def comp(self, scope):
    match self.type:
      case 'bool': return int(self.value)
      case _: return self.value

#************************************************************
#* DebugExpr ************************************************
# (debug, string level, (python args...), (Expr exprs...))
# Used to debug the interpreter / compiler

class DebugExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.level = expr[1]
    self.args = expr[2]
    self.exprs = [Expr.construct(subexpr) for subexpr in expr[3]]
  def __repr__(self):
    args = ', '.join([str(arg) for arg in self.args])
    if args != '':
      args = ', ' + args
    return f'(debug, {tuple(self.exprs)}{args})'

  def define(self, scope):
    self.debug(scope)
  def comp(self, scope):
    # self.debug(scope) # TODO
    return ''

  def debug(self, scope):
    results = [expr.exec(scope) for expr in self.exprs] # TODO
    debugStep(*self.args, *results, level = self.level)

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

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
    
    self.text = text
    return self.text

#************************************************************
#* Utils ****************************************************

def getExprType(t):
  if t.startswith('*'): # Pointer
    return IntrinsicExpr

  match t:
    case 'file': return FileExpr

    case 'fun': return FunExpr
    case 'def': return DefExpr
    case 'param': return ParamExpr

    case 'set': return SetExpr
    case 'call': return CallExpr
    case 'return': return ReturnExpr

    case 'if': return IfExpr

    case 'var': return VarExpr
    case 'ref': return RefExpr
    case 'deref': return DerefExpr

    case '+' | '-' | '*' | '/' | '%' | '&&' | '||' | '!': return ArithmExpr
    case 'char' | 'int8' | 'int16' | 'int32' | 'int64' | 'bool': return IntrinsicExpr

    case 'debug': return DebugExpr
  return Expr
