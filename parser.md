# Parser

## Types
### Built-in types
 * (u)int8, (u)int16, (u)int32 = (u)int, (u)int64
 * float32 = float, float64
 * byte = uint8
 * \* (pointer)

 They have defined
 * arithmetic (+, -, \*, /, //, !, &&, ||) //TODO: What else?
 * conversion between them (int <-> float, etc.) //TODO: Rules
 * arithmetic between them (via conversion int * float -> float * float) //TODO: Hierarchy
 * pointers also have ptr[i] defined

### Provided types
 * char (ASCII and UTF-8)
 * string (ASCII and UTF-8)
 * bool
 * array[T]
 * list[T]
 * map[K, T]
 * TODO: Expand

## Expressions
In general "(...)" is taken to mean a list of expressions of any type.  
TODO: Sort

### Keyword
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

### General
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

## Steps

### File

0. Init
1. Split into lines
1. Search until finding first expression
  1. Apply steps for an expression
1. Repeat with the next expression

### Expression
0. Init
```
fun (array[T] a) append(T newElement) size_t {
  if a.elements == NULL || a.size == a.maxSize {
    a.expand()
  }

  a[a.size] = newElement
  a.size += 1
  return a.size
}
```
1. Receives only the first line
```
fun (array[T] a) append(T newElement) size_t {
```
1. Split by spaces except when inside (), [], {}, or ""
```
(fun, \(array[T] a\), append(T newElement), size_t, {)
```
1. Identify based on first element (in this case it's a function) and current scope.  
  If no keyword matches, it's a general expression.
1. Apply steps based on type of expression and current scope

#### Type
0. Init
```
type array[T] = struct {
  *T elements = nil
  size_t size = 0
  size_t maxSize = 0
}
```
1. Will be left at
```
(type, array[T], =, struct, {)
```
1. Second is name
1. Third has to be "="
1. Fourth is either typename or struct //TODO: Is struct unnecesary?
  1. If typename, parse it as such
  1. If struct will parse next few lines until "}" as struct

#### Struct
0. Was left at
```
// type array[T] = struct { // This line has already been read
  *T elements = nil
  size_t size = 0
  size_t maxSize = 0
}
```
1. Build
```
(struct)
```
1. Read and parse as variables the next lines until closing "}" (drop the "}") and put them at the end // TODO: Nothing trailing after "}"
```
(struct, (...))
```

#### Variable
0. Was left at
```
  *T elements = nil
```
1. If there's an "="
  1. Split at "="
1. Split the first (or whole if no "=") part by spaces, has to be of length 1 or 2.
  1. If 1 and "=" infer type from second part //TODO: When?
  1. If 1 and no "=", error
  1. If 2 first is typename, second is name
```
  (elements, *T)
```
1. If there was an "=", parse second part as expression and put it at the end
```
  (elements, *T, nil)
```

#### Function
0. Was left at
```
(fun, \(array[T] a\), append(T newElement), size_t, {)
```
1. Check if second is for a struct function or function\_def //TODO: How?
  1. In this case is for a struct function, so third is function\_def //TODO: How to parse it?
    ```
    (fun, \(array[T] a\), append, ((newElement, T)), size_t, {)
    ```
  1. Add second as first parameter //How?
    ```
    (fun, append, ((a, array[], T), (newElement, T)), size_t, {)
    ```
1. Fifth and until "{" are outputs, also drop "{" //NOTE: Current fifth
```
(fun, append, ((a, array[], T), (newElement, T)), (size_t))
```
1. Read lines and parse them as expressions until next "}" (and drop the "}") // TODO: Nothing trailing after "}", put that at the end
```
(fun, append, ((a, array[], T), (newElement, T)), (size_t), (...))
```

#### General
0. Was left at
```
  a.size += 1
```
1. TODO
