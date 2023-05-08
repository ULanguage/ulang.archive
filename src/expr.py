from copy import deepcopy

from var import Var
from debug import log, error, debugStep

#************************************************************
#* Expr *****************************************************

class Expr:
  def __init__(self, expr):
    self._expr = expr
    self.text = ''
  def __repr__(self):
    return f'({self._expr[0]}, ({len(self._expr[1:])})...)'
  def define(self, scope):
    # U: Used to define this expression in the current scope
    log('[define] TODO', self, level = 'error')
    return None
  def comp(self, scope):
    # U: Used to compile this expression
    log('[comp] TODO', self, level = 'error')
    return None

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

  # TODO: Define to get exported functions

  def comp(self, scope, isMain = False):
    log(self, level = 'deepDebug')
    imports = ''
    exports = ''
    data = 'section .data\n'
    # TODO: .rodata
    text = '\nsection .text\n'

    # Define vars, funs, imports # TODO: Anything else? options, libname, types
    for expr in self.exprs:
      # TODO: Check types?
      _def = expr.define(scope)
      if isinstance(expr, ImportExpr):
        imports += _def
      elif isinstance(expr, FunExpr):
        exports += _def
      elif isinstance(expr, DefExpr):
        data += _def
      else:
        error('[FileExpr] Comp not yet supported', self)

    # Compile functions # NOTE: The order doesn't matter
    main = scope.findFun('main')
    for expr in self.exprs:
      if isinstance(expr, FunExpr):
        expr.comp(scope.child(), isMain = expr == main)
        text += expr.text

    self.text = imports + ('\n' if imports != '' else '') + exports + ('\n' if exports != '' else '') + data + text
    return self.text

#************************************************************
#* ImportExpr ***********************************************
# (cimport, string funName)

class ImportExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.name = expr[1]
    self.type = expr[2]
    self.params = [Expr.construct(subexpr) for subexpr in expr[3:]]
  def __repr__(self):
    params = ', '.join([str(param) for param in self.params])
    if params != '':
      params = ', ' + params
    return f'(cimport, {self.name}, {self.type}{params})'

  def define(self, scope):
    scope.defFun(self, lang = 'C')
    return f'extern {self.name}\n'

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
    return f'global {self.name}\n' # TODO: Selective exports

  def comp(self, scope, isMain = False):
    log(self, level = 'deepDebug')
    s = ''

    # TODO: If isMain instance global vars with (default) values

    # NOTE: Assumes params exist
    for param in self.params:
      param.define(scope)

    # Compile expressions in order
    for expr in self.exprs:
      res = expr.comp(scope)
      scope.freeReg(res)
      s += expr.text

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

    text = self.compComment()
    text += f'{self.name}: '
    if isinstance(self.value, EmptyExpr):
      return text + 'dq 0\n' # TODO: Reserve space for it's type
    elif isinstance(self.value, IntrinsicExpr):
      return text + f'{self.value.define()}\n'
    else: # TODO: Other types, queue for main to comp it
      error('[DefExpr] Define not implemented:', self)

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()

    scope.defVar(self)
    var = scope.findVar(self.name)

    if not isinstance(self.value, EmptyExpr):
      value = self.value.comp(scope)

      text += self.value.text
      text += value.putInto(var, scope)

      scope.freeReg(value)

    self.text = text
    return var

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
      text += value.passAsArg(scope)
      scope.freeReg(value)
    
    self.text = text
    return var

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
    return self.find(scope)

  def find(self, scope):
    var = scope.findVar(self.name)
    if var is None:
      error('[VarExpr.find]', scope = scope, expr = self)
    return var

#************************************************************
#* RefExpr **************************************************
# (ref, Expr expr)
# Returns a pointer to whatever is returned by expr

class RefExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.expr = Expr.construct(expr[1])
  def __repr__(self):
    return f'(ref, {self.expr})'

  def comp(self, scope):
    log(self, level = 'deepDebug')

    var = self.expr.comp(scope)
    if self.expr.text != '':
      self.text = self.compComment() + self.expr.text

    return var.ref()

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
    if self.expr.text != '':
      self.text = self.compComment() + self.expr.text
    return var.deref()

