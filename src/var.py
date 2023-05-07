from debug import log, error

class Var:
  def __init__(self, place, reference, _type):
    self.place = place

    self.reference = reference
    self.type = _type
    self.isPointer = _type.startswith('*')

    self.value = reference if place in ['intrinsic', 'reg'] else f'[{reference}]' # TODO: Depends on value
    self.refed = False
    self.derefed = False

    if self.isPointer:
      self.size = 'qword'
    else:
      match self.type:
        case 'bool' | 'char' | 'int8': self.size = 'byte'
        case 'int16': self.size = 'word'
        case 'int32': self.size = 'dword'
        case 'int64': self.size = 'qword'

  def __repr__(self):
    return f'var<{self.place}, {self.reference}, {self.type}, {self.refed}, {self.derefed}>'

  def putInto(self, into, scope):
    if into.place == 'intrinsic' and not into.derefed:
      error('[Var.putInto] Can\' put into intrinsic', self, into)
    elif self.type != into.type:
      error('[Var.putInto] Wrong types:', self, into)

    text = ''

    bar = 'lea' if self.refed else 'mov'

    # SEE: https://docs.google.com/spreadsheets/d/18ub3Nthb5VFduQ35bTkvx3cy-fi4NeufmC474_UgQz8/edit?usp=sharing
    # TODO: Clean
    # TODO: I think there's some extra self.size
    match [self.derefed, self.place, into.derefed, into.place]:
      case (
        [False, 'intrinsic' | 'reg', False, _] |
        [False, _, False, 'reg']
      ):
        text += f'  {bar} {self.size} {into.value}, {self.value}\n' # TODO: Should mix bar with self intrinsic and reg?

      case [False, 'intrinsic' | 'reg', True, 'intrinsic' | 'reg']:
        text += f'  mov {self.size} [{into.value}], {self.value}\n'

      case [False, 'intrinsic' | 'reg', True, _]:
        reg = scope.allocReg()
        text += f'  lea {reg.value}, {into.value}\n'
        text += f'  mov {self.size} [{reg.value}], {self.value}\n'
        scope.freeReg(reg)

      case [False, _, False, _]:
        reg = scope.allocReg()
        text += f'  {bar} {self.size} {reg.value}, {self.value}\n'
        text += f'  mov {self.size} {into.value}, {reg.value}\n'
        scope.freeReg(reg)

      case [False, _, True, 'intrinsic' | 'reg']:
        reg = scope.allocReg()
        text += f'  {bar} {self.size} {reg.value}, {self.value}\n'
        text += f'  mov {self.size} [{into.value}], {reg.value}\n'
        scope.freeReg(reg)

      case [False, _, True, _]:
        reg0 = scope.allocReg()
        reg1 = scope.allocReg()
        text += f'  lea {reg0}, {into.value}\n'
        text += f'  {bar} {self.size} {reg1}, {self.value}\n'
        text += f'  mov {self.size} [{reg0}], {reg1}\n'
        scope.freeReg(reg0)
        scope.freeReg(reg1)

      case [True, 'intrinsic' | 'reg', False, 'reg']:
        text += f'  mov {self.size} {into.value}, [{self.value}]\n'

      case [True, 'intrinsic' | 'reg', False, _]:
        reg = scope.allocReg()
        text += f'  mov {self.size} {reg.value}, [{self.value}]\n'
        text += f'  mov {self.size} {into.value}, {reg.value}\n'
        scope.freeReg(reg)

      case [True, 'intrinsic' | 'reg', True, 'intrinsic' | 'reg']:
        reg = scope.allocReg()
        text += f'  mov {self.size} {reg.value}, [{self.value}]\n'
        text += f'  mov {self.size} [{into.value}], {reg.value}\n'
        scope.freeReg(reg)

      case [True, 'intrinsic' | 'reg', True, _]:
        reg0 = scope.allocReg()
        reg1 = scope.allocReg()
        text += f'  lea {reg0}, {into.value}\n'
        text += f'  mov {self.size} {reg1}, [{self.value}]\n'
        text += f'  mov {self.size} [{reg0}], {reg1}\n'
        scope.freeReg(reg0)
        scope.freeReg(reg1)

      case [True, _, False, 'reg']:
        reg = scope.allocReg()
        text += f'  lea {reg.value}, {self.value}\n'
        text += f'  mov {self.size} {into.value}, [{reg.value}]\n'
        scope.freeReg(reg)

      case [True, _, False, _]:
        reg = scope.allocReg()
        text += f'  lea {reg.value}, {self.value}\n'
        text += f'  mov {self.size} {reg.value}, [{reg.value}]\n'
        text += f'  mov {self.size} {into.value}, {reg.value}\n'
        scope.freeReg(reg)

      case [True, _, True, 'intrinsic' | 'reg']:
        reg = scope.allocReg()
        text += f'  lea {reg.value}, {self.value}\n'
        text += f'  mov {self.size} {reg.value}, [{reg.value}]\n'
        text += f'  mov {self.size} [{into.value}], {reg.value}\n'
        scope.freeReg(reg)

      case [True, _, True, _]:
        reg0 = scope.allocReg()
        reg1 = scope.allocReg()
        text += f'  lea {reg0}, {into.value}\n'
        text += f'  lea {reg1}, {self.value}\n'
        text += f'  mov {self.size} {reg1}, [{reg1}]\n'
        text += f'  mov {self.size} [{reg0}], {reg1}\n'
        scope.freeReg(reg0)
        scope.freeReg(reg1)

      case _: 
        error('[Var.putInto] Missing case:', self, into)

    self.refed = False
    into.refed = False
    self.derefed = False
    into.derefed = False
    return text

  def passAsArg(self, scope):
    if self.derefed and not self.isPointer:
      error('[Var.passAsArg] Not a pointer:', self)

    text = ''

    bar = 'lea' if self.refed else 'mov'

    match [self.derefed, self.place]:
      case [False, 'intrinsic' | 'reg']:
        text += f'  push {self.size} {self.value}\n'

      case [False, _]:
        reg = scope.allocReg()
        text += f'  {bar} {reg.value}, {self.value}\n'
        text += f'  push {self.size} {reg.value}\n'
        scope.freeReg(reg)

      case [True, 'intrinsic' | 'reg']:
        reg = scope.allocReg()
        text += f'  mov {self.size} {reg.value}, [{self.value}]\n'
        text += f'  push {reg.value}\n'
        scope.freeReg(reg)

      case [True, _]:
        reg = scope.allocReg()
        text += f'  lea {reg.value}, {self.value}\n'
        text += f'  {bar} {self.size} {reg.value}, [{reg.value}]\n'
        text += f'  push {self.size} {reg.value}\n'
        scope.freeReg(reg)

      case _:
        error('[Var.passAsArg] Missing case:', self)

    self.refed = False
    self.derefed = False
    return text

  def ref(self):
    var = Var(self.place, self.reference, '*' + self.type) # TODO: Place? Think of passing as argument
    var.refed = True
    return var

  def deref(self):
    if not self.isPointer:
      error('[Var.deref] Not a pointer:', self)

    var = Var(self.place, self.reference, self.type[1:]) # TODO: Place? Original 
    var.derefed = True
    return var
