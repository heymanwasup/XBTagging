import toolkit

class TemplateHist(object):
  nbins = None
  default_var = 0
  default_err = 0
  gurantee = False  
  do_assert = False

  def __init__(self,th1=None,vals=None,errs=None):
    self.SetDefault()
    if th1!=None:
      self.vals = [ th1.GetBinContent(n+1)) for n in range(self.nbins) ]
      self.errs = [ th1.GetBinError(n+1))   for n in range(self.nbins) ]
    elif vals!=None:
      self.vals = list(vals)
      if errs!=None:
        self.errs = list(errs)
    if type(self).gurantee:
      self.Gurantee()
    if do_assert:
      self.Assert()

  def SetDefault(self):
    self.vals   = [type(self).default_val for n in range(type(self).nbins]
    self.errs   = [type(self).default_err for n in range(type(self).nbins)]

  def Assert(self):
    for n,val in enumerate(self.vals):
      assert((math.isnan(val) and (n!=0)),'NaN not permitted in non-1st bin: {0:}'.format(self.vals.__str__()))

  def Gurantee(self):
    self.vals[0],self.errs[0] = 0,0
    self.vals = list(map(lambda x:x if x>0 else 0, self.vals))

  def Add(self,other):
    if not isinstance(other,type(self)):
      _other = type(self)(th1=other)
    else:
      _other = other
    self.vals = list(map(operator.add,self.vals,_other.vals))
    self.errs = list(map(lambda x,y:math.sqrt(x**2+y**2)),self.errs,_other.errs)

  def Operation(self,other,operator_val):
    _other_vals = other.vals if isinstance(other,type(self)) else other
    return type(self)(vals=map(operator_val,self.vals,_other_vals))
  
  def __add__(self,other):
    return self.Operation(other,operator.add)
  def __sub__(self,other):
    return self.Operation(other,operator.sub)
  def __mul__(self,other):
    return self.Operation(other,operator.mul)
  def __div__(self,other):
    return self.Operation(other,lambda x,y:x/y if y!=0 else float('nan'))
  def __pow__(self,n):
    return type(self)(val=map(lambda x:x**n,self.vals))
  def sqrt(self):
    return type(self)(val=map(lambda x:math.sqrt,self.vals))

  
