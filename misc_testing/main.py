import lrparsing
from lrparsing import * 

class UParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        integer = Token(re='[0-9]+') # TODO: Hex and binary
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        eol = Choice(';', '\n', Token(re='\Z'))

        char = Token(re="'.'")
        string = Token(re='".*"')

        int64 = Keyword('int64')
        int32 = Keyword('int32')
        int16 = Keyword('int16')
        int8 = Keyword('int8')
        char = Keyword('char')
        bool = Keyword('bool')
        _type = Choice(int64, int32, int16, int8, char, bool)
        pointer = Some('*') + _type
        type = Choice(_type, pointer)

        true = Keyword('true')
        false = Keyword('false')

        _import = Keyword('import') | Keyword('cimport')
        _from = Keyword('from')

    expr = Ref('expr')
    line = Ref('line')

    atom = (
      T.ident | T.integer |
      T.type | T.true | T.false |
      ('(' + Repeat(T.eol) + expr + Repeat(T.eol) + ')')
    )
    block = '{' + Repeat(T.eol) + Repeat(line) + Opt(expr) + '}' # TODO: Opt(epxr) is a hack to match c in {b; c}

    param = Opt(T.type) + T.ident
    returns = '(' + List(T.type, ',') + ')' | T.type
    _fun = '(' + List(param, ',') + ')' + (returns | THIS*0) + block
    fun = Keyword('fun') + T.ident + _fun
    lamb = Keyword('fun') + _fun

    _else = Keyword('else') + block
    _elif = Keyword('elif') + expr + block
    _if = Keyword('if') + expr + block + Repeat(_elif) + Opt(_else) 

    _while = Keyword('while') + expr + block

    call = atom + '(' + List(expr, ',') + ')'
    ret = Keyword('return') + Opt('(' + List(expr, ',') + ')')

    _import = T._import + T.string
    _from = T._from + T.string + T._import + '(' + List(T.ident, ',') + ')'

    expr = Prio( # TODO: Check order
      atom,
      block,
      '(' + T.type + ')(' + THIS + ')', # Casting
      (T.type | Keyword('var')) + T.ident, # Variable definition: "var a" or "int64 a"
      '++' >> THIS, THIS << '++', 
      THIS << Tokens('= += -= *= /= %= &= |=') << THIS, # Setting "a = b", also matches for definitions "var a = b" # TODO: *= and others
      THIS + '[' + THIS + ']', # Array access
      Tokens('& *') >> (T.ident | '(' + THIS + ')'), # Pointer manipulation "&a" or "*a" or "*(123)"
      Tokens("+ - !") >> THIS,
      THIS << Tokens("* / %") << THIS,
      THIS << Tokens("+ - & |") << THIS,
      THIS << Tokens("== != < > <= >=") << THIS,
      THIS << Tokens("&& ||") << THIS,
      fun, _if, _while, call, ret,
      _from, _import,
    )

    line = expr + Some(T.eol)
    file = Repeat(T.eol) + Repeat(line)

    START = file
    COMMENTS = (
      Token(re='/[*](?:[^*]|[*][^/])*[*]/') |
      Token(re='//(?:[^\r\n]*(?:\r\n?|\n\r?))')
    )
    # WHITESPACE = ' '

parse_tree = UParser.parse('''
from "fncntl.h" cimport (open, read, write) // TODO: import open, read, write

fun strlen(*char str, int64 maxLen) int64 {
  int64 len = 0
  while *(str++) {
    len++
  }
  return (len) // TODO: return len
}

fun main(int32 argc, **char argv) int32 {
  if argc {
    var idx = 0
    while (idx < argc) {
      write(1, argv[idx], strlen(argv + idx))
    }
  }
}
''')
print(UParser.repr_parse_tree(parse_tree))
