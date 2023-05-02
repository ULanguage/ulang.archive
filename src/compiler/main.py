if __name__ == '__main__':
  prog = (
    ('def', 'test', 5),
    ('func', 'main', 
      ('def', 'ing', 8),
      ('def', 'asd', 11),
      ('exit', ('var', 'asd')),
    ),
  )

  # Step 1, Checks
  # Step 2...

  res = ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\nglobal _start\n' # NOTE: Line only to make it easier to follow with 'tail -f'
  data = '\nsection .data\n'
  text = '\nsection .text\n'

  for expr in prog:
    if expr[0] == 'func':
      var = {}
      s = ''
      ex = '  ret'
      for subexpr in expr[2:]:
        if subexpr[0] == 'def':
          # TODO: addVar() that allocates an offset based on variable length
          offset = len(var) * 8 # TODO: Based on variable length
          var[subexpr[1]] = offset
          if offset == 0:
            s += f'  mov qword [rsp], {subexpr[2]}\n'
          else:
            s += f'  mov qword [rsp + {var[subexpr[1]]}], {subexpr[2]}\n'
        elif subexpr[0] == 'exit':
          s += '  mov rax, 60\n'
          ssubexpr = subexpr[1]
          if ssubexpr[0] == 'int':
            s += f'  mov rdi, {ssubexpr[1]}\n'
          elif ssubexpr[0] == 'var':
            if ssubexpr[1] in var:
              offset = var[ssubexpr[1]]
              if offset == 0:
                s += f'  mov rdi, [rsp]\n'
              else:
                s += f'  mov rdi, [rsp + {var[ssubexpr[1]]}]\n'
            else: # TODO: Look in parent scope
              s += f'  mov rdi, [{ssubexpr[1]}]\n'
          ex = '  syscall\n'

      if expr[1] == 'main':
        text += '_start:\n'
      text += expr[1] + ':\n'

      if len(var) != 0:
        text += f'  sub rsp, {len(var) * 8}\n' # TODO: Based on each variable's length

      text += s

      if len(var) != 0:
        text += f'  add rsp, {len(var) * 8}\n' # TODO: Based on each variable's length

      text += ex

    elif expr[0] == 'def':
      data += f'{expr[1]}: dq {hex(expr[2])}\n'

  print(res + data + text)
