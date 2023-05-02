;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
global _start

section .data

section .text
exit:
  mov rax, 60
  mov rdi, 2
  syscall

_start:
main:
  sub rsp, 8
  mov qword [rsp], 8
  call exit
  mov rax, 60
  mov rdi, 1
  add rsp, 8
  syscall

