from expr import expr_t
from state import state_t

def runProgram(prog):
  print('[runProgram]', prog)
  state = state_t()
  res = state.execute(prog)
  print('[runProgram] Exited with:', res)

if __name__ == '__main__':
  prog = expr_t(('prog', 'test',
    ('file', 'main.u',
      ('typedef', 'Person', ('struct',
        ('param', 'name', '__string', ()),
        ('param', 'age', '__int', ()), # TODO: What happens if I put a call as the default value, where is it called?
      )),
      ('fun', 'print', (('param', 'G', 'Person', ()), ('param', 'S', 'Person', ())), '__string', 
        ('print',
          ('get', ('var', 'G'), 'name'),
          ('get', ('var', 'G'), 'age'),
          ('__string', 'ama a'),
          ('get', ('var', 'S'), 'name'),
          ('get', ('var', 'S'), 'age'),
          ('__string', '\n'),
          ('var', 'G'),
          ('var', 'S'),
        ),
        ('return', ('__string', 'Galileo')),
      ),
      ('fun', 'main', (), '__int',
        ('def', 'G', 'Person'),
        ('setattr', ('var', 'G'), 'name', ('__string', 'Galileo')),
        ('setattr', ('var', 'G'), 'age', ('__int', 22)),
        ('def', 'S', 'Person'),
        ('setattr', ('var', 'S'), 'name', ('__string', 'Sofia')),
        ('setattr', ('var', 'S'), 'age', ('__int', 21)),
        # ('set', 'G', ('__string', 'Galileo')),

        # ('print', ('get', ('var', 'G'), '__type'), ('get', ('var', 'G'), 'name'), ('get', ('var', 'G'), 'age')),

        # ('def', 'A', ''),
        # ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),
        # ('set', 'A', ('__string', 'asd')),
        # ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),
        # ('set', 'A', ('__int', 123)),
        # ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),

        ('def', 'res', ''),
        ('set', 'res', ('call', 'print', ('var', 'G'), ('var', 'S'))),
        ('set', 'res', ('__int', 6)),
        ('return', ('var', 'res')),
      ),
    )
  ))

  runProgram(prog)
