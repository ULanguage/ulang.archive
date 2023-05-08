from compiler import Compile
from expr import Expr

from debug import setDebug, setLogMask
from utils import parseArgs

if __name__ == '__main__':
  args = parseArgs()

  setLogMask(args.logMask.split(','))
  setDebug(args.debugMask.split(','))

  main = Expr.construct(('file', 'main.u',
    ('cimport', 'open', 'int64', ('param', 'filename', '*char', ()), ('param', 'flags', 'int64', ()), ('param', 'mode', 'int64', ())),
    ('cimport', 'write', 'int64', ('param', 'fd', 'int64', ()), ('param', 'buf', '*char', ()), ('param', 'count', 'int64', ())),
    ('cimport', 'read', 'int64', ('param', 'fd', 'int64', ()), ('param', 'buf', '*char', ()), ('param', 'count', 'int64', ())),

    ('fun', 'strlen', 'int64', (('param', 'str', '*char', ()), ('param', 'maxLen', 'int64', ('int64', 256))),
      ('def', 'len', 'int64', ('int64', 0)),

      # ('while', ('&&', ('deref', ('var', 'str')), ('-', ('var', 'maxLen'), ('var', 'len'))),
      ('while', ('deref', ('var', 'str')),
        ('set', ('var', 'len'), ('+', ('var', 'len'), ('int64', 1))),
        ('set', ('var', 'str'), ('+', ('var', 'str'), ('*char', 1))),
      ),

      ('return', ('var', 'len')),
    ),

    ('fun', 'main', 'int64', (),
      ('def', 'message', '*char', ()),
      ('def', 'idx', '**char', ('**char', 0)),
      ('if', ('var', 'argc'),
        (
          ('while', ('+', ('var', 'idx'), ('**char', 1)),
            ('set', ('var', 'message'), ('deref', ('+', ('var', 'argv'), ('var', 'idx')))),
            ('return', ('call', 'strlen', ('var', 'message'))),
            ('call', 'write', ('int64', 1), ('var', 'message'), ('call', 'strlen', ('var', 'message'))),
            ('set', ('var', 'idx'), ('-', ('var', 'idx'), ('**char', 1))),
          ),
        ), ()
      ),
    ),
  ))

  Compile(main, args.o)
