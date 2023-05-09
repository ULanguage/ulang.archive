import lrparsing
from lrparsing import * 

class UParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        integer = Token(re='[0-9]+')
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        eol = Choice('\n', ';')

    expr = Ref('expr')
    atom = T.ident | T.integer | '(' + expr + ')'
    block = '{' + Repeat(T.eol) + Repeat(expr + Repeat(T.eol)) + '}'

    fun = Keyword('fun') + T.ident + '(' + List(T.ident, ',', min = 0) + ')' + block
    file = Repeat(T.eol) + Repeat((block | fun) + Repeat(T.eol))

    expr = Prio(
      atom,
      block,
      fun,
    )
    START = file
    COMMENTS = (
      Token(re='/[*](?:[^*]|[*][^/])*[*]/') |
      Token(re='//[^\n]*') # TODO: ^T.eol
    )
    # WHITESPACE = ' '

# parse_tree = UParser.parse('/* This is an\n * Example\n */\nfun main() int32 {\n\ttest() // Call a function\n  return 0\n}')
# parse_tree = UParser.parse('ia = test(a)\ning = test(a, b, c) /* Call a function */')
parse_tree = UParser.parse('''
fun main (a, b) {
a
  b // This is comment*/
c}
{
a
b}
''')
print(UParser.repr_parse_tree(parse_tree))
