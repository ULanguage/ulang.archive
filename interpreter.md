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
  1. TODO: Global variables
1. Execute main //TODO: Args

## Execution
Pseudo-code, assumes "state" variable that holds the current state

### `(set, VARNAME, EXPRESSION)`
```
state.set(VARNAME, state.execute(EXPRESSION))
return state.get(VARNAME)
```

### `(construct, TYPE, (...PARAMETER))`
```
tmp = TODO
return tmp
```

### `(call, TYPE, (...PARAMETER))`
```
tmp = TODO
return tmp
```
