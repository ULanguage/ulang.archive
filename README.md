# ULang
## Roadmap

* I think it's close to being able to compile itself, so next is:  
  * Implementing what is actually needed to compile itself
    - [X] Boolean logic
    - [X] int8 = char, int16, int32, int64
    - [X] Basic array manipulation
    - [X] Basic string manipulation
    - [ ] Export functions and import other .u files
    - [ ] Import and call C functions
    - [ ] For loops
    - [ ] Data structures
    - [ ] Main arguments
  * Removing what isn't needed (but is already implemented or halfway)
    - [X] Variable types
    - [X] Calling functions based on more than name
- [ ] Implement Rule 110 to prove it's Turing-complete, mark as (v0.1.0)
- [ ] Write a self-compiler Tag as v0.2.0
  * Must read .parsed.u files, and then compile them writing an .asm file for each and call nasm and ld on them
- [ ] Write an interpreter. v0.3.0
- [ ] Extreme future:
  1. More features:
    * Inline assembly (replace libc?)
    * Better debug during exection
    * Better management of registers
    * Casting variables (convert intrinsic)
    * "Levels"
    * ...
  1. Define a syntax
  1. Write a parser
