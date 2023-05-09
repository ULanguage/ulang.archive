import lrparsing
from lrparsing import * 

class UParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        integer = Token(re='[0-9]+')
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        eol = Choice('\n', ';')

    expr = Ref('expr')
    atom = T.ident | T.integer | '(' + expr + ')' | '()'

    block = '{' + Repeat(T.eol) + Repeat(expr + Repeat(T.eol)) + '}'
    file = Repeat(T.eol) + Repeat(block + Repeat(T.eol))

    expr = Prio(
      atom,
      block,
    )
    START = file
    COMMENTS = Token(re='/[*](?:[^*]|[*][^/])*[*]/')
    # WHITESPACE = ' '

# parse_tree = UParser.parse('/* This is an\n * Example\n */\nfun main() int32 {\n\ttest() // Call a function\n  return 0\n}')
# parse_tree = UParser.parse('ia = test(a)\ning = test(a, b, c) /* Call a function */')
parse_tree = UParser.parse('\n{\na\n\tb\nc}\n{\na\t\nb}')
print(UParser.repr_parse_tree(parse_tree))
