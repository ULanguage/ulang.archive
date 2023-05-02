;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
global _start

section .data
test: dq 0x5

section .text
_start:
main:
  sub rsp, 16
  mov qword [rsp], 8
  mov qword [rsp + 8], 11
  mov rax, 60
  mov rdi, [rsp]
  add rsp, 16
  syscall
