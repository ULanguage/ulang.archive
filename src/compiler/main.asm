global _start

section .data
test: dq 0x8
ing: dq 0x3

section .text
_start:
main:
  mov rax, 60
mov rdi, [ing]
syscall

