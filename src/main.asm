global _start

section .data

  ; (def, globA, None)
globA: dq 0

  ; (def, globB, (int64, 1))
globB: dq 1

section .text

  ; (fun, getGlob, int64, (1)...)
getGlob:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; (return, (var, globA))
  mov rax, [globA]
  jmp .__ret

.__ret:
  ; Remove the stack frame
  pop rbp
  ret

  ; (fun, setGlob, int64, (1)...)
setGlob:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; (set, (var, globA), (int64, 2))
  mov qword [globA], 2

.__ret:
  ; Remove the stack frame
  pop rbp
  ret

  ; (fun, main, int64, (5)...)
_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 8 ; 1 stack vars

  ; (def, ing, (int64, 4))
  mov qword [rsp + 0], 4

  ; (set, (var, ing), (int32, 5))
  mov qword [rsp + 0], 5

  ; (call, setGlob)
  call setGlob

  ; (set, (var, ing), (call, getGlob))

  ; (call, getGlob)
  call getGlob
  mov qword [rsp + 0], rax

  ; (return, (var, ing))
  mov rax, [rsp + 0]
  jmp .__ret

  mov rax, 0 ; By default exit with value 0
.__ret:
  ; Remove the stack frame
  add rsp, 8
  pop rbp
  ; Exit
  mov rdi, rax
  mov rax, 60
  syscall
