# Steps for compilation

## main (special)

## generic

1. Put constant values into .rodata and give them unique names
1. .text:
  1. Make space in the stack for all local variables and for all call structs that will be needed  
    Note, this is highly inefficient as registers could (and should!) be used when possible, I'll worry about this later.  
    For example, in:
    ```ulang
	fun testFamily(*Person A) /* bool */ {
	  C = A.children[0]
	  D = copy(C) // TODO: depth

	  equivalent = C == D // Have the same value
	  theSame = C === D // Same pointer
	  print("[testFamily]", C, D, equivalent, theSame, C === C, D === D)

      delete(D)
	  return equivalent && !theSame
	}
	```
    The local variables are: `C : *Person`, `D : *Person`, `equivalent : bool`, `theSame : bool`, `b0 : bool` (`C === C` in print), `b1 : bool` (`D === D` in print), `res : bool`.  
    And the call structs are the ones for: `(A.)array[0]`, `copy(C)`, `print(...)`, `delete`.  
    So the stack frame should be of `size = 2 * sizeof(*Person) + 5 * sizeof(bool) + sizeof(TODO: Call structs)`

## Parser
### Steps
1. Split by spaces (except when inside "")
1. For each file
  1. Create (file, path, CODE)  
    Where CODE is (...) of:
    * (type, NAME, DEF)  
      Where DEF is a combination of type names or a struct
    * 

### TODO
#### Built-in types
 * (u)int8, (u)int16, (u)int32 = (u)int, (u)int64
 * float32 = float, float64
 * byte = uint8
 * \* (pointer)

 They have defined
 * arithmetic (+, -, \*, /, //, !, &&, ||) //TODO: What else?
 * conversion between them (int <-> float, etc.) //TODO: Rules
 * arithmetic between them (via conversion int * float -> float * float) //TODO: Hierarchy
 * pointers also have ptr[i] defined

#### Provided types
 * char (ASCII and UTF-8)
 * string (ASCII and UTF-8)
 * bool
 * array[T]
 * list[T]
 * map[K, T]
 * TODO: Expand

### Expressions
 In general "(...)" is taken to mean a list of expressions of any type.
 * (lib, NAME, (...)), describes a library //TODO  
  `library NAME` as the first expression
 * (file, PATH, (...)), describes a file
 * (import, (...FILEPATH or LIBNAME)), imports other files and libraries
  `import (...FILEPATH or LIBNAME)` somewhere in the file (is imported for the entire file)
  //TODO: Selective and named imports

 * (typename, NAME, (TYPE\_NAME))

 * (type, NAME, TYPENAME or STRUCT) describes a type  
 `type bool = int8` -> (type, bool, int8)
 * (ttype, NAME, (...TEMPLATE\_TYPENAMES), TYPENAME or STRUCT) describes a template type. //TODO: Also template constants and functions, and set default values, like C++  
 `type array[T] = struct {...}` -> (ttype, array[], (T), (struct, ...))

  * (param, NAME, TYPENAME), describes a parameter
  * (param, NAME, TYPENAME, DEFAULTVALUE), describes a parameter with a default value
    TYPENAME might be a list with first the actual typename and then template replacements in order:
    `array[int8] foo` -> (param, foo, (array[], int8))
  * (struct, (...PARAM)), describes a data structure
  ```
  struct {
    string name
    int8 age
  }
  ```
  -> (struct, ((param, name, string), (param, age, int8)))

  * (fun, NAME, (...PARAM), (...TYPENAME), (...)), describes a function
  `fun startFamily(*Person A, B) bool {...}` -> (fun, startFamily, ((\*Person, A), (\*Person, B)), (bool), (...))
  `fun (Person p) marry(*Person spouse) *Person {...}` -> `fun marry(*Person p, *Person spouse) *Person {...}` //TODO: Difference between `fun (*Person p)` and `fun (Person p)`?
  * (tfun, NAME, (...TEMPLATE\_TYPENAMES), (...PARAM), (...TYPENAME), (...)), describes a template function. //TODO: Same todo as ttype  
  `fun foo[T, U](T a, U b) (T, U, bool) {...}` -> (tfun, foo[], (T, U), ((T, a), (U, b)), (T, U, bool), (...))

#### Actions
  * (call, FUNNAME, (...VARNAME), (...(PARAMNAME, VARNAME))), calls FUNNAME with VARNAMEs in matching order and (PARAMNAME, VARNAME)s matching by PARAMNAME  
  `print(A, B, sep = "\n")` -> (call, print, (A, B), (sep, "\n"))  
  Looks for a single function that:
    * Has the same name
    * Has the same number of parameters // TODO: Actually it should accept less based on default values and named parameters, figure out the arithmetic here
    * Each parameter matches the provided var's type

  * (set, VARNAME, NEWVALUE) where NEWVALUE is an expression  
    Sets the value of the second into the first
    `int foo = bar()` -> (set, foo, (call, bar, (), ()))

  * (pset, VARNAME or PTR, NEWVALUE) where PTR would be a constant pointer  
    Sets the value of the second into where the first one points.  
    `*int foo = bar()` -> (pset, foo, (call, bar, (), ())) (or set if bar returns a pointer to an integer, is inferred) //TODO: Better explanation

  * (return, VARNAME or CONSTVALUE), returns a value and exits a function
  * (if, COND, (...), (...)) where COND is an expression that returns a bool, executes the first path if true, or the second path if fals

  * (construct, VARNAME, TYPENAME, (...VARNAME)), constructs an element of the type into a variable //TODO: On the stack for compiled //TODO: Infers wether to pset or set based on type of varname and typename
  NOTE: &Type{} doesn't construct, but rather calls new and constructs into it //TODO: Better explanation

  * (&, VARNAME) returns a pointer to this variable
  * (!, COND) where cond is a boolean expression, not
  * TODO...

### TODO
* Sort-of keywords: typeof(X)
* Multi-line expressions

