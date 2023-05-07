from compiler import Compile
from expr import Expr

from debug import setDebug, setLogMask
from utils import parseArgs

if __name__ == '__main__':
  args = parseArgs()

  setLogMask(args.logMask.split(','))
  setDebug(args.debugMask.split(','))

  main = Expr.construct(('file', 'main.u',
    ('def', 'message', '*char', ('*char', 0)),
    ('def', '_message0', 'char', ('char', 65)), # TODO: Define arrays
    ('def', '_message1', 'char', ('char', 104)),
    ('def', '_message2', 'char', ('char', 111)),
    ('def', '_message3', 'char', ('char', 121)),
    ('def', '_message4', 'char', ('char', 32)),
    ('def', '_message5', 'char', ('char', 116)),
    ('def', '_message6', 'char', ('char', 104)),
    ('def', '_message7', 'char', ('char', 101)),
    ('def', '_message8', 'char', ('char', 114)),
    ('def', '_message9', 'char', ('char', 101)),
    ('def', '_message10', 'char', ('char', 33)),
    ('def', '_message11', 'char', ('char', 0)),

    ('def', 'zero', 'char', ('char', 48)), # Character '0'
    ('def', 'one', 'char', ('char', 49)), # Character '1'

    ('fun', 'inc', 'int64', (('param', 'value', 'int64', ('int64', 0)),),
      ('return', ('+', ('var', 'value'), ('int64', 1))),
    ),

    ('fun', 'main', 'int64', (),
      ('set', ('var', 'message'), ('ref', ('var', '_message0'))),

      ('def', 'foo', '*char', ('*char', 0)),
      ('set', ('var', 'foo'), ('*char', 1)),
      ('set', ('var', 'foo'), ('var', 'message')),
      # ('set', ('var', 'foo'), ('+', ('var', 'message'), ('*char', 2))),
      ('set', ('deref', ('var', 'foo')), ('char', 5)),

      ('def', 'bar', 'int64', ()),
      ('set', ('var', 'bar'), ('call', 'inc')),
      ('set', ('var', 'bar'), ('call', 'inc', ('var', 'bar'))),
    ),
  ))

  Compile(main, args.o)
