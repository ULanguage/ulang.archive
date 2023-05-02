from expr import expr_t
from state import state_t

def runProgram(prog):
  print('[runProgram]', prog)
  state = state_t()
  state.execute(prog)

if __name__ == '__main__':
  prog = expr_t(('prog', 'test', (
    ('file', 'main.u', (
      ('fun', 'main', (
        ('print', ('_p', 1))
      ))
    ))
  )))

  runProgram(prog)
