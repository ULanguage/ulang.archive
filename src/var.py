from expr import expr_t
import utils

class var_t:
  def __init__(self, value, t):
    self.value = value
    self.type = t
  
  def __repr__(self):
    return f'var<{self.value}, {self.type}>'

  def __str__(self):
    t = self.type
    if t in utils.intrinsic: return f'{self.value}'
    else: return repr(self)
