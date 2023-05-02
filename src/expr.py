import utils

class expr_t:
  ############################################################
  # Init #####################################################

  def __init__(self, expr):
    if type(expr) == expr_t: # Copy other expressions
      for k in dir(expr):
        if not k in dir(self):
          self.__setattr__(k, expr.__getattribute__(k))
      return

    self._expr = expr
    t = utils.getList(expr, 0, 'empty')
    self.type = t
    # TODO: Nicer order
    if t == 'empty': pass
    elif t == 'prog': self.init_prog()
    elif t == 'file': self.init_file()
    elif t == 'fun': self.init_fun()
    elif t == 'call': self.init_call()
    elif t == 'def': self.init_def()
    elif t == 'var': self.init_var()
    elif t == 'set': self.init_set()
    elif t == 'param': self.init_param()
    elif t == 'import': self.init_import()
    elif t == 'return': self.init_return()
    # TODO: Expressions below are only for testing
    elif t == 'print': self.init_print()
    elif t == '_p': self.init__p()
    else: print('[expr_t.__init__] Type not implemented:', t)

  def init_prog(self):
    # (prog, string name, expr_t files...)
    expr = self._expr # Rename
    self.name = expr[1]
    self.files = [expr_t(file) for file in expr[2:]]

  def init_file(self):
    # (file, string path, expr_t exprs...)
    expr = self._expr # Rename
    self.path = expr[1]
    self.exprs = [expr_t(subexpr) for subexpr in expr[2:]]

  def init_fun(self):
    # (fun, string name, (expr_t params...), expr_t exprs...)
    # TODO: Named params
    expr = self._expr # Rename
    self.name = expr[1]
    self.params = [expr_t(subexpr) for subexpr in expr[2]]
    self.exprs = [expr_t(subexpr) for subexpr in expr[3:]]

  def init_call(self):
    # (call, string name, expr_t args...)
    # TODO: Named args
    expr = self._expr # Rename
    self.name = expr[1]
    self.args = [expr_t(subexpr) for subexpr in expr[2:]]

  def init_def(self):
    # (def, string name, string varType)
    # TODO: Default value
    expr = self._expr # Rename
    self.name = expr[1]
    self.varType = expr[2]

  def init_var(self):
    # (var, string name)
    expr = self._expr # Rename
    self.name = expr[1]

  def init_set(self):
    # (set, string varname, expr_t expr)
    # TODO: Check type matches
    expr = self._expr # Rename
    self.varname = expr[1]
    self.expr = expr_t(expr[2])

  def init_param(self):
    # (param, string name, expr_t default)
    # TODO: Type
    expr = self._expr # Rename
    self.name = expr[1]
    self.default = expr_t(expr[2])

  def init_return(self):
    # (return, expr_t res)
    # TODO: return a, b, c
    expr = self._expr # Rename
    self.expr = expr_t(expr[1])

  ############################################################
  # Testing exprs ############################################

  def init_print(self):
    self.exprs = [expr_t(subexpr) for subexpr in self._expr[1:]]

  def init__p(self):
    self.value = self._expr[1]

  def str_print(self):
    return self.strSubexprs(self.exprs)

  def str__p(self):
    return [self.value]

  ############################################################
  # Printing #################################################

  def __repr__(self):
    return str(self)
  def __str__(self):
    parts = [self.type]
    t = self.type
    # TODO: Nicer order (same as __init__)
    if t == 'empty': parts = [] # Special case
    elif t == 'prog': parts += self.str_prog()
    elif t == 'file': parts += self.str_file()
    elif t == 'fun': parts += self.str_fun()
    elif t == 'call': parts += self.str_call()
    elif t == 'def': parts += self.str_def()
    elif t == 'var': parts += self.str_var()
    elif t == 'set': parts += self.str_set()
    elif t == 'param': parts += self.str_param()
    elif t == 'return': parts += self.str_return()
    # TODO: Expressions below are only for testing
    elif t == 'print': parts += self.str_print()
    elif t == '_p': parts += self.str__p()

    return '(' + ', '.join([str(part) for part in parts]) + ')'

  def str_prog(self):
    files = self.strSubexprs(self.files)
    return [self.name] + files

  def str_file(self):
    exprs = self.strSubexprs(self.exprs)
    return [self.path] + exprs

  def str_fun(self):
    params = '(' + ', '.join([str(param) for param in self.params]) + ')' # TODO: Repeated code
    exprs = self.strSubexprs(self.exprs)
    return [self.name, params] + exprs

  def str_call(self):
    args = '(' + ', '.join([str(arg) for arg in self.args]) + ')' # TODO: Repeated code
    return [self.name, args]

  def str_def(self):
    return [self.name, self.varType]

  def str_var(self):
    return [self.name]

  def str_set(self):
    return [self.varname, self.expr] 

  def str_param(self):
    return [self.name, self.default] 

  def str_return(self):
    return [self.expr] 

  def strSubexprs(self, exprs):
    return [f'({len(exprs)}) exprs...'] #TODO: Nicer input
    # return exprs if input(f'Show ({len(exprs)}) subexprs for {self.type} [Y/n] ').lower() not in ['n', 'no'] else [f'({len(exprs)}) exprs...']
