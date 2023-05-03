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

.__ret:
; Remove the stack frame
  pop rbp
  ret

test:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 8 ; 1 stack vars

  ; ('def', 'glob', 'int64')

  ; ('set', ('var', 'glob'), ('int64', 5))
  mov qword [rsp + 0], 5

  ; ('return', ('var', 'glob'))
  mov qword r8, [rsp + 0]
  mov qword rax, r8
  jmp .__ret

.__ret:
; Remove the stack frame
  add rsp, 8
  pop rbp
  ret

_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 16 ; 2 stack vars

  ; ('def', 'ing', 'int64')

  ; ('set', ('var', 'ing'), ('int64', 1))
  mov qword [rsp + 0], 1

  ; ('set', ('var', 'ing'), ('call', 'test'))
  call test
  mov qword [rsp + 0], rax

  ; ('def', '__exitCode', 'int64')

  ; ('set', ('var', '__exitCode'), ('int64', 1))
  mov qword [rsp + 8], 1

  ; ('set', ('var', '__exitCode'), ('var', 'ing'))
  mov qword r8, [rsp + 0]
  mov qword [rsp + 8], r8

  ; ('call', 'exit', ('var', '__exitCode'))
  push qword [rsp + 8]
  call exit
  add rsp, 8

.__ret:
; Remove the stack frame
  add rsp, 16
  pop rbp
  ret

