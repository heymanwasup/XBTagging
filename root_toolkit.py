'''
Functions and classes designed for some dedicated usages
'''
import operator,math,re


import ROOT as R

class TemplateHist(object):
  __doc__ = '__MetaHistogram__'

  nbins = None
  default_val = 0
  default_err = 0
  do_gurantee = False  
  do_assert = False
  do_warnings = False
  always_report = False
  altHist = None
  
  def __init__(self,th1=None,vals=None,errs=None):
    self.SetDefault()
    if th1!=None:
      self.vals = [ th1.GetBinContent(n+1) for n in range(self.nbins) ]
      self.errs = [ th1.GetBinError(n+1)   for n in range(self.nbins) ]
    elif vals!=None:
      self.vals = list(vals)
      if errs!=None:
        self.errs = list(errs)
    if type(self).always_report:
      good,verbose = self.Report()
      if not good:
        print 'Error in init hist',verbose
    
  def __iter__(self):
    self.current = 0
    return self

  def next(self):
    if self.current==type(self).nbins:
      raise StopIteration
    else:
      self.current += 1
      return (self.vals[current-1],self.errs[current-1])

  def IsSame(self,other):
    if self.__doc__ == other.__doc__:
      res = True
    else:
      res = False
    return res

  def AltHist(self):
    if not self.IsSame(type(self).altHist):
      return type(self)
    else:
      return type(self).altHist
  
  def Report(self):   
    warnings = True,''
    if type(self).do_warnings:
      warnings = self.Warnings()
    if type(self).do_gurantee:
      self.Gurantee()
    if type(self).do_assert:
      self.Assert()
    return warnings

  def SetDefault(self):
    self.vals   = [type(self).default_val for n in range(type(self).nbins)]
    self.errs   = [type(self).default_err for n in range(type(self).nbins)]

  def IsEmpty(self):
    isEmpty = True
    isNan   = True
    for n in range(1,type(self).nbins):
      isEmpty &= (self.vals[n]==type(self).default_val) or (math.isnan(self.vals[n]))
      isNan &= math.isnan(self.vals[n])
    verbose = ''  
    if isEmpty:
      verbose += 'Empty Histogram!'
      if isNan:
        verbose += ' with Nan {0:}'.format(self.vals.__str__())
    return isEmpty,verbose

  def Assert(self):
    pass

  def Gurantee(self):
    pass

  def Warnings(self):
    return True,''

  def Add(self,other):
    if not self.IsSame(other):
      _other = type(self)(th1=other)
    else:
      _other = other
    self.vals = list(map(operator.add,self.vals,_other.vals))
    self.errs = list(map(lambda x,y:math.sqrt(x**2+y**2),self.errs,_other.errs))

  def Scale(self,sf=1.):
    self.vals = list(map(lambda x:x*sf,self.vals))
  def Operation(self,other,operator_val):
    _other_vals = other.vals if self.IsSame(other) else other
    return self.AltHist()(vals=map(operator_val,self.vals,_other_vals))
  
 
  def __str__(self):
    return zip(self.vals,self.errs).__str__()
  def __repr__(self):
    return self.__str__()
  
  def __add__(self,other):
    return self.Operation(other,operator.add)
  def __sub__(self,other):
    return self.Operation(other,operator.sub)
  def __mul__(self,other):
    return self.Operation(other,operator.mul)
  def __div__(self,other):
    try:
      iter(other)
    except TypeError:
      other = [other]*type(self).nbins
    return self.Operation(other,lambda x,y:x/y if y!=0 else float('nan'))
  def __pow__(self,n):
    return type(self)(vals=map(lambda x:x**n,self.vals))
  def sqrt(self):
    return type(self)(vals=map(math.sqrt,self.vals))
  def abs(self):
    return type(self)(vals=map(lambda x:abs(x),self.vals))


def GetVarsList(rfile,Pnominal,Pvars):
  Rvars      = re.compile(Pvars)
  Rnominal  = re.compile(Pnominal)

  Vars = {}
  for key in rfile.GetListOfKeys():
    isDir = key.IsFolder()
    name = key.GetName()

    if not Rvars.match(name) \
      or (name.find('SysLUMI')!=-1) \
      or (not isDir):
      continue

    var = Rvars.findall(name)[0][0]
    if var in Vars:
      Vars[var].append(name)
    else:
      Vars[var] = [name]
  for var in Vars: 
    if len(Vars[var])==1:
      Vars[var].append(Pnominal)
  return Vars

def GetHistFromNames(tfile,names,is_debug=False):
  sumHist = None
  for name in names:
    hist = tfile.Get(name) 
    if hist == None:
      continue
    if sumHist == None:
      sumHist = hist.Clone()
    else:
      sumHist.Add(hist)
    if is_debug:
      print 'tot {0:4.2e} \n \t add {1:} \n \t\t {2:3.2e}'.format(sumHist.Integral(),name,hist.Integral())
  return sumHist

def main():
  f = R.TFile('../input/test.root')
  varsList = GetVarsList(f,'SysNominal',r'(.*[^_])(_+[0-9]*)(up|down)')
  print varsList

if __name__ == '__main__':
  main()
