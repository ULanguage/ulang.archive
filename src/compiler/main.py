Res = ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\nglobal _start\n' # NOTE: Line only to make it easier to follow with 'tail -f'
Data = '\nsection .data\n'
Text = '\nsection .text\n'

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

  def exec_def(self, expr):
    if self.parent is None: return self.exec_defGlobal(expr)
    else: return self.exec_defLocal(expr)

  def exec_param(self, expr):
    return self.addVar(expr)

  def exec_defGlobal(self, expr):
    global Data
    name = expr[1] # TODO: Mangle global names
    value = self.exec(expr[2])
    Data += f'{name}: dq {hex(value)}\n' # TODO: dq based on type

  def addVar(self, var):
    t = var[0]
    name = var[1]
    l = len([_v[0] for _v in self.vars.values() if _v[0] == t])
    offset = (l + 2 * int(t == 'param')) * 8 # TODO: Based on variable type
    self.vars[name] = (t, offset)
    return (t, offset)

  def exec_defLocal(self, expr):
    name = expr[1]
    value = self.exec(expr[2])

    s = ''
    t, offset = self.addVar(expr)
    reg = 'rsp' if t == 'def' else 'rbp'

    if offset == 0: s = f'  mov qword [{reg}], {value}\n' # TODO: qword depending on variable type
    else: s = f'  mov qword [{reg} + {offset}], {value}\n'

    return s

  def exec_fun(self, expr):
    global Text
    name = expr[1]
    params = expr[2]
    exprs = expr[3:]

    self.addFun(expr)

    child = self.child()
    s = ''

    for param in params:
      print(param)
      child.exec(param)

    for subexpr in exprs:
      s += child.exec(subexpr)

    l = len([_v[0] for _v in child.vars.values() if _v[0] == 'def'])

    if name == 'main':
      Text += '_start:\n'
    Text += name + ':\n'
    Text += '  push rbp\n'
    Text += '  mov rbp, rsp\n'
    if l != 0:
      Text += f'  sub rsp, {l * 8}\n' # TODO: Based on each variable's length
    Text += s
    if l != 0:
      Text += f'  add rsp, {l * 8}\n' # TODO: Based on each variable's length
    Text += '  pop rbp\n'
    Text += '  ret\n\n'

  def addFun(self, expr):
    name = expr[1] 
    self.funs[name] = expr # TODO: Mangle the name

  def findFun(self, call):
    # TODO: Similar to the interpreter
    name = call[1]

    if name in self.funs:
      # TODO: Checks like in the interpreter
      return self.funs[name]

    if not self.parent is None:
      return self.parent.findFun(call)

    return None
  
  def exec_exit(self, expr):
    s = '  mov rax, 60\n'
    value = self.exec(expr[1])
    s += f'  mov rdi, {value}\n'
    s += '  syscall\n'
    return s

  def exec_int(self, expr):
    return expr[1]

  def exec_var(self, expr):
    name = expr[1]
    if name in self.vars:
      t, offset = self.vars[name]
      reg = 'rsp' if t == 'def' else 'rbp'
      if offset == 0: return f'[{reg}]'
      else: return f'[{reg} + {offset}]'
    else: # TODO: Look in parent scope
      return f'[{name}]'

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

    return s

if __name__ == '__main__':
  prog = (
    ('fun', 'exit', (('param', 'exitCode'),),
      # TODO: Params
      ('exit', ('var', 'exitCode')),
      ('exit', ('int', 2)),
    ),
    ('fun', 'main', (),
      ('def', 'exitCode', ('int', 5)),
      ('def', 'test', ('int', 6)),
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
