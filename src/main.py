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

    ('def', 'fpath', '*char', ('*char', 0)),
    ('def', '_fpath0', 'char', ('char', 47)), # TODO: Define arrays
    ('def', '_fpath1', 'char', ('char', 116)),
    ('def', '_fpath2', 'char', ('char', 109)),
    ('def', '_fpath3', 'char', ('char', 112)),
    ('def', '_fpath4', 'char', ('char', 47)),
    ('def', '_fpath5', 'char', ('char', 120)),
    ('def', '_fpath6', 'char', ('char', 0)),

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
    ('def', '_message11', 'char', ('char', 10)),
    ('def', '_message12', 'char', ('char', 0)),

    ('fun', 'main', 'int64', (),
      ('set', ('var', 'message'), ('ref', ('var', '_message0'))), # TODO
      ('set', ('var', 'fpath'), ('ref', ('var', '_fpath0'))), # TODO

      ('call', 'write', ('int64', 1), ('var', 'message'), ('int64', 12)),
    ),
  ))

  Compile(main, args.o)
