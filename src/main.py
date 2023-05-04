from compiler import Compile
from interpreter import Execute
from expr import Expr

if __name__ == '__main__':
  main = Expr.construct(('file', 'main.u',
    ('def', 'globA', 'int64', ()),
    ('def', 'globB', 'int64', ('int64', 1)),
    ('fun', 'getGlob', 'int64',
      ('return', ('var', 'globA')),
    ),
    ('fun', 'setGlob', 'int64',
      ('set', ('var', 'globA'), ('int64', 2)),
    ),
    ('fun', 'main', 'int64',
      ('def', 'ing', '', ('int64', 4)),
      ('set', ('var', 'ing'), ('int32', 5)),
      ('call', 'setGlob'),
      ('set', ('var', 'ing'), ('call', 'getGlob')),
      ('return', ('var', 'ing')),
    ),
  ))

  Execute(main)
  Compile(main, 'main.asm')