#************************************************************
#* SetExpr **************************************************
# (set, Expr into, Expr value)
# Sets value into "into"

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

    # TODO: Does the order matter? Yes, and I should decide an order for each expression
    A = self.A.comp(scope) 
    text += self.A.text

    B = self.B.comp(scope)
    text += self.B.text

    text += B.putInto(A, scope)
    scope.freeReg(B)

    self.text = text
    return A

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
  
    fun, lang = scope.findFun(self.name)

    match lang:
      case 'U': return self.compU(fun, scope)
      case 'C': return self.compC(fun, scope)

  def compU(self, fun, scope):
    text = self.compComment()
    sibling = scope.sibling()

    # TODO: Templated types? Should be compiled

    # Pass args
    if len(self.args) > len(fun.params):
      error('[CallExpr.compU] Too many args:', scope = scope, expr = self)

    for _idx, param in enumerate(reversed(fun.params)): # NOTE: Params are passed on the stack, thus they're reversed
      idx = len(fun.params) - 1 - _idx # Also in reverse
      if idx < len(self.args): # This param is provided
        arg = self.args[idx]

        var = param.define(sibling)
        value = arg.comp(scope)

        text += arg.text
        text += value.passAsArg(scope)

        scope.freeReg(value)
      else:
        res = param.comp(sibling)
        text += param.text
        scope.freeReg(res)

    text += f'  call {fun.name}\n'
    text += f'  add rsp, {len(fun.params) * 8}\n' # Restore the stack # TODO: Depends on the size of the params
    
    self.text = text
    return scope.allocReg('rax', fun.type) # TODO: More than one return

  def compC(self, fun, scope):
    text = self.compComment()
    sibling = scope.sibling()

    # Pass args
    if len(self.args) > len(fun.params):
      error('[CallExpr.compC] Too many args:', scope = scope, expr = self)

    # TODO: Support more than 6 params (not needed for syscalls)
    regs = []
    for reg, param in zip(['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'], fun.params):
      regs.append(scope.allocReg(reg, param.type))

    for idx, param in enumerate(fun.params):
      reg = regs[idx]
      reg = Var(reg.place, reg.reference, param.type) # Replace it's type

      if idx < len(self.args): # This param is provided
        arg = self.args[idx]

        var = param.define(sibling)
        value = arg.comp(scope)

        text += arg.text
        text += value.putInto(reg, scope)

        scope.freeReg(value)
      else:
        error('[CallExpr.compC] Not yet supported', self)

    text += f'  call {fun.name} wrt ..plt\n'

    for reg in regs:
      scope.freeReg(reg)
    
    self.text = text
    return scope.allocReg('rax', fun.type) # TODO: More than one return


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

    rax = None
    if isinstance(self.expr, EmptyExpr):
      pass # TODO: Check current return type?
    else:
      rax = scope.allocReg('rax')
      res = self.expr.comp(scope)

      rax = Var(rax.place, rax.reference, res.type) # Replace rax's type

      # TODO: Check current return type and res' type

      text += self.expr.text

      if isinstance(self.expr, EmptyExpr):
        log('[ReturnExpr] Empty return', level = 'warning') # TODO: Check it's valid
      else:
        text += res.putInto(rax, scope)

      scope.freeReg(res)

    text += '  jmp .__ret\n'

    self.text = text
    return rax

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

    # TODO: Repeated code with ReturnExpr
    res = self.cond.comp(child) 
    text += self.cond.text

    reg = child.allocReg()
    if isinstance(self.value, EmptyExpr):
      log('[ReturnExpr] Empty return', level = 'warning') # TODO: Check it's valid
    else:
      text += res.putInto(Var('reg', reg, res.type), scope)
      child.freeReg(res)

    trueLabel = child.getLabel('.__true')
    falseLabel = child.getLabel('.__else')
    endLabel = child.getLabel('.__end')

    text += f'  cmp {reg}, {FALSE.comp(scope)}\n' # TODO: FALSE.comp? Clean this!
    text += f'  je {falseLabel}\n'
    
    child.freeReg(reg)

    text += f'{trueLabel}:\n'

    for expr in self.truePath:
      text += expr.comp(child)

    text += f'  jmp {endLabel}\n'
    text += f'{falseLabel}:\n'

    for expr in self.falsePath:
      text += expr.comp(child)

    text += f'{endLabel}:\n'

    self.text = text
    return None

#************************************************************
#* WhileExpr ************************************************
# (while, Expr cond, Expr exprs...)

