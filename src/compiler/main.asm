global _start
section .text
_start:
main:
  mov rax, 60
  mov rdi, 123
  syscall
