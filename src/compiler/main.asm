;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
global _start

section .data

section .text
exit:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; ('exit', ('var', 'exitCode'))
  mov rax, 60
  mov rdi, [rbp + 16]
  syscall

  ; Remove the stack frame
.__ret:
  pop rbp
  ret

test:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; ('return', ('int64', 7))
  mov qword rax, 7
  jmp .__ret

  ; Remove the stack frame
.__ret:
  pop rbp
  ret

_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 16 ; 2 stack vars

  ; ('def', 'ing', 'int64')

  ; ('set', ('var', 'ing'), ('int64', 3))
  mov qword [rsp + 0], 3

  ; ('set', ('var', 'ing'), ('call', 'test'))
  call test
  mov qword [rsp + 0], rax

  ; ('call', 'exit', ('var', 'ing'))
  push qword [rsp + 0]
  call exit
  add rsp, 8

  ; ('def', '__exitCode', 'int64')

  ; ('set', ('var', '__exitCode'), ('int64', 3))
  mov qword [rsp + 8], 3

  ; ('call', 'exit', ('var', '__exitCode'))
  push qword [rsp + 8]
  call exit
  add rsp, 8

  ; Remove the stack frame
.__ret:
  add rsp, 16
  pop rbp
  ret

