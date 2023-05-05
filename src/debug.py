import sys

debugMask = [
  # 'user',
  'error',
  'debug',
  'deepDebug',
]
logMask = [] # NOTE: Same options as debugMask
isDebugging = False

def log(*args, level):
  if level in debugMask:
    return debugStep(*args, level = level)
  elif level in logMask:
    print(*args)
  return False

def error(*args, scope = None, expr = None):
  resolved = log('ERROR:', *args, scope, expr, level = 'error')
  if not resolved:
    sys.exit(1)

def debugStep(*args, level):
  print('[DEBUG]')
  print(*args)
  cmd = input('> ')
  # TODO: use command
  match cmd:
    case 'exit':
      sys.exit(0)
    case 'continue':
      return True
    case _:
      pass
  return level != 'error'

def setDebug(to):
  global debugMask
  debugMask = to

def setLogMask(to):
  global logMask
  logMask = to
