from scope import Scope

def Execute(fileExpr):
  print('[Execute]', fileExpr)

  scope = Scope()
  ret = fileExpr.exec(scope, isMain = True)
  print(f'Exited with {ret}')
