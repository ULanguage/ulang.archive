import scope
from scope import scope_t

if __name__ == '__main__':
  prog = (
    ('fun', 'exit', (('param', 'exitCode', 'int64'),), 'int64',
      ('exit', ('var', 'exitCode')),
    ),

    ('fun', 'test', (), 'int64',
      ('return', ('int64', 3)),
    ),

    ('fun', 'main', (), 'int64',
      ('def', 'ing', 'int64'),
      ('set', ('var', 'ing'), ('int64', 1)),
      ('set', ('var', 'ing'), ('call', 'test')),

      ('def', '__exitCode', 'int64'),
      ('set', ('var', '__exitCode'), ('int64', 1)),
      ('set', ('var', '__exitCode'), ('var', 'ing')),
      ('call', 'exit', ('var', '__exitCode')),
    ),
  )

  # Step 1, Checks
  # Step 2...

  globalScope = scope_t()
  for expr in prog:
    globalScope.exec(expr)

  with open('main.asm', 'w') as fout:
    fout.write(scope.getResult())
