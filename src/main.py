from compiler import Compile
from interpreter import Execute
from expr import Expr

if __name__ == '__main__':
  main = Expr.construct(('file', 'main.u',
    ('fun', 'test',
      ('return', ('int64', 1)),
    ),
    ('fun', 'main',
      ('return', ('int64', 0)),
    ),
  ))

  Execute(main)
  Compile(main, 'main.asm')
