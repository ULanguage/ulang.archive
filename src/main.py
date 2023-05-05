from compiler import Compile
from interpreter import Execute
from expr import Expr

from debug import setDebug, setLogMask
from utils import parseArgs

if __name__ == '__main__':
  args = parseArgs()

  setLogMask(args.logMask.split(','))
  setDebug(args.debugMask.split(','))

  main = Expr.construct(('file', 'main.u', # TODO: Read file
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
    ('fun', 'setGlob', 'int64', (('param', 'newValue', 'int64', ()), ('param', 'otherValue', 'int64', ()), ('param', 'thirdValue', 'int64', ())),
      # ('debug', 'debug', (), (('var', 'newValue'), ('var', 'otherValue'), ('var', 'thirdValue'))),
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
      ('call', 'setGlob', ('int64', 4), ('int64', 5), ('int64', 6)),

      # ing = getGlob()
      ('set', ('var', 'ing'), ('call', 'getGlob')),

      # return ing
      ('return', ('var', 'ing')),
    ), # }
  ))

  if args.compile:
    Compile(main, args.o)
  else:
    Execute(main)
