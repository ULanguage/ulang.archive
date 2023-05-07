from compiler import Compile
from interpreter import Execute
from expr import Expr

from debug import setDebug, setLogMask
from utils import parseArgs

if __name__ == '__main__':
  args = parseArgs()

  setLogMask(args.logMask.split(','))
  setDebug(args.debugMask.split(','))

  main = Expr.construct(('file', 'main.u',
    ('def', 'zero', 'char', ('char', 48)), # Character '0'
    ('def', 'one', 'char', ('char', 49)), # Character '1'

    ('fun', 'main', 'int', (),
      ('def', 'foo0', 'char', ('char', 48)),
      ('def', 'foo1', 'int8', ('int8', 48)),
      ('def', 'foo2', 'int16', ('int16', 48)),
      ('def', 'foo3', 'int32', ('int32', 48)),
      ('def', 'foo4', 'int64', ('int64', 48)),
    ),
  ))

  if args.compile:
    Compile(main, args.o)
  else:
    Execute(main)
