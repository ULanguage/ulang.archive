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

### Expressions
#### Types
 * (file, PATH, (...)), describes a file
 * (import, (...FILEPATH or LIBNAME)), imports other files //TODO: Other types of imports
 * (type, NAME, DEF) where DEF is either another typename or struct, describes a type
 * (struct, (...PARAM)), describes a data structure
 * (fun, NAME, (...PARAM), (...TYPENAMES), (...)), describes a function
 * (tfun, TYPENAME, NAME, (...PARAM), (...TYPENAMES), CODE), describes a function for a type
 * Param: (TYPENAME, VARNAME) or (TYPENAME, VARNAME, DEFAULTVALUE), describes a paramter for a function or struct

#### Actions
  * (set, VARNAME, NEWVALUE) where NEWVALUE is an expression, sets the value of the second into the first
  * (call, FUNNAME, (..VARNAME)), calls funname with varnames as // TODO: Setting values like in `sep = "\n"`
  * (return, VARNAME or CONSTVALUE), returns a value from a fucntion
  * (if, COND, (...) truePath, (...) elsePath) where COND is an expression that returns a bool, executes the first path if true, or the second path if false
  * (new, TYPENAME, (...VARNAME)), returns a pointer to a new element of the type
  * (construct, VARNAME, TYPENAME, (...VARNAME)), constructs an element of the type //TODO: Where?
  * (&, VARNAME) returns a pointer to this variable
  * (!, COND) where cond is a boolean expression, not
  * TODO...

### TODO
* Keywords: fun, tfun, set, new, construct, if, call, return, !, ===, &&, ||, +, -
* Sort-of keywords: typeof(X)
* 
* Multi-line expressions

