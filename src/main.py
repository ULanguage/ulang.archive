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
      ('fun', 'print', (('param', 'G', '__string', ()), ('param', 'S', '__string', ('__string', 'Sofia'))), 
        ('def', 'foo', '__string'),
        ('set', 'foo', ('__string', 'ama a')),
        ('print', ('var', 'G'), ('var', 'foo'), ('var', 'S')),
        ('return', ('__string', 'Galileo')),
      ),
      ('fun', 'main', (),
        ('def', 'G', '__string'),
        ('set', 'G', ('__string', 'Galileo')),
        ('return', ('call', 'print', ('var', 'G'), ('__string', 'Sofi'))),
      ),
    )
  ))

  runProgram(prog)
