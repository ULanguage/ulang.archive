# ULang
## Roadmap

* I think it's close to being able to compile/interpret itself, so next is:  
  * Implementing what is actually needed to compile/interpret itself
    - [X] Boolean logic
    - [ ] int8, int16, int32, int64
    - [ ] Casting variables (convert intrinsic)
    - [ ] Basic array manipulation
    - [ ] Basic string manipulation
    - [ ] Calling C's stdlib for syscalls and malloc (temporary later will be implemented in U).  
    Since this would be too hard for interpretation (for now), I'll have only the next few functions:
      * malloc and free
      * read, write, open, close
      * exit
    - [ ] Import other .u files
    - [ ] For loops
    - [ ] Data structures (not classes though)
    - [ ] Main arguments
  * Removeing what isn't needed (but is already implemented or halfway)
    - [X] Variable types
    - [X] Calling functions based on more than name
- [ ] Implement Rule 110 to prove it's Turing-complete, mark as (v0.1.0)
- [ ] Write a self-compiler/interpreter. Tag as v0.2.0
  * Must read .parsed.u files, and:
    * If interpreting then execute them
    * Or if compiling then compile them writting an .asm file for each and call nasm and ld on them
- [ ] Extreme future:
  1. More features:
    * Inline assembly (replace libc?)
    * Better debug during exection
    * Better management of registers
    * "Levels"
    * ...
  1. Define a syntax
  1. Write a parser
