import lrparsing
from lrparsing import * 

class UParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        integer = Token(re='[0-9]+')
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        
        int64 = Keyword('int64')
        int32 = Keyword('int32')
        _type = Choice(int64, int32)
        pointer = '*' + _type
        type = Choice(_type, pointer)

    expr = Ref('expr')
    atom = T.ident | T.integer | '(' + expr + ')'
    block = '{' + Repeat(expr) + '}'

    param = Opt(T.type) + T.ident
    returns = '(' + List(T.type, ',') + ')' | T.type
    _fun = '(' + List(param, ',') + ')' + (returns | THIS*0) + block
    fun = Keyword('fun') + T.ident + _fun
    lamb = Keyword('fun') + _fun

    file = Repeat(expr)

    var = (T.type | Keyword('var')) + T.ident + Opt('=' + expr)
    set = atom + '=' + expr
    ref = '&' + atom
    deref = '*' + atom

    expr = Prio( # TODO: Order?
      atom,
      block,
      fun, lamb,
      var, set,
      ref, deref,
    )
    START = file
    COMMENTS = (
      Token(re='/[*](?:[^*]|[*][^/])*[*]/') |
      Token(re='//[^\n]*') # TODO: ^T.eol
    )
    WHITESPACE = ' ;\n'

# parse_tree = UParser.parse('/* This is an\n * Example\n */\nfun main() int32 {\n\ttest() // Call a function\n  return 0\n}')
# parse_tree = UParser.parse('ia = test(a)\ning = test(a, b, c) /* Call a function */')
parse_tree = UParser.parse('''
fun main
(int64
a, b
,
*int32 c)
(int32/*asd*/, *int64) {
a
                           int32 z = 5
                           var x
                           x = 5

var foo = fun() {}
  b // This is comment*/
  *z
  &asdasd
c}
''')
print(UParser.repr_parse_tree(parse_tree))
