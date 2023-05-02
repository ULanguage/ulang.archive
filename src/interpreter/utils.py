def getList(l, idx, default = None):
  return l[idx] if len(l) > idx else default

def findMainFile(prog):
  for file in prog.files:
    for fun in file.exprs:
      if fun.type == 'fun' and fun.name == 'main':
        return file
  return None

intrinsic = ['__string', '__int']
