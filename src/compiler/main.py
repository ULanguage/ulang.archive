Res = ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\nglobal _start\n' # NOTE: Line only to make it easier to follow with 'tail -f'
Data = '\nsection .data\n'
Text = '\nsection .text\n'

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
    elif expr[0] == 'int': return self.exec_int(expr)
    elif expr[0] == 'var': return self.exec_var(expr)
    elif expr[0] == 'asm': return self.exec_asm(expr)
    elif expr[0] == 'call': return self.exec_call(expr)
    elif expr[0] == 'param': return self.exec_param(expr)
    elif expr[0] == 'set': return self.exec_set(expr)

  def exec_def(self, expr):
    # TODO: Check not already defined
    exprT = expr[0]
    name = expr[1] # TODO: Mangle names
    var = self.addVar(exprT, name)

    if var.reg == 'global':
      global Data
      Data += f'\n  ; {expr}\n'
      Data += f'{name}: dq {var.value}\n' # TODO: dq based on type
    else:
      value = self.exec(expr[2])
      return f'  mov qword [{var.reg} + {var.offset}], {value}\n' # TODO: qword based on type

  def exec_param(self, expr):
    exprT = expr[0]
    name = expr[1] # TODO: Mangle names
    return self.addVar(exprT, name) # TODO: Different from exec_def? Only for now because of default values, and because can replace global vars

  def addVar(self, exprT, name):
    var = None
    if self.parent is None:
      var = var_t('int', 'global', name) # TODO: Type
    else:
      reg = 'rsp' if exprT == 'def' else 'rbp'

      l = len(self.varsOfPlace(reg))
      offset = (l + 2 * int(exprT == 'param')) * 8

      var = var_t('int', reg, offset) # TODO: Type

    self.vars[name] = var
    return var

  def exec_fun(self, expr):
    global Text
    name = expr[1]
    params = expr[2]
    exprs = expr[3:]

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

  def exec_int(self, expr):
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
    s += f'  '

    return s

  def exec_set(self, expr):
    var = self.exec(expr[1])
    to = self.exec(expr[2])

    # TODO: Check types
    # TODO: Depends on to
    return f'  mov qword {var}, {to}\n' # TODO: qword depends on type
    
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

if __name__ == '__main__':
  prog = (
    ('fun', 'exit', (('param', 'exitCode'),),
      # TODO: Params
      ('exit', ('var', 'exitCode')),
      ('exit', ('int', 2)),
    ),
    ('fun', 'main', (),
      ('def', 'exitCode', ('int', 5)),
      ('set', ('var', 'exitCode'), ('int', 6)),
      ('call', 'exit', ('var', 'exitCode')), # TODO: pass int or exitCode
      ('exit', ('int', 1)),
    ),
  )

  # Step 1, Checks
  # Step 2...

  globalScope = scope_t()
  for expr in prog:
    globalScope.exec(expr)

  with open('main.asm', 'w') as fout:
    fout.write(Res + Data + Text)
