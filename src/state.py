from expr import expr_t
from var import var_t
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
    fun = self.findFun(call) # TODO: Also callable variables
    if fun is None:
      print('[exec_call] ERROR: No such function', call.name)
      return None #TODO: Error

    return self.callFun(call, fun)

  def exec_def(self, expr):
    # TODO: Check it doesn't exist or error
    self.vars[expr.name] = var_t(None, expr.varType) # TODO: Default value

  def exec_var(self, var):
    res = self.findVar(var.name)
    if res is None:
      return None #TODO: Error
    return res

  def exec_set(self, expr):
    self.setVar(expr.varname, self.execute(expr.expr))

  def setVar(self, name, newValue): # TODO: Move
    var = self.findVar(name)
    if var.type != newValue.type:
      print('[exec_set] ERROR: Wrong types:', var.type, newValue.type)
    var.value = newValue.value # TODO: Or replace?

  def exec_return(self, expr):
    self.res = self.execute(expr.expr)
    self.returned = True

  #************************************************************
  #* Testing exprs ********************************************

  def exec_print(self, expr):
    print(' '.join([str(self.execute(subexpr)) for subexpr in expr.exprs]))

  def exec__p(self, expr):
    return var_t(expr.value, '_p')#str(type(expr.value))) #TODO: Type

  #************************************************************
  #* Utils ****************************************************

  def findFun(self, call):
    if call.name in self.funs:
      fun = self.funs[call.name] # TODO: Multiple functions with the same name (but different types/args/etc)
      matches = len(call.args) <= len(fun.params)

      # Check all params have a value
      for idx in range(len(fun.params)): 
        param = fun.params[idx]
        arg = utils.getList(call.args, idx, param.default)
        matches &= arg.type != 'empty'

      #TODO: Named params
      #TODO: Check param types
      #TODO: Check return types
      #TODO: Check template types
      if matches:
        return fun
    if self.parent is None:
      return None
    return self.parent.findFun(call)

  def findVar(self, name):
    # TODO: Repeated code with findFun
    if name in self.vars:
      return self.vars[name]
    if self.parent is None:
      return None
    return self.parent.findVar(name)

  def callFun(self, call, fun):
    sib = self.sibling()

    # TODO: Define templated types in child

    # Pass arguments
    for idx in range(len(fun.params)): 
      param = fun.params[idx]
      arg = utils.getList(call.args, idx, param.default)
      value = self.execute(arg)

      sib.execute(expr_t(('def', param.name, param.varType)))
      # sib.execute(expr_t(('set', param.name, arg)))
      sib.setVar(param.name, value)
    #TODO: Named params

    for expr in fun.exprs:
      sib.execute(expr)
      if sib.returned:
        break
    return sib.res

  def child(self):
    return state_t(parent = self)
  def sibling(self):
    return state_t(parent = self.parent)

  def __repr__(self):
    return str(self)
  def __str__(self):
    return f'state<{not self.parent is None}, {list(self.funs.keys())}, {list(self.vars.keys())}>'
