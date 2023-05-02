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
      ('fun', 'print', (('param', 'G', ()), ('param', 'S', ('_p', 'Sofia'))), 
        ('def', 'foo', '_p'),
        ('set', 'foo', ('_p', 'ama a')),
        ('print', ('var', 'G'), ('var', 'foo'), ('var', 'S')),
        ('return', ('_p', 'Galileo')),
      ),
      ('fun', 'main', (),
        ('def', 'G', '_p'),
        ('set', 'G', ('_p', 'Galileo')),
        # ('return', ('call', 'print', ('var', 'G'), ('_p', 'Sofi'))),
      ),
    )
  ))

  runProgram(prog)
