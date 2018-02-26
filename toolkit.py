import hashlib
import math
import functools
import time
import re
import sys
import json
import os
import commands
import operator
import numpy as np
from copy import deepcopy,copy

class ALG(object):
  iters = staticmethod( \
      lambda dt : \
      range(len(dt)) if isinstance(dt,list) else dt.keys())

  setter = staticmethod( \
      lambda dt,itm,entry : \
      dt.append(entry) if isinstance(dt,list) else dt.update({itm:entry}))

  getter = staticmethod(lambda dt,itm:dt[itm])
  
  def smartMap(self,stop,alg,result,*args):
    for itm in type(self).iters(args[0]):
      entries = [ type(self).getter(arg,itm) for arg in args ]
      if stop(entries[0]):
        type(self).setter(result,itm,alg(*entries))
      else:
        to_entry = type(entries[0])()
        type(self).setter(result,itm,to_entry)
        self.smartMap(stop,alg,to_entry,*entries)

  def isIsomorphism(self,A,B,stop):
    if not isinstance(A,type(B))\
      or not (isinstance(A,list) or isinstance(A,dict)):
      return False
    isomorphism = True
    for itm in type(self).iters(A):
      a = type(self).getter(A,itm)
      b = type(self).getter(B,itm)
      if stop(a) and stop(b):
        continue
      elif stop(a) or stop(b):
        return False
      else:
        if not self.isIsomorphism(a,b,stop):
          return False
    return isomorphism
    
  def Map(self,stop,alg,*args):
    if len(args)>1:
      isIso = True
      for n in range(len(args)-1):
        isIso &= self.isIsomorphism(args[n],args[n+1],stop)
      if not isIso:
        raise ValueError('not all ISO')
    result = type(args[0])()
    self.smartMap(stop,alg,result,*args)
    return result

  def Reduce(self,stop,bi_alg,args):
    if len(args)<2:
      raise ValueError('at least two args needed for Reduce')
    wraper = lambda alg : lambda *atoms : reduce(alg,atoms)
    alg = wraper(bi_alg)
    res = self.Map(stop,alg,*args)
    return res

def MergeDict(A,B):
  Res = copy(A)
  Res.update(B)
  return Res

class PrintPriority(object):
  priorities = []
  def __init__(self,priority):
    priorities = type(self).priorities
    priorities.append(priority)
    type(self).priorities = sorted(set(priorities))
    self.priority = priority
  def __call__(self,fun):
    @functools.wraps(fun)
    def newFun(*args,**kw):
      fd = '/dev/fd/%s'%(self.GetFd())
      with open(fd,'w') as f:
        sys.stdout,saved = f,sys.stdout
        res = fun(*args,**kw)
        sys.stdout = saved
      return res
    return newFun
  def GetFd(self):
    for n,priority in enumerate(type(self).priorities):
      if priority == self.priority:
        return n


def json_load(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    return data

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

class CopyParameters(object):
  def __init__(self,types=[dict,list]):
    self.types = types

  def IsInTypes(self,obj):
    for t in self.types:
      if isinstance(obj,t):
        return True
    return False

  def __call__(self,fun):
    @functools.wraps(fun)
    def wrap(*args,**kw): 
      _args = tuple(deepcopy(arg) if self.IsInTypes(arg) else arg for arg in args)
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

def FooCopyClass(name,cls,inherits=(object,),new_attrs={}):
  attrs = vars(cls).copy()
  attrs.update(new_attrs)
  
  return type(name,inherits,attrs)

   
    
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
    print res
    if not res[0]:
      raise IOError(res[1])

def DumpToJson(data,f=sys.stdout):
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


  
def GetVarsList(rfile,Pnominal,Pvars):
  Rvars      = re.compile(Pvars)
  Rnominal  = re.compile(Pnominal)

  Vars = {}
  for key in rfile.GetListOfKeys():
    obj      = key.ReadObj()
    obj_name = obj.GetName()
    cls_name = obj.ClassName()

    if Rnominal.match(obj_name) \
      or (cls_name.find('TDirectory')==-1) \
      or (obj_name.find('SysLUMI')!=-1):
      continue

    var = Rvars.split(obj_name)[0]
    if var in Vars:
      Vars[var].append(obj_name)
    else:
      Vars[var] = [obj_name]
  for var in Vars: 
    if len(Vars[var])==1:
      Vars[var].append(Pnominal)
  return Vars

def main():
  PartialFormat('{a:}af{f:}{c:}',{'a':1,'c':3})
  
if __name__ == '__main__':
  main()
