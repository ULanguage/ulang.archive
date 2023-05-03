import scope
from scope import scope_t

if __name__ == '__main__':
  prog = (
    ('fun', 'exit', (('param', 'exitCode', 'int64'),), 'int64',
      ('exit', ('var', 'exitCode')),
    ),

    ('fun', 'test', (), 'int64',
      ('return', ('int64', 7)),
    ),

    ('fun', 'main', (), 'int64',
      ('def', 'ing', 'int64'),
      ('set', ('var', 'ing'), ('int64', 3)),
      ('set', ('var', 'ing'), ('call', 'test')),

      ('call', 'exit', ('var', 'ing')),

      ('def', '__exitCode', 'int64'),
      ('set', ('var', '__exitCode'), ('int64', 3)),
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
