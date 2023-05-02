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
      ('fun', 'print', (('param', 'S'),), 
        ('def', 'foo'),
        ('set', 'foo', ('_p', 'ama a')),
        ('print', ('var', 'G'), ('var', 'foo'), ('var', 'S')),
        ('return', ('_p', 'Galileo')),
      ),
      ('set', 'G', ('call', 'print', ('_p', 'Soso'))),
      ('fun', 'main', (),
        ('def', 'S'),
        ('set', 'S', ('_p', 'Sofia')),
        ('return', ('call', 'print', ('var', 'S'))),
      ),
    )
  ))

  runProgram(prog)
