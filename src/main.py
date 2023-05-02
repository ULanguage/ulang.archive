from expr import expr_t

if __name__ == '__main__':
  prog = expr_t(('prog', 'test', (
    ('file', 'main.u', (
      ('fun', 'main', (
        ('print', 1)
      ))
    ))
  )))

  print(prog)
