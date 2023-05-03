global _start


section .data


section .text

  ; (fun, test, (1)...)
test:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; (return, (int64, 1))
  mov rax, 1
  jmp .__ret

.__ret:
  ; Remove the stack frame
  pop rbp
  ret

  ; (fun, main, (1)...)
_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; (return, (int64, 0))
  mov rax, 0
  jmp .__ret

  mov rax, 0 ; By default exit with value 0
.__ret:
  ; Remove the stack frame
  pop rbp
  ; Exit
  mov rdi, rax
  mov rax, 0
  syscall
