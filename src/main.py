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

    # fun setGlob(*int64 var) {
    ('fun', 'setGlob', 'int64', (('param', 'var', '*int64', ()),),
      # globA = *var
      ('set', ('var', 'globA'), ('deref', ('var', 'var'))),
    ), # }

    # fun main() int64 {
    ('fun', 'main', 'int64', (),
      ('return', ('ref', ('var', 'globA'))),
      # var ing = 2
      ('def', 'ing', '', ('int64', 2)),

      # ing = 31
      ('set', ('var', 'ing'), ('int64', 31)),

      # setGlob(&ing)
      ('call', 'setGlob', ('ref', ('var', 'ing'))),

      # ing = getGlob()
      # ('set', ('var', 'ing'), ('call', 'getGlob')),

      # ing = 31
      ('set', ('var', 'ing'), ('int64', 31)),
      # int64 foo = 4
      ('def', 'foo', 'int64', ('int64', 4)),

      # int64 bar0 = 1
      ('def', 'bar0', 'int64', ('int64', 0)),
      # int64 bar1 = 1
      ('def', 'bar1', 'int64', ('int64', 0)),

      ('if', ('var', 'bar0'), (
        ('if', ('var', 'bar1'), (
          ('return', ('/', ('var', 'ing'), ('var', 'foo'))),
        ), (
          ('return', ('%', ('var', 'ing'), ('var', 'foo'))),
        )),
      ), (
        ('return', ('*', ('var', 'ing'), ('var', 'foo'))),
      )),

      # return ing + var
      ('return', ('+', ('var', 'ing'), ('var', 'foo'))),
    ), # }
  ))

  if args.compile:
    Compile(main, args.o)
  else:
    Execute(main)
