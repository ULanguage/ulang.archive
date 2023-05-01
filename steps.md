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
1. Identify keywords

### TODO
* Keywords: fun, tfun, set, if, call, return, !, ===, &&, ||
* Sort-of keywords: typeof(X)
* Multi-line expressions

