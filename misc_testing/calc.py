import lrparsing
from lrparsing import * 

class CalcParser(lrparsing.Grammar):
    class T(lrparsing.TokenRegistry):
        number = Token(re='\d+(\.\d+)?') # TODO: Hex and binary # TODO: Spaces
        ident = Token(re='[A-Za-z_][A-Za-z_0-9]*')
        eol = Choice(';', '\n', '\r')

        var = Keyword('var')

    _expr = Ref('_expr')
    
    #************************************************************
    #* S: Math **************************************************

    add = _expr << '+' << _expr
    sub = _expr << '-' << _expr
    prod = _expr << '*' << _expr
    div = _expr << '/' << _expr
    exp = _expr << '^' << _expr
    neg = '-' << _expr
    _arithm = Prio(neg, exp, prod, div, sub, add)

    eq = _expr << '==' << _expr
    neq = _expr << '!=' << _expr
    less = _expr << '<' << _expr
    greater = _expr << '>' << _expr
    leq = _expr << '<=' << _expr
    geq = _expr << '>=' << _expr
    le_le = _expr << '<' << _expr << '<' << _expr
    le_leq = _expr << '<' << _expr << '<=' << _expr
    leq_le = _expr << '<=' << _expr << '<' << _expr
    leq_leq = _expr << '<=' << _expr << '<=' << _expr
    _ineq = Choice(eq, neq, Prio(le_le, le_leq, less), Prio(leq_le, leq_leq, leq), greater, geq)

    land = _expr << '&&' << _expr
    lor = _expr << '||' << _expr
    implies = _expr << '->' << _expr
    _boolArithm = Prio(land, lor, implies)

    _math = Prio(_arithm, _ineq, _boolArithm)

    #************************************************************
    #* S: Variables *********************************************

    # type = Choice(Repeat('*') + T.ident, T.var)
    # Def = type + T.ident
    Def = T.var + T.ident
    set = _expr >> '=' >> _expr

    _vars = Choice(Def, set)

    #************************************************************
    #* S: Functions *********************************************

    call = _expr + '(' + List(_expr, ',') + ')'

    #************************************************************
    #* S: Main **************************************************

    _atom = Choice(T.number, T.ident, '(' + _expr + ')', call) # TODO: (_expr) causes problems with call
    _expr = Prio(
      _atom,

      # call,

      _math,
      _vars,
    )
    line = Prio(_expr + T.eol, _expr, T.eol)
    START = Repeat(line)
    COMMENTS = (
      Token(re='/[*](?:[^*]|[*][^/])*[*]/') |
      Token(re='//(?:[^\r\n]*(?:\r\n?|\n\r?))')
    )

# compile_grammar(CalcParser)
parse_tree = CalcParser.parse('''
/*
2 + 1 == 3
1 - 3 != -2
3 * 5 < 15
1 - 3 * 5 > -14
3 * 5^2 <= 76
5^2 / 2 >= 12.5
2 + 1 - (3 * 5)^2 / 3
1 == 5 > 6 < 7
1 < i < 5
1 < i <= 5
1 <= i < 5
1 <= i <= 5
i == 0 -> true && 1 <= j <= 5 -> i < j
*/
(var foo = 1)
var foo = main()
foo = main(1)
foo = main(bar)
foo = main(bar, 1)
foo = main(bar, bar, strlen())
                              /*
foo(1, bar, strlen())
                              */
''')
print(CalcParser.repr_parse_tree(parse_tree))

print(unused_rules(CalcParser))
# print(repr_parse_table(CalcParser))
