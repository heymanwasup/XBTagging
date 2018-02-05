import hashlib
import functools
import time
import pickle
import re
import sys
import json
import os
import commands

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
        print '{0:.3f}s used!'.format(end-start)
      return result
    return wrap


def Decomposer(obj):
    return {attr:getattr(obj,attr) for attr in dir(obj) if not callable(getattr(obj,attr)) and not attr.startswith('__')}
    
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

@TimeCalculator()  
def hash_md5(filename,fun):
  hashmd5 = hashlib.md5()
  with open(filename,'rb') as f:
    hashvalue = fun(f,hashmd5)
  return hashvalue

def get_md5_1(data,hasher,buff):
  for chunk in iter(lambda :data.read(buff),b''):
    hasher.update(chunk)
  return hasher.hexdigest()

def get_md5_2(data,hasher,buff):
  chunk = data.read(buff)
  while len(chunk)!=0:
    hasher.update(chunk)
    chunk = data.read(buff)
  return hasher.hexdigest()

def get_md5_3(data,hasher):
  hasher.update(data.read())
  return hasher.hexdigest()

def get_md5_4(data,hasher,buff):
  hasher.update(data.read(buff))
  return hasher.hexdigest()

def test_hashmd5():
#  fname = 'Goodfellas.1990.720p.BrRip.264.YIFY.mp4'   
  fname = 'WWW.YIFY-TORRENTS.COM.jpg'  
  f = lambda g,x:functools.partial(g,buff=x)

  '''
  d11 = hash_md5(fname,f(get_md5_1,10000)) 
  d12 = hash_md5(fname,f(get_md5_1,1000)) 

  d21 = hash_md5(fname,f(get_md5_2,10000)) 
  d22 = hash_md5(fname,f(get_md5_2,1000)) 

  print d11
  print d12
  print d21
  print d22
  '''

  d = []

  d3 = hash_md5(fname,get_md5_3) 
  d.append(d3)

  buff = -1
  da = hash_md5(fname,f(get_md5_4,buff))
  d.append(da)

  buff = int(1e7)
  for n in range(0,3):
    da = hash_md5(fname,f(get_md5_4,buff))
    buff*=10
    d.append(da)

  for a in d:
    print a

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
#print keys_used 
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
