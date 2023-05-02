Res = ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\nglobal _start\n' # NOTE: Line only to make it easier to follow with 'tail -f'
Data = '\nsection .data\n'
Text = '\nsection .text\n'

class scope_t:
  def __init__(self, parent = None):
    self.parent = parent
    self.vars = dict()

  def child(self):
    return scope_t(parent = self)

  def exec(self, expr):
    # print('[exec]', expr)

    if expr[0] == 'def': return self.exec_def(expr)
    elif expr[0] == 'fun': return self.exec_fun(expr)
    elif expr[0] == 'exit': return self.exec_exit(expr)
    elif expr[0] == 'int': return self.exec_int(expr)
    elif expr[0] == 'var': return self.exec_var(expr)

  def exec_def(self, expr):
    if self.parent is None: return self.exec_defGlobal(expr)
    else: return self.exec_defLocal(expr)

  def exec_defGlobal(self, expr):
    global Data
    name = expr[1] # TODO: Mangle global names
    value = self.exec(expr[2])
    Data += f'{name}: dq {hex(value)}\n' # TODO: dq based on type

  def addVar(self, var):
    name, _ = var[1:3]
    offset = len(self.vars) * 8 # TODO: Based on variable type
    self.vars[name] = offset
    return offset

  def exec_defLocal(self, expr):
    name = expr[1]
    value = self.exec(expr[2])

    s = ''
    offset = self.addVar(expr)
    if offset == 0: s = f'  mov qword [rsp], {value}\n' # TODO: qword depending on variable type
    else: s = f'  mov qword [rsp + {offset}], {value}\n'

    return s

  def exec_fun(self, expr):
    global Text

    child = self.child()
    s = ''
    ex = '  ret'
    for subexpr in expr[2:]:
      s += child.exec(subexpr)
      if subexpr[0] == 'exit':
        ex = '  syscall\n'

    if expr[1] == 'main':
      Text += '_start:\n'
    Text += expr[1] + ':\n'

    if len(child.vars) != 0:
      Text += f'  sub rsp, {len(child.vars) * 8}\n' # TODO: Based on each variable's length

    Text += s

    if len(child.vars) != 0:
      Text += f'  add rsp, {len(child.vars) * 8}\n' # TODO: Based on each variable's length

    Text += ex
  
  def exec_exit(self, expr):
    s = '  mov rax, 60\n'
    value = self.exec(expr[1])
    s += f'  mov rdi, {value}\n'
    return s

  def exec_int(self, expr):
    return expr[1]

  def exec_var(self, expr):
    name = expr[1]
    if name in self.vars:
      offset = self.vars[name]
      if offset == 0: return '[rsp]'
      else: return f'[rsp + {offset}]'
    else: # TODO: Look in parent scope
      return f'[{name}]'

if __name__ == '__main__':
  prog = (
    ('def', 'test', ('int', 5)),
    ('fun', 'main', 
      ('def', 'ing', ('int', 8)),
      ('def', 'asd', ('int', 11)),
      ('exit', ('var', 'ing')),
    ),
  )

  # Step 1, Checks
  # Step 2...

  globalScope = scope_t()
  for expr in prog:
    globalScope.exec(expr)

  with open('main.asm', 'w') as fout:
    fout.write(Res + Data + Text)
