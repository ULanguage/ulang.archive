if __name__ == '__main__':
  prog = (
    ('def', 'test', 5),
    ('func', 'main', 
      ('exit', 4),
    ),
  )

  # Step 1, Checks
  # Step 2...

  res = 'global _start\n'
  data = '\nsection .data\n'
  text = '\nsection .text\n'

  for expr in prog:
    if expr[0] == 'func':
      s = ''
      if expr[1] == 'main':
        s += '_start:\n'
      s += expr[1] + ':\n'
      for subexpr in expr[2:]:
        if subexpr[0] == 'exit':
          s += f'  mov rax, 60\n  mov rdi, {subexpr[1]}\n  syscall\n'

      text += s
    elif expr[0] == 'def':
      data += f'{expr[1]}: dq {hex(expr[2])}\n'

  print(res + data + text)
