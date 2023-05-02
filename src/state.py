from expr import expr_t
import utils

class state_t:
  def __init__(self, parent = None):
    self.parent = parent
    self.funs = dict()

  def execute(self, expr):
    t = expr.type
    if t == 'empty': pass
    elif t == 'prog': return self.exec_prog(expr)
    elif t == 'file': return self.exec_file(expr)
    elif t == 'fun': return self.exec_fun(expr)
    elif t == 'call': return self.exec_call(expr)
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

  #************************************************************
  #* Testing exprs ********************************************

  def exec_print(self, expr):
    print(' '.join([str(self.execute(subexpr)) for subexpr in expr.exprs]))

  def exec__p(self, expr):
    return expr.value

  #************************************************************
  #* Utils ****************************************************

  def findFun(self, name):
    for funName, fun in self.funs.items():
      if funName == name: # TODO: Also match on args and returns type 
        return fun
    if self.parent is None:
      return None
    return self.parent.findFun(name)

  def callFun(self, fun):
    for expr in fun.exprs:
      self.execute(expr)
    #TODO: Return

  def child(self):
    return state_t(parent = self)