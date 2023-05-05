from compiler import Compile
from interpreter import Execute
from expr import Expr

if __name__ == '__main__':
  main = Expr.construct(('file', 'main.u',
    # int64 globA = 0
    ('def', 'globA', 'int64', ('int64', 0)),

    # int64 globB = 1
    ('def', 'globB', 'int64', ('int64', 1)),

    # fun getGlob() int64 {
    ('fun', 'getGlob', 'int64', (),
      # return globA
      ('return', ('var', 'globA')),
    ), # }

    # fun setGlob(int64 newValue = getGlob())) {
      ('fun', 'setGlob', 'int64', (('param', 'newValue', 'int64', ('int64', 4)),),
      # globA = newValue
      ('set', ('var', 'globA'), ('var', 'newValue')),
    ), # }
    # fun main() int64 {
    ('fun', 'main', 'int64', (),
      # var ing = 2
      ('def', 'ing', '', ('int64', 2)),

      # ing = 3 # TODO: int32
      ('set', ('var', 'ing'), ('int32', 3)),

      # setGlob()
      ('call', 'setGlob'),

      # ing = getGlob()
      ('set', ('var', 'ing'), ('call', 'getGlob')),

      # return ing
      ('return', ('var', 'ing')),
    ), # }
  ))

  Execute(main)
  Compile(main, 'main.asm')
