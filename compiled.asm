/************************************************************/
/* Highest level ********************************************/
/*
 * repl
 * garbage collector
 * type inference
 *
 */

// person.u

Person = struct {
  name
  age
  spouse
  children
}

fun (p Person) growUp() {
  p.age += 1
  // return p
}

fun (p Person) marry(spouse) {
  p.spouse = spouse
  spouse.spouse = p
  // return p
}

fun (p Person) haveChild(name, age = 0) {
  if name.empty() {
    return nil
  }

  newPerson = Person{name, age}

  p.children.append(newPerson)
  if p.spouse {
    p.spouse.children.append(newPerson)
  }

  return newPerson
}

// main.u

import (
  ./person.u
)

fun startFamily(A, B) {
  C = G.marry(S).haveChild("Gafia")
  N = S.haveChild("")

  print("[startFamily]", A, B, C, N, sep = ", ")
  // return true
}

fun testFamily(A) {
  C = A.children[0]
  D = copy(C)

  equivalent = C == D // Have the same value
  print("[testFamily]", C, D, equivalent)

  return equivalent
}

fun main(args) {
  A = Person{args[0], 22}
  B = Person{args[1], 21}

  if !startFamily(A, B) {
    print("[startFamily] Error")
    return 1
  } elif !testFamily(A) {
    print("[testFamily] Error")
    return 1
  }
  
  // return 0
}

/************************************************************/
/* Second level *********************************************/
/*
 * compiled
 *
 */

// person.u

type Person = struct {
  string name
  int age
  *Person spouse = nil
  array[*Person] children = array[*Person]{}
}

fun (p Person) growUp() /* *Person */ {
  p.age += 1
  // return p
}

fun (p Person) marry(*Person spouse) /* *Person */ {
  p.spouse = spouse
  spouse.spouse = p
  // return p
}

fun (p Person) haveChild(string name, int age = 0) *Person {
  if name.empty() {
    return nil
  }

  newPerson = &Person{name, age}

  p.children.append(newPerson)
  if p.spouse {
    p.spouse.children.append(newPerson)
  }

  return newPerson
}

// main.u

import (
  ./person.u
)

fun startFamily(*Person A, B) /* bool */ {
  C = G.marry(S).haveChild("Gafia")
  N = S.haveChild("")

  print("[startFamily]", A, B, C, N, sep = ", ")
  // return true
}

fun testFamily(*Person A) /* bool */ {
  C = A.children[0]
  D = copy(C)

  equivalent = C == D // Have the same value
  theSame = C === D // Same pointer (should be false)
  print("[testFamily]", C, D, equivalent, theSame, C === C, D === D)

  return equivalent && !theSame
}

fun main(args) /* int */ {
  A = Person{args[0], 22}
  B = Person{args[1], 21}

  if !startFamily(A, B) {
    print("[startFamily] Error")
    return 1
  } elif !testFamily(A) {
    print("[testFamily] Error")
    return 1
  }

  // return 0
}

;************************************************************
;* Third level **********************************************

;* constants *
; str1 "[startFamily] Error"
; str2 "[testFamily] Success"
; str3 "[testFamily]"

;* stdlib *
; TODO

fun new(size_t size) *byte { // Also used on &Person{} and &array[]{}
  malloc(size)
}

fun delete(*byte ptr) {
  free(size)
}

type array[T] = struct {
  // TODO ...
}

type string = struct {
  // TODO ...
}

fun print() {
  // TODO ...
}

;* person *
; TODO

/*
import (
  stdlib
)
*/

type Person = struct {
  string name
  int age
  *Person spouse = nil
  array[*Person] children = &array[*Person]{}
}

fun (p Person) growUp() /* *Person */ {
  p.age += 1
  // return p
}

fun (p Person) marry(*Person spouse) /* *Person */ {
  p.spouse = spouse
  spouse.spouse = p
  // return p
}

fun (p Person) haveChild(string name, int age = 0) *Person {
  if name.empty() {
    return nil
  }

  newPerson = &Person{name, age}

  p.children.append(newPerson)
  if p.spouse {
    p.spouse.children.append(newPerson)
  }

  return newPerson
}

; * main.u *

import (
  ./person.u
)

fun startFamily(*Person A, B) /* bool */ {
  C = G.marry(S).haveChild("Gafia")
  N = S.haveChild("")

  print("[startFamily]", A, B, C, N, sep = ", ")
  // return true
}

; fun testFamily(*Person A) bool
testFamily:
  ; Make space for C, D, equivalent, theSame, b1, b2, and res, on the stack ; NOTE: C and D are both pointers (inferred from return types) ; TODO: Also for all call structs
  ; Construct res with true (aka. 1)
  ;
  ; Construct call (struct) for "array[i]" with A.children and i = 0
  ; Call array[i] (with the call struct)
  ; Put the result into C
  ;
  ; Construct call for copy with C
  ; call copy
  ; put the result into D
  ; 
  ; Construct call for == with C and D
  ; Call ==
  ; put the result into equivalent
  ;
  ; Construct call for === with C and D 
  ; Call === ; NOTE === checks if they have the same ptr, so it shouldn't be a function
  ; put the result into theSame
  ;
  ; Construct call for === with C and C
  ; Call === ; NOTE === checks if they have the same ptr, so it shouldn't be a function
  ; put the result into b1
  ;
  ; Construct call for === with D and D
  ; Call === ; NOTE === checks if they have the same ptr, so it shouldn't be a function
  ; put the result into b2
  ;
  ; Construct call for print with str3, C, D, equivalent, theSame, b1, b2
  ; Call print
  ;
  ; Construct call for delete with D
  ; Call delete
  ;
  ; remove the stack frame
  ; res = equivalent && !theSame
  ; ret

; fun main(array[int] args) int
; TODO: Callable, have multiple entries, one for the OS (C abi) and another from runtime (ulang abi)
main:
  ; Follow C abi for args (argc, argv), and construct an array
  ;
  ; Make space for A, B, and res on the stack ; TODO: Also for all call structs
  ; Construct res with 0
  ; Construct A and B ; TODO
  ;
  ; Construct call struct for startFamily with A, B
  ; call startFamily with the call struct
  ; if !(result != 0)
  ;   construct call struct for print with str1
  ;   call print with the call struct
  ;   res = 1
  ;   GOTO .return
  ;   GOTO .endif
  ;
  ; Construct call struct for testFamily with A
  ; call testFamily with the call struct
  ; if !(result != 0)
  ;   construct call struct for print with str2
  ;   call print with the call struct
  ;   res = 1
  ;   GOTO .return
  ;   GOTO .endif
  ; .endif
  ;
  ; .return:
  ; remove the stack frame
  ; ret with res
