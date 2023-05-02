from expr import expr_t
from state import state_t

def runProgram(prog):
  print('[runProgram]', prog)
  state = state_t()
  state.execute(prog)

if __name__ == '__main__':
  prog = expr_t(('prog', 'test',
    ('file', 'main.u',
      ('fun', 'print', (('param', 'G'), ('param', 'S')), 
        ('def', 'foo'),
        ('set', 'foo', ('_p', 'ama a')),
        ('print', ('var', 'G'), ('var', 'foo'), ('var', 'S'))
      ),
      ('fun', 'main', (),
        ('def', 'G'),
        ('set', 'G', ('_p', 'Galileo')),
        ('def', 'S'),
        ('set', 'S', ('_p', 'Sofia')),
        ('call', 'print', ('var', 'G'), ('var', 'S'))
      )
    )
  ))

  runProgram(prog)
