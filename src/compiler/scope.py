Res = ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\nglobal _start\n' # NOTE: Line only to make it easier to follow with 'tail -f'
Data = '\nsection .data\n'
Text = '\nsection .text\n'

def getResult():
  return Res + Data + Text

class var_t:
  def __init__(self, t, reg, offset):
    self.type = t
    self.reg = reg
    self.offset = offset 

  def reference(self):
    reg, offset = self.reg, self.offset # Rename
    if reg == 'global': return f'[{offset}]'
    else: return f'[{reg} + {offset}]'

class scope_t:
  def __init__(self, parent = None):
    self.parent = parent
    self.vars = dict()
    self.funs = dict()

  def child(self):
    return scope_t(parent = self)

  def exec(self, expr):
    # print('[exec]', expr)

    if expr[0] == 'def': return self.exec_def(expr)
    elif expr[0] == 'fun': return self.exec_fun(expr)
    elif expr[0] == 'exit': return self.exec_exit(expr)
    elif expr[0] == 'var': return self.exec_var(expr)
    elif expr[0] == 'asm': return self.exec_asm(expr)
    elif expr[0] == 'call': return self.exec_call(expr)
    elif expr[0] == 'param': return self.exec_param(expr)
    elif expr[0] == 'set': return self.exec_set(expr)
    elif expr[0] == 'return': return self.exec_return(expr)
    elif expr[0] in ['int64']: return self.exec_intrinsicType(expr)

  def exec_def(self, expr):
    # TODO: Check not already defined
    exprT = expr[0]
    name = expr[1] # TODO: Mangle names
    varT = expr[2]
    var = self.addVar(exprT, name, varT)

    if var.reg == 'global':
      global Data
      Data += f'\n  ; {expr}\n'
      Data += f'{name}: dq {var.value}\n' # TODO: dq based on type
    else: return ''

  def exec_param(self, expr):
    exprT = expr[0]
    name = expr[1] # TODO: Mangle names
    varT = expr[2]
    return self.addVar(exprT, name, varT)
    # return f'  mov qword [{var.reg} + {var.offset}], {value}\n' # TODO: qword based on type

  def addVar(self, exprT, name, varT):
    reg, offset = 'global', name
    if not self.parent is None:
      reg = 'rsp' if exprT == 'def' else 'rbp'

      l = len(self.varsOfPlace(reg))
      offset = (l + 2 * int(exprT == 'param')) * 8

    var = var_t(varT, reg, offset)
    self.vars[name] = var
    return var

  def exec_fun(self, expr):
    global Text
    name = expr[1]
    params = expr[2]
    resT = expr[3]
    exprs = expr[4:]

    self.addFun(expr)

    child = self.child()
    s = ''

    for param in params:
      child.exec(param)

    for subexpr in exprs:
      s += f'\n  ; {subexpr}\n'
      s += child.exec(subexpr)

    # TODO: Comment with signature
    if name == 'main':
      Text += '_start:\n'
    Text += name + ':\n'
    Text += '  ; Set the stack frame\n'
    Text += '  push rbp\n'
    Text += '  mov rbp, rsp\n'

    l = len(child.varsOfPlace('rsp'))
    if l != 0:
      Text += f'  sub rsp, {l * 8} ; {l} stack vars\n' # TODO: Based on each variable's length

    Text += s

    Text += '\n  ; Remove the stack frame\n'
    Text += '.__ret:\n'
    if l != 0:
      Text += f'  add rsp, {l * 8}\n' # TODO: Based on each variable's length
    Text += '  pop rbp\n'
    Text += '  ret\n\n'

  def addFun(self, expr):
    name = expr[1] 
    self.funs[name] = expr # TODO: Mangle the name

  def exec_exit(self, expr):
    s = '  mov rax, 60\n'
    value = self.exec(expr[1])
    s += f'  mov rdi, {value}\n'
    s += '  syscall\n'
    return s

  def exec_intrinsicType(self, expr):
    return expr[1]

  def exec_var(self, expr):
    name = expr[0]
    var = self.findVar(expr)
    if var is None:
      # TODO: Error
      return None
    return var.reference()

  def exec_asm(self, expr):
    return expr[1]

  def exec_call(self, call):
    fun = self.findFun(call)
    name = fun[1] # TODO: Change
    args = call[2:]

    s = ''
    for arg in reversed(args):
      s += f'  push qword {self.exec(arg)}\n' # TODO: qword based ons ize
    s += f'  call {name}\n'
    if len(args) != 0:
      s += f'  add rsp, {len(args) * 8}\n' # TODO: 8 based on each arg's size

    return s

  def exec_set(self, expr):
    # TODO: Check types
    # TODO: Depends on to
    A = expr[1]
    B = expr[2]

    s = ''
    to = ''
    if B[0] == 'call':
      to = 'rax'
      s += self.exec(B)
    elif B[0] == 'var':
      # TODO: Actually depends on where both vars are stored
      to = 'r8' # TODO: Alloc a register
      s += f'  mov qword {to}, {self.exec(B)}\n' # TODO: qword depends on type
    else: to = self.exec(B)
      
    var = self.exec(expr[1])

    s += f'  mov qword {var}, {to}\n' # TODO: qword depends on type
    return s

  def exec_return(self, expr):
    to = self.exec(expr[1])
    # TODO: Very similar to set

    s = f'  mov qword rax, {to}\n'
    s += f'  jmp .__ret\n'
    return s

  def findFun(self, call):
    # TODO: Similar to the interpreter
    name = call[1]

    if name in self.funs:
      # TODO: Checks like in the interpreter
      return self.funs[name]
    if not self.parent is None:
      return self.parent.findFun(call)

    # TODO: Error

    return None

  def findVar(self, expr):
    # TODO: Repeated code
    name = expr[1]

    if name in self.vars:
      return self.vars[name]
    if not self.parent is None:
      return self.parent.findVar(expr)

    # TODO: Error
    return None

  def varsOfPlace(self, reg):
    return [(name, v) for name, v in self.vars.items() if v.reg == reg]
  
  def varsOfType(self, t):
    return [(name, v) for name, v in self.vars.items() if v.type == t]
