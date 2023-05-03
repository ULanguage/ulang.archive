;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
global _start

section .data

  ; ('def', 'glob', 'int64', ('int64', 1))
glob: dq 1

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

getGlob:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; ('return', ('var', 'glob'))
  mov qword r8, [glob]
  mov qword rax, r8
  jmp .__ret

.__ret:
; Remove the stack frame
  pop rbp
  ret

setGlob:
  ; Set the stack frame
  push rbp
  mov rbp, rsp

  ; ('set', ('var', 'glob'), ('var', 'newGlob'))
  mov qword r8, [rbp + 16]
  mov qword [glob], r8

  ; ('return', ('var', 'glob'))
  mov qword r8, [glob]
  mov qword rax, r8
  jmp .__ret

.__ret:
; Remove the stack frame
  pop rbp
  ret

_start:
main:
  ; Set the stack frame
  push rbp
  mov rbp, rsp
  sub rsp, 8 ; 1 stack vars

  ; ('def', 'ing', 'int64')

  ; ('set', ('var', 'ing'), ('int64', 4))
  mov qword [rsp + 0], 4

  ; ('call', 'exit', ('call', 'setGlob', ('var', 'ing')))
  push qword [rsp + 0]
  call setGlob
  add rsp, 8
  push rax
  call exit
  add rsp, 8

  mov rax, 0 ; By default exit with value 0
.__ret:
; Remove the stack frame
  add rsp, 8
  pop rbp
; Exit
  mov rdi, 0
  syscall
