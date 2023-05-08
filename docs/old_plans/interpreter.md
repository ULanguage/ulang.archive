# Interpreter

## Prepare

0. Get structure of expressions from parser
1. Build a graph of file and library dependencies (based on imports)
1. TODO: List exactly what each file imports (selective imports)
1. List exactly what each file exports (TODO: public/private, for now all defined functions and types are exported)
1. Check that only one file exports a main function
1. For each file:
  1. Define current scope as all imported files/libs and this file.
  1. Check if library, that it's the first expression
  1. TODO: Level
  1. Check that each used type exists in current scope
    Simply by name (array[], int) == (array[], int), but (array[], int) != (array[], char).  
    NOTE: Templates such as (array[], T) match with anything the same length (not with a possible (array[], T, U)).
  1. For each function  
    Define current scope as previous scope + this function.
    * Check that each used function exists in current scope (incl. new and construct). //TODO: Lambdas
      They must:
      * Belong to the same type (or none at all).
      * Have the same name. NOTE: Includes templates //TODO: Change this in parser explanation
      * Each provided positional parameter's type matches the respective parameter.
      * Each named parameter provided (and it's type) matches a parameter not already provided by positional one.
      * No parameters without value (provided or default).
    * Check that each used variable exists in current scope and is set (TODO: or defined) before being used.
    * For each set check the expression's final type matches the variable's (for first time, if not typed, this defines it's type) (also, change to setp if the case)
    * For all returns check it matches the function's return type
    * Check that all accesses to variable's elements exist (p.children.spouse)
    * Replace all typeof with the actual type //TODO: Wait until runtime in level 1
  1. TODO: Global variables
1. Execute main //TODO: Args

## Execution
Pseudo-code, assumes `state s` variable that holds the current state

### State
```ulang
type expr_t = struct {
  string type

  //TODO: Params for each type
}

type typeName_t = struct {
  string type
  array[string] templateVars
}

type namedParam_t = struct {
  string name
  var_t value
}

type params_t = struct {
  array[string] positional
  array[namedParam_t] named
}

type type_t = struct {
  string name
  bool isStruct

  // If !isStruct
  string actualType

  // If isStruct
  map[string, var_t] variables
  map[string, fun_t] functions
}

type var_t = type_t

type state = struct {
  map[string, type_t] types //NOTE: "" matches VOID type
  map[string, var_t] variables
  *state parent

  bool break
  bool continue
}

fun (*state s) newState() *state {
  return &state{parent = s}
}

fun (*state s) get(string varname, bool inParent = true) *var_t {
  *var_t v
  for idx, namePart in varname.split('.') {
    if idx == 0 {
      v = s.get(namePart)
    } else {
      v = v.get(namePart)
    }
  }

  if v == nil && s.parent != nil && inParent {
    v = s.parent.get(varname)
  }

  return v
}

fun (*state s) execute(expr_t expr) var_t {
  return s.EXPR(expr) //TODO
}

fun (*state s) call(typeName_t typeName, string funName, params_t params) var_t {
  // (call, typeName, funName, (...params))
  f = s.get(typeName.type + "." + funName)
  newS = s.newState()
  // TODO: newS define function and type templates

  // Assign parameters values in the new scope
  // TODO: Checks
  for idx, value in params.positional {
    newS.set(true, f.params[idx].name, value)
  }
  for idx, param in params.named {
    newS.set(true, param.name, param.value)
  }

  for _, expr in f.expressions {
    newS.execute(expr)
    if newS.return {
      // TODO: delete newS?
      return newS.res
    }
  }
}

fun (*state s) forin(expr_t expr) {
  // (forin, IDXNAME, VARNAME, RANGE_EXPR, ...SUBEXPRS)
  newS = s.newState()
  for idx, var in newS.execute(expr.RANGE_EXPR) {
    newS.set(idx, idx)
    newS.set(var, var)
    for _, subExpr in expr.exprs {
      newS.execute(subExpr)
      if newS.continue || newS.break {
        newS.continue = false
        break
      }
    }
    if newS.break {
      break
    }
  }
}

fun (*state s) break() {
  // (break)
  s.break = true
}

fun (*state s) continue() {
  // (continue)
  s.continue = true
}

fun (*state s) set(bool local, strig varname, expr_t expr) *var_t {
  // (set, local?, varname, expr)
  v = s.get(varname, inParent = !local)
  if v == null {
    //TODO: Check varname doesn't have any "."
    v = &var_t{}
    s.variables[varname] = v
  }
  *v = s.execute(expr)
  return v
}

fun (*state s) construct(typeName_t typeName, params_t params) var_t {
  // (construct, typeName, (...params))
  //TODO
}

fun (*state s) new(typeName_t typeName, params_t params) *var_t {
  // (new, typeName, (...params))
  //TODO
}

fun (*state s) if(expr_t condExpr, array[expr_t] trueExpr, falseExpr) {
  // (if, condExpr, trueExpr, falseExpr)
  newS = s.newState()

  exprs = trueExpr
  if !newS.execute(condExpr) {
    exprs = falseExpr
  }

  for _, expr in exprs {
    newS.execute(expr)
    if newS.break {
      break
    }
  }
}

fun (*state s) return(expr_t expr) var_t {
  // (return, expr)
  state.return = true
  return s.execute(expr)
}

fun (*state s) !(expr_t expr) var_t {
  // (!, expr)
  return !s.execute(expr)
}

//TODO: Arithmetic and other trivial expressions
```
