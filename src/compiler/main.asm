;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
global _start

section .data

section .text
exit:
  push rbp
  mov rbp, rsp
  mov rax, 60
  mov rdi, [rbp + 16]
  syscall
  mov rax, 60
  mov rdi, 2
  syscall
  pop rbp
  ret

_start:
main:
  push rbp
  mov rbp, rsp
  sub rsp, 16
  mov qword [rsp], 5
  mov qword [rsp + 8], 6
  push 4
  call exit
  mov rax, 60
  mov rdi, 1
  syscall
  add rsp, 16
  pop rbp
  ret

