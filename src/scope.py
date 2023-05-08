from expr import *
from var import Var
from debug import log, error

class Scope:
  def __init__(self, parent = None):
    self.parent = parent

    self.funs = dict()
    self.vars = dict()

    self.ret = None
    self.returned = False
    self.broke = False

    self.labels = dict()
    self.registers = { reg: True for reg in ['rax', 'rbx', 'rcx', 'rdx', 'rdi', 'rsi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'] }
  def __repr__(self):
    return f'Scope<{not self.parent is None}, {list(self.funs.keys())}, {list(self.vars.keys())}>'

  def defFun(self, fun, lang = 'U'):
    if not self.findFun(fun.name) is None:
      error(f'[defFun] A function with the name "{fun.name}" already exists', scope = self, expr = fun)
    self.funs[fun.name] = (fun, lang)

  def findFun(self, name):
    if name in self.funs:
      return self.funs[name]
    if not self.parent is None:
      return self.parent.findFun(name)
    return None

  def defVar(self, _def, local = False):
    if not self.findVar(_def.name, localOnly = local) is None:
      error(f'[defVar] A variable with the name "{_def.name}" already exists', local, scope = self, expr = _def)
    var = self.newVar(_def)
    self.vars[_def.name] = var
    return var

  def findVar(self, name, localOnly = False):
    # TODO: Repeated code with findFun
    if name in self.vars:
      return self.vars[name]
    if not localOnly and not self.parent is None:
      return self.parent.findVar(name)
    return None

  def getLabel(self, label):
    if self.parent is not None and self.parent.parent is not None: # Go upstreams until the function scope # TODO: Simplify
      return self.parent.getLabel(label)

    count = self.labels.get(label, 0)
    self.labels[label] = count + 1
    return f'{label}_{count}'

  def child(self):
    return type(self)(parent = self)
  def sibling(self):
    return type(self)(parent = self.parent)

  def newVar(self, _def):
    place = 'def' if isinstance(_def, DefExpr) else 'param'

    reference = ''
    offset = len(self.varsWithPlace(place)) * 8 # TODO: 8 depends on each var's size
    if place == 'def':
      reference = f'rbp - {offset + 8}' # Below rbp
    elif place == 'param':
      reference = f'rbp + {offset + 16}' # Above rbp and rip

    if self.parent is None and isinstance(_def, DefExpr):
      place = 'global'
      reference = f'rel {_def.name}'

    return Var(place, reference, _def.type)

  def varsWithPlace(self, place):
    return [var for _, var in self.vars.items() if var.place == place]

  def allocReg(self, force = None, _type = 'int64'):
    if self.parent.parent is not None: # Managed by function scope # TODO: Simplify
      return self.parent.allocReg(force)

    freeRegs = [reg for reg, free in self.registers.items() if free]
    if len(freeRegs) == 0 or (force is not None and force not in freeRegs):
      error('[Scope.allocReg] No free registers available, handle', force, _type, self)

    reg = freeRegs[0]
    if force is not None:
      reg = force
    self.registers[reg] = False
    return Var('reg', reg, _type)

  def freeReg(self, reg):
    if isinstance(reg, Var) and reg.place == 'reg':
      if self.parent.parent is not None: # Managed by function scope # TODO: Simplify
        return self.parent.freeReg(reg)
      self.registers[reg.reference] = True
