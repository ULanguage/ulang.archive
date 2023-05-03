# Compiler and interpreter

## File

1. Define vars, types, funs <!-- TODO: Anything else? options, libname, import -->
1. Alloc vars (based on type) and set default to all 0's
1. Begin compiling/executing main

## Fun

1. Skip if already compiled (with this signature)
1. Compile/Execute expressions in order
  * If compiling, queue funs (with this signature) to be compiled next
  * If executing, call funs along the way <!-- TODO: JIT? -->
1. If is main, exit rather than return
