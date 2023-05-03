from compiler import Compile
from interpreter import Execute
from expr import Expr

if __name__ == '__main__':
  main = Expr.generic(('file', 'main.u',
    ('fun', 'main',
      ('return', 0),
    ),
  ))

  Execute(main)
  Compile(main, 'main.asm')
