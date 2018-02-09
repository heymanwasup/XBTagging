import hashlib
import functools
import time
import pickle
import re
import sys
import json
import os
import commands
import numpy as np
from copy import deepcopy


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
    pass
    for n,val in enumerate(self.vals):
      assert((math.isnan(val) and (n!=0)),'NaN not permitted in non-1st bin: {0:}'.format(self.vals.__str__()))

  def Gurantee(self):
    pass
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

class CopyParameters(object):
  def __init__(self,types=[dict]):
    self.types = types

  def IsInTypes(self,obj):
    for t in self.types:
      if isinstance(obj,t):
        return True
    return False

  def __call__(self,fun):
    @functools.wraps(fun)
    def wrap(*args,**kw): 
      _args = ( deepcopy(arg) if self.IsInTypes(arg) else arg for arg in args)
      _kw   = {k:deepcopy(kw[k]) if self.IsInTypes(kw[k]) else kw[k] for k in kw}
      res = fun(*_args,**_kw)
      return res
    return wrap
      
#better, fexible 
class TimeCalculator(object):
  def __init__(self,isOpen=True):
      self.isOpen = isOpen
  def __call__(self,fun):
    @functools.wraps(fun)
    def wrap(*args,**kw):
      start = time.time()
      result = fun(*args,**kw)
      end = time.time()
      if self.isOpen:
        print '\n{0:18s} {1:8.1f}s used!'.format(fun.__name__,end-start)
      return result
    return wrap


def Decomposer(obj):
    return {attr:getattr(obj,attr) for attr in dir(obj) if not callable(getattr(obj,attr)) and not attr.startswith('__')}

def FooCopyClass(name,cls,new_attrs={}):
  attrs = vars(cls).copy()
  return type(name,(object,),attrs.update(new_attrs))

   
    
def TimeCalculator2(isOpen=True):
  def decorator(fun):
    @functools.wraps(fun)
    def wrap(*args,**kw):
      start = time.time()
      result = fun(*args,**kw)
      end = time.time()
      if isOpen:
        print '{0:.3f}s used!'.format(end-start)
      return result
    return wrap
  return decorator

#Fill a dictionay with multi-keys  
def Fill(data_dict,entry,*keys):
  if len(keys)>1:
    if keys[0] not in data_dict:
      data_dict[keys[0]] = {}
    Fill(data_dict[keys[0]],entry,*keys[1:])
  else:
    if keys[0] in data_dict:
      print 'Warning in tookit.Fill, a replacement occurred!! '
      print 'data\n\t',data_dict
      print 'entry\n\t',entry
      print 'keys\n\t',keys
    data_dict[keys[0]] = entry

    
def GetHash(fname,size=-1):
  hasher = hashlib.md5()
  with open(fname,'rb') as f:
    chunk = f.read(int(size))
    hasher.update(chunk)
  return hasher.hexdigest()[::2]

def GetHashFast(fname):
  return GetHash(fname,size=int(1e7))

def mkdir(path):
	if not os.path.isdir(path):
		res = commands.getstatusoutput('mkdir -p %s'%(path)) 
		if not res[0]:
			raise IOError(res[1])#'{0:}'.format(res[1]))

def DumpDictToJson(data,f=sys.stdout):
    json_str = json.dumps(data,indent=4,sort_keys=True)
    f.write(json_str)


def PartialFormat(fmt,keys): 
  reg_keys = '{([^{}:]+)[^{}]*}'
  reg_fmts = '{[^{}:]+[^{}]*}'
  pat_keys = re.compile(reg_keys)
  pat_fmts = re.compile(reg_fmts)
  
  allkeys = pat_keys.findall(fmt)
  allfmts = pat_fmts.findall(fmt)
  kf_map  = dict(zip(allkeys,allfmts))
  
  allkeys_set = set(allkeys)   
  keys_set     = set(keys.keys())
  
  invariant   = allkeys_set - keys_set

  keys_used = {key:keys[key] for key in keys}
  for k in invariant:
    keys_used[k] = kf_map[k]   
  res = fmt.format(**keys_used)
  print res
  
def InverseFormat(fmt,res):
  reg_keys = '{([^{}:]+)[^{}]*}'
  reg_fmts = '{[^{}:]+[^{}]*}'
  pat_keys = re.compile(reg_keys)
  pat_fmts = re.compile(reg_fmts)
  keys = pat_keys.findall(fmt)
  lmts = pat_fmts.split(fmt)
  temp = res
  values = []
  for lmt in lmts:
    if not len(lmt)==0:
      value,temp = temp.split(lmt,1)
      if len(value)>0:
        values.append(value)
  if len(temp)>0:
    values.append(temp)
  return dict(zip(keys,values))

def main():
  PartialFormat('{a:}af{f:}{c:}',{'a':1,'c':3})
  
if __name__ == '__main__':
  main()

  
