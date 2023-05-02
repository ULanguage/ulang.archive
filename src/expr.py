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
    else: print('[expr_t.__init__] Type not implemented:', t)

  def init_prog(self):
    # (prog, string name, expr_t files...)
    expr = self.expr # Rename
    self.name = expr[1]
    self.files = [expr_t(file) for file in expr[2:]]

  ############################################################
  # Printing #################################################

  def __repr__(self):
    return str(self)
  def __str__(self):
    parts = [self.type]
    t = self.type
    if t == 'empty': parts = [] # Special case
    elif t == 'prog': parts += self.str_prog()

    return '(' + ', '.join([str(part) for part in parts]) + ')'

  def str_prog(self):
    files = self.strSubexprs(self.files)
    return [self.name] + files

  def strSubexprs(self, exprs):
    return exprs if input('Show ({len(exprs)}) subexprs for {self.type} [y/N] ').lower() in ['y', 'yes'] else [f'({len(exprs)}) exprs...']
