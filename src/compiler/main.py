import scope
from scope import scope_t

if __name__ == '__main__':
  prog = (
    # fun exit(int64 exitCode) int64
    ('fun', 'exit', (('param', 'exitCode', 'int64'),), 'int64',
      # exit exitCode
      ('exit', ('var', 'exitCode')),
    ),

    # fun test() int64
    ('fun', 'test', (), 'int64',
      # return 3
      ('return', ('int64', 3)),
    ),

    # fun main() int64
    ('fun', 'main', (), 'int64',
      # int64 ing = 1
      ('def', 'ing', 'int64'),
      ('set', ('var', 'ing'), ('int64', 1)),

      # ing = test()
      ('set', ('var', 'ing'), ('call', 'test')),

      # int64 __exitCode = 1
      ('def', '__exitCode', 'int64'),
      ('set', ('var', '__exitCode'), ('int64', 1)),

      # int64 __exitCode = ing
      ('set', ('var', '__exitCode'), ('var', 'ing')),

      # exit(__exitCode)
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