class WhileExpr(Expr):
  def __init__(self, expr):
    super().__init__(expr)
    self.cond = Expr.construct(expr[1])
    self.exprs = [Expr.construct(subexpr) for subexpr in expr[2:]]
  def __repr__(self):
    return f'(while, {self.cond}, ({len(self.exprs)})...)'

  def comp(self, scope):
    log(self, level = 'deepDebug')
    text = self.compComment()
    
    child = scope.child()

    # TODO: Repeated code with ReturnExpr and IfExpr

    condLabel = child.getLabel('.__cond')
    trueLabel = child.getLabel('.__true')
    endLabel = child.getLabel('.__end')

    text += f'{condLabel}:\n'

    res = self.cond.comp(child) 
    text += self.cond.text

    if not isinstance(self.cond, EmptyExpr):
      reg = child.allocReg(_type = res.type)

      text += res.putInto(reg, scope)
      child.freeReg(res)

      text += f'  cmp {reg.value}, {FALSE.comp(scope).value}\n' # TODO: FALSE.comp? Clean this!
      text += f'  je {endLabel}\n'
    
    child.freeReg(reg)

    text += f'{trueLabel}:\n'

    for expr in self.exprs:
      res = expr.comp(child)
      child.freeReg(res)
      text += expr.text

    text += f'  jmp {condLabel}\n'
    text += f'{endLabel}:\n'

    self.text = text
    return None

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
    
    x = self.x.comp(scope)
    text += self.x.text

    y = self.y.comp(scope)
    text += self.y.text

    if x.type != y.type:
      error('[ArithmExpr] Wrong types', self)

    regX = scope.allocReg()
    regX = Var(regX.place, regX.reference, x.type)
    text += x.putInto(regX, scope)
    scope.freeReg(x)

    regY = scope.allocReg()
    regY = Var(regY.place, regY.reference, y.type)
    text += y.putInto(regY, scope)
    scope.freeReg(y)

    text += self.compAction(regX.value, regY.value, scope)
    scope.freeReg(regY)

    self.text = text
    return regX

  def compAction(self, x, y, scope):
    text = ''

    match self.action:
      case '+':
        text += f'  add {x}, {y}\n'
      case '-':
        text += f'  sub {x}, {y}\n'
      case '*':
        # TODO: Alloc rax, and high part
        text += f'  imul {x}, {y}\n' # TODO: unsigned
        text += f'  mov {x}, rax\n' # TODO: High part
      case '/':
        # TODO: Alloc rax,
        text += f'  idiv qword {y}\n' # TODO: unsigned # TODO: qword depends on size
        text += f'  mov {x}, rax\n'
      case '%':
        # TODO: Alloc rdx,
        text += f'  idiv qword {y}\n' # TODO: unsigned # TODO: qword depends on size
        text += f'  mov {x}, rdx\n'
      case '&&':
        text += f'  and {x}, {y}\n'
      case '||':
        text += f'  or {x}, {y}\n'
      case '!':
        text += f'  not {x}\n'

    return text

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
    value = int(self.value) if self.type == 'bool' else self.value
    size = 'dq' # Default to int64 or pointer
    match self.type:
      case 'bool' | 'char' | 'int8': size = 'db'
      case 'int16': size = 'dw'
      case 'int32': size = 'dd'
    return f'{size} {value}'

  def comp(self, scope):
    value = int(self.value) if self.type == 'bool' else self.value
    return Var('intrinsic', f'{value}', self.type) # TODO: Reference?

#21, number of lines for the GenericExpr
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
    return None 

#************************************************************
#* Utils ****************************************************

def getExprType(t):
  match t:
    case 'file': return FileExpr
    case 'cimport': return ImportExpr

    case 'fun': return FunExpr
    case 'def': return DefExpr
    case 'param': return ParamExpr

    case 'set': return SetExpr
    case 'call': return CallExpr
    case 'return': return ReturnExpr

    case 'if': return IfExpr
    case 'while': return WhileExpr

    case 'var': return VarExpr
    case 'ref': return RefExpr
    case 'deref': return DerefExpr

    case '+' | '-' | '*' | '/' | '%' | '&&' | '||' | '!': return ArithmExpr
    case 'char' | 'int8' | 'int16' | 'int32' | 'int64' | 'bool': return IntrinsicExpr

    case _:
      if t.startswith('*'): # Pointer
        return IntrinsicExpr
      return Expr

TRUE = Expr.construct(('bool', True))
FALSE = Expr.construct(('bool', False))

