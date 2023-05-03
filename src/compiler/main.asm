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

  ; ('return', ('int64', 5))
  mov qword rax, 5
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
  sub rsp, 8 ; 1 stack vars

  ; ('call', 'test')
  call test
  
  ; ('def', '__exitCode', 'int64')

  ; ('set', ('var', '__exitCode'), ('int64', 3))
  mov qword [rsp + 0], 3

  ; ('call', 'exit', ('var', '__exitCode'))
  push qword [rsp + 0]
  call exit
  
  ; Remove the stack frame
.__ret:
  add rsp, 8
  pop rbp
  ret

