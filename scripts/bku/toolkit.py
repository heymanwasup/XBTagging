'''
Classes and functions designed for general purpose.
Only dependent on built-in python packages
'''

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
    if stop(A) and stop(B):
      return True
    if not isinstance(A,type(B))\
      or not (isinstance(A,list) or isinstance(A,dict)):
      return False
    
    isomorphism = True
    for itm in type(self).iters(A):
      a = type(self).getter(A,itm)
      b = type(self).getter(B,itm)
      isomorphism &= self.isIsomorphism(a,b,stop)
    return isomorphism
    
  def Map(self,stop,alg,*args):
    
    if len(args)>1:
      isIso = True
      for n in range(len(args)-1):
        isIso &= self.isIsomorphism(args[n],args[n+1],stop)
      if not isIso:
        raise ValueError('not all ISO')
    if stop(args[0]):
      result = alg(*args)
    else:
      result = type(args[0])()
      self.smartMap(stop,alg,result,*args)
    return result

  def Reduce(self,stop,bi_alg,args,start=None):
    if len(args)<2:
      raise ValueError('at least two args needed for Reduce')
    if start != None:
      wraper = lambda alg : lambda *atoms : reduce(alg,atoms,start)
    else:
      wraper = lambda alg : lambda *atoms : reduce(alg,atoms)
    alg = wraper(bi_alg)
    res = self.Map(stop,alg,*args)
    return res

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
    if isinstance(file_handle,str):
        file_handle = open(file_handle,'r')
          
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
    if res[0]:
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
  return res
  
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

def Decomposer(obj):
    return {attr:getattr(obj,attr) for attr in dir(obj) if not callable(getattr(obj,attr)) and not attr.startswith('__')}

def DumpClassToJson(obj,file_name):
  dict_of_cls = Decomposer(obj)
  with open(file_name,'w') as f:
    DumpToJson(dict_of_cls,f)

def MergeDict(A,B):
  Res = copy(A)
  Res.update(B)
  return Res

  
def main():
  res = PartialFormat('{key1:},{key2}',{'key3':10})
  print res
  
if __name__ == '__main__':
  main()