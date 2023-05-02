from expr import expr_t
import utils

class state_t:
  def __init__(self, parent = None):
    self.parent = parent
    self.funs = dict()
    self.vars = dict()

  def execute(self, expr):
    t = expr.type
    if t == 'empty': pass
    elif t == 'prog': return self.exec_prog(expr)
    elif t == 'file': return self.exec_file(expr)
    elif t == 'fun': return self.exec_fun(expr)
    elif t == 'call': return self.exec_call(expr)
    elif t == 'def': return self.exec_def(expr)
    elif t == 'var': return self.exec_var(expr)
    elif t == 'set': return self.exec_set(expr)
    # TODO: Expressions below are only for testing
    elif t == 'print': return self.exec_print(expr)
    elif t == '_p': return self.exec__p(expr)
    else: print('[state_t.execute] Type not implemented:', t)

    return None

  def exec_prog(self, prog):
    print(f'Running {prog.name}')
    file = utils.findMainFile(prog)
    if file is None:
      return None # TODO: Error

    child = self.child() # TODO: Should this be inside exec_file?
    child.execute(file)
    return child.execute(expr_t(('call', 'main'))) # TODO: Args

  def exec_file(self, file):
    for t in ['fun']: # Execute them in order such that functions are defined first #TODO: Full order
      for expr in file.exprs:
        if expr.type == t:
          self.execute(expr)

  def exec_fun(self, fun):
    self.funs[fun.name] = fun

  def exec_call(self, call):
    fun = self.findFun(call.name) # TODO: Also callable variables
    if fun is None:
      return None #TODO: Error

    child = self.child() # TODO: Should this be in callFun
    # TODO: Define templated types
    return child.callFun(fun)

  def exec_def(self, expr):
    # TODO: Check it doesn't exist or error
    self.vars[expr.name] = None

  def exec_var(self, var):
    # TODO: Check it exists or error
    return self.vars[var.name]

  def exec_set(self, expr):
    self.vars[expr.varname] = self.execute(expr.expr)

  #************************************************************
  #* Testing exprs ********************************************

  def exec_print(self, expr):
    print(' '.join([str(self.execute(subexpr)) for subexpr in expr.exprs]))

  def exec__p(self, expr):
    return expr.value

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

  def callFun(self, fun):
    for expr in fun.exprs:
      self.execute(expr)
    #TODO: Return

  def child(self):
    return state_t(parent = self)
