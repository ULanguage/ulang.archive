import sys

logMask = [
  'error',
  'user',
  'debug'
]

def log(*args, level):
  if level in logMask:
    print(*args)

def error(*args, scope, expr):
  log('ERROR:', *args, scope, expr, level = 'error')
  sys.exit(1)
