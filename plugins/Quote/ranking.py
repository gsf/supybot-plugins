class Ranking(object):
  
  def __init__(self, *args):
    self.data = {}
      
  def sorted_data(self):
    result = sorted(self.data.iteritems())
    return sorted(result, key=lambda c:c[1], reverse=True)
    
  def increment(self, key):
    if self.data.has_key(key):
      self.data[key] += 1
    else:
      self.data[key] = 1
  
  def set(self, key, value):
    self.data[key] = value
    
  def items_at(self, value):
    return [c for c in self.sorted_data() if c[1] == value]

  def keys_at(self, value):
    return map(lambda c: c[0], self.items_at(value))
    
  def rank(self,key):
    value = self.data[key]

    sd = self.sorted_data()
    unique_values = sorted(set(map(lambda c: c[1], sd)), reverse=True)
    
    standard = len([c for c in sd if c[1] > value]) + 1
    dense = unique_values.index(value) + 1
    result = { 
      'nick' : key,
      'ordinal' : [sd.index(c) for c in sd if c[0] == key][0]+1, 
      'competition' : standard, 
      'dense' : dense, 
      'value' : value,
      'entries' : len(sd), 
      'ranks' : len(unique_values),
      'tied_with' : [k for k in self.keys_at(value) if k != key]
    }
    result['noun'] = 'citation'
    if result['value'] > 1:
      result['noun'] = 'citations'
    return result
