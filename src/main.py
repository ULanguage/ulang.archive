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
    ('def', 'zero', 'int', ('int', 48)), # Character '0'
    ('def', 'one', 'int', ('int', 49)), # Character '1'

    ('fun', 'main', 'int', (),
      ('&&', ('bool', False), ('bool', False)),
      ('||', ('bool', True), ('bool', False)),
      ('!', ('bool', True), ()),
    ),
  ))

  if args.compile:
    Compile(main, args.o)
  else:
    Execute(main)
