import scope
from scope import scope_t

if __name__ == '__main__':
  prog = (
    # int64 glob = 1
    ('def', 'glob', 'int64', ('int64',  1)),

    # fun exit(int64 exitCode) int64
    ('fun', 'exit', (('param', 'exitCode', 'int64'),), 'int64',
      # exit exitCode
      ('exit', ('var', 'exitCode')),
    ),

    # fun getGlob() int64
    ('fun', 'getGlob', (), 'int64',
      # return glob
      ('return', ('var', 'glob')),
    ),

    # fun setGlob(int64 newGlob) int64
    ('fun', 'setGlob', (('param', 'newGlob', 'int64'),), 'int64',
      ('set', ('var', 'glob'), ('var', 'newGlob')),
    ),

    # fun main() int64
    ('fun', 'main', (), 'int64',
      # int64 ing = 1
      ('def', 'ing', 'int64'),
      ('set', ('var', 'ing'), ('int64', 2)),

      # setGlob(ing)
      ('call', 'setGlob', ('var', 'ing')),

      # int64 __exitCode = getGlob()
      ('def', '__exitCode', 'int64'),
      ('set', ('var', '__exitCode'), ('call', 'getGlob')),

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
