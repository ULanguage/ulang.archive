from expr import expr_t
import utils

class struct_t:
  def __init__(self, attrs):
    self._attrs = attrs
    self.attrs = dict()

  def get(self, attr):
    return self.attrs[attr]
  def set(self, attr, to):
    #TODO: Check it exists
    #TODO: Check types
    self.attrs[attr] = to
  
  def __repr__(self):
    return str(self)
  def __str__(self):
    attrs = ', '.join([str(attr) for attr in self.attrs])
    return f'struct<{attrs}>'
