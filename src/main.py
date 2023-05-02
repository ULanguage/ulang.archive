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
      ('fun', 'print', (('param', 'G', '__string', ()), ('param', 'S', '__string', ('__string', 'Sofia'))), '__string', 
        ('def', 'foo', '__string'),
        ('set', 'foo', ('__string', 'ama a')),
        ('print', ('var', 'G'), ('var', 'foo'), ('var', 'S')),
        ('return', ('__string', 'Galileo')),
      ),
      ('fun', 'main', (), '__int',
        ('def', 'G', '__string'),
        ('set', 'G', ('__string', 'Galileo')),

        ('def', 'A', ''),
        ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),
        ('set', 'A', ('__string', 'asd')),
        ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),
        ('set', 'A', ('__int', 123)),
        ('print', ('get', ('var', 'A'), '__type'), ('get', ('var', 'A'), '__typeless')),

        ('def', 'res', ''),
        ('set', 'res', ('call', 'print', ('var', 'G'), ('__string', 'Sofi'))),
        ('set', 'res', ('__int', 6)),
        ('return', ('var', 'res')),
      ),
    )
  ))

  runProgram(prog)
