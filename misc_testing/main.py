import lrparsing
from lrparsing import * 

class UParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        integer = Token(re='[0-9]+') # TODO: Hex and binary
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        
        int64 = Keyword('int64')
        int32 = Keyword('int32')
        int16 = Keyword('int16')
        int8 = Keyword('int8')
        char = Keyword('char')
        bool = Keyword('bool')
        _type = Choice(int64, int32, int16, int8, char, bool)
        pointer = '*' + _type
        type = Choice(_type, pointer)

        true = Keyword('true')
        false = Keyword('false')

        eol = Choice(';', '\n', Token(re='\Z'))

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

    expr = Prio( # TODO: Check order
      atom,
      block,
      '(' + T.type + ')(' + THIS + ')', # Casting
      (T.type | Keyword('var')) + T.ident, # Variable definition: "var a" or "int64 a"
      THIS << '=' << THIS, # Setting "a = b", also matches for definitions "var a = b" # TODO: +=
      Tokens('& *') >> (T.ident | '(' + THIS + ')'), # Pointer manipulation "&a" or "*a" or "*(123)"
      Tokens("+ - !") >> THIS,
      THIS << Tokens("* / %") << THIS,
      THIS << Tokens("+ -") << THIS,
      THIS << Tokens("== !=") << THIS,
      THIS << Tokens("&& ||") << THIS,
      fun, _if, _while, call, ret,
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
fun times(int64 a, b) int64 {
  int64 res = a
  while ((b = b - 1) != 0) {
    res = res + a
  }
  return (res)
}

fun main(int64 a, b, *int64 c) (int64, bool) {
  var sum = times(a, b)
  // sum = (int32)(a + b); *c = sum; *(c + 1) = &sum
  if sum == 42 {
    return (sum, true)
  } elif sum + 1 == 42 || sum - 1 == 42 {
    return (sum, true)
  } else {
    return (sum, false)
  }
  /* TODO
  return (
    sum,
    sum == 42
  )
  return sum, sum == 42
  */
}
''')
print(UParser.repr_parse_tree(parse_tree))
