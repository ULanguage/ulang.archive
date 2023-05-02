from expr import expr_t
import utils

class state_t:
  def __init__(self, parent = None):
    self.parent = parent
    self.funs = dict()
    self.vars = dict()

    self.res = None
    self.returned = False

  def execute(self, expr):
    # print('[execute]', self, expr) # TODO: Print current state # TODO: Arg to debug or not

    t = expr.type
    if t == 'empty': pass
    elif t == 'prog': return self.exec_prog(expr)
    elif t == 'file': return self.exec_file(expr)
    elif t == 'fun': return self.exec_fun(expr)
    elif t == 'call': return self.exec_call(expr)
    elif t == 'def': return self.exec_def(expr)
    elif t == 'var': return self.exec_var(expr)
    elif t == 'set': return self.exec_set(expr)
    elif t == 'return': return self.exec_return(expr)
    # TODO: Expressions below are only for testing
    elif t == 'print': return self.exec_print(expr)
    elif t == '_p': return self.exec__p(expr)
    else: print('[state_t.execute] Type not implemented:', t)

    return None

  def exec_prog(self, prog):
    # print(f'Running {prog.name}')
    file = utils.findMainFile(prog)
    if file is None:
      return None # TODO: Error

    child = self.child() # TODO: Should this be inside exec_file?
    child.execute(file)
    return child.child().execute(expr_t(('call', 'main'))) # TODO: Args

  def exec_file(self, file):
    for expr in file.exprs: # TODO: Execute in order based on type of expression, such that all functions are defined before all variables?
      self.execute(expr)

  def exec_fun(self, fun):
    self.funs[fun.name] = fun

  def exec_call(self, call):
    fun = self.findFun(call.name) # TODO: Also callable variables
    if fun is None:
      print('[exec_call] ERROR: No such function', call.name)
      return None #TODO: Error

    return self.callFun(call, fun)

  def exec_def(self, expr):
    # TODO: Check it doesn't exist or error
    self.vars[expr.name] = None

  def exec_var(self, var):
    value = self.findVar(var.name)
    if value is None:
      return None #TODO: Error
    return value

  def exec_set(self, expr):
    self.vars[expr.varname] = self.execute(expr.expr)

  def exec_return(self, expr):
    self.res = self.execute(expr.expr)
    self.returned = True

  #************************************************************
  #* Testing exprs ********************************************

  def exec_print(self, expr):
    print(' '.join([str(self.execute(subexpr)) for subexpr in expr.exprs]))

  def exec__p(self, expr):
    return expr.value

  #************************************************************
  #* Utils ****************************************************

  def findFun(self, name):
    if name in self.funs:
      # TODO: Also match on args and returns type 
      return self.funs[name]
    if self.parent is None:
      return None
    return self.parent.findFun(name)

  def findVar(self, name):
    # TODO: Repeated code with findFun
    if name in self.vars:
      return self.vars[name]
    if self.parent is None:
      return None
    return self.parent.findVar(name)

  def callFun(self, call, fun):
    child = self.sibling() # TODO: Should this be in callFun
    # TODO: Define templated types

    # Pass arguments
    for idx in range(len(fun.params)): 
      param = fun.params[idx]
      arg = utils.getList(call.args, idx, param.default)
      value = expr_t(('_p', self.execute(arg)))

      child.execute(expr_t(('def', param.name)))
      child.execute(expr_t(('set', param.name, value)))
    #TODO: Check len(args) <= len(params)
    #TODO: Default values
    #TODO: Named params
    #TODO: Check all params have a value

    for expr in fun.exprs:
      child.execute(expr)
      if child.returned:
        break
    return child.res

  def child(self):
    return state_t(parent = self)
  def sibling(self):
    return state_t(parent = self.parent)

  def __repr__(self):
    return str(self)
  def __str__(self):
    return f'state<{not self.parent is None}, {list(self.funs.keys())}, {list(self.vars.keys())}>'
