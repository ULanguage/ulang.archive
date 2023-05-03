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

  ; ('exit', ('int', 2))
  mov rax, 60
  mov rdi, 2
  syscall

  ; Remove the stack frame
  pop rbp
  ret

_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 8 ; 1 stack vars

  ; ('def', 'exitCode', ('int', 5))
  mov qword [rsp + 0], 5

  ; ('set', ('var', 'exitCode'), ('int', 6))
  mov qword [rsp + 0], 6

  ; ('call', 'exit', ('var', 'exitCode'))
  push qword [rsp + 0]
  call exit
  
  ; ('exit', ('int', 1))
  mov rax, 60
  mov rdi, 1
  syscall

  ; Remove the stack frame
  add rsp, 8
  pop rbp
  ret

