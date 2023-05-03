from compiler import Compile
from interpreter import Execute
from expr import Expr

if __name__ == '__main__':
  main = Expr.construct(('file', 'main.u',
    ('def', 'globA'),
    ('def', 'globB', ('int64', 1)),
    ('fun', 'getGlob',
      ('return', ('int64', 2)),
    ),
    ('fun', 'setGlob',
      ('return', ('int64', 3)),
    ),
    ('fun', 'main',
      ('def', 'ing', ('int64', 4)),
      ('set', ('var', 'ing'), ('int64', 5)),
      ('return', ('var', 'ing')),
    ),
  ))

  Execute(main)
  Compile(main, 'main.asm')
