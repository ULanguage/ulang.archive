import utils

class expr_t:
  ############################################################
  # Init #####################################################

  def __init__(self, expr):
    self.expr = expr
    t = utils.getList(expr, 0, 'empty')
    self.type = t
    if t == 'empty': pass
    elif t == 'prog': self.init_prog()
    elif t == 'file': self.init_file()
    elif t == 'fun': self.init_fun()
    elif t == 'call': self.init_call()
    elif t == 'def': self.init_def()
    elif t == 'var': self.init_var()
    elif t == 'set': self.init_set()
    # TODO: Expressions below are only for testing
    elif t == 'print': self.init_print()
    elif t == '_p': self.init__p()
    else: print('[expr_t.__init__] Type not implemented:', t)

  def init_prog(self):
    # (prog, string name, expr_t files...)
    expr = self.expr # Rename
    self.name = expr[1]
    self.files = [expr_t(file) for file in expr[2:]]

  def init_file(self):
    # (file, string path, expr_t exprs...)
    expr = self.expr # Rename
    self.path = expr[1]
    self.exprs = [expr_t(subexpr) for subexpr in expr[2:]]

  def init_fun(self):
    # (fun, string name, expr_t exprs...)
    expr = self.expr # Rename
    self.name = expr[1]
    self.exprs = [expr_t(subexpr) for subexpr in expr[2:]]

  def init_call(self):
    # (call, string name)
    # TODO: Args
    expr = self.expr # Rename
    self.name = expr[1]

  def init_def(self):
    # (def, string name)
    # TODO: Define type
    # TODO: Default value
    expr = self.expr # Rename
    self.name = expr[1]

  def init_var(self):
    # (var, string name)
    expr = self.expr # Rename
    self.name = expr[1]

  def init_set(self):
    # (set, string varname, expr_t expr)
    # TODO: Check type matches
    expr = self.expr # Rename
    self.varname = expr[1]
    self.expr = expr_t(expr[2])

  ############################################################
  # Testing exprs ############################################

  def init_print(self):
    self.exprs = [expr_t(subexpr) for subexpr in self.expr[1:]]

  def init__p(self):
    self.value = self.expr[1]

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
    if t == 'empty': parts = [] # Special case
    elif t == 'prog': parts += self.str_prog()
    elif t == 'file': parts += self.str_file()
    elif t == 'fun': parts += self.str_fun()
    elif t == 'call': parts += self.str_call()
    elif t == 'def': parts += self.str_def()
    elif t == 'var': parts += self.str_var()
    elif t == 'set': parts += self.str_set()
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
    exprs = self.strSubexprs(self.exprs)
    return [self.name] + exprs

  def str_call(self):
    return [self.name]

  def str_def(self):
    return [self.name]

  def str_var(self):
    return [self.name]

  def str_set(self):
    return [self.varname, self.expr] 

  def strSubexprs(self, exprs):
    return exprs if input(f'Show ({len(exprs)}) subexprs for {self.type} [Y/n] ').lower() not in ['n', 'no'] else [f'({len(exprs)}) exprs...']
