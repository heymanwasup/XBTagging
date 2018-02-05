
import re
import importlib

import libs.cfg as Cfg
import imp,json
import hashlib
import toolkit
class A(object):
  @staticmethod
  def foo():
    print 'hello'

def main():
  A.foo()

def WriteVSPrint():
  a = {1:2}
  jstr = json.dumps(a,indent=4,sort_keys=True)
  with open('testP.json','w') as f:
    toolkit.DumpDictToJson(a,f)
  with open('testW.json','w') as f:
    f.write(jstr)
  p = toolkit.GetHashFast('testP.json')
  w = toolkit.GetHashFast('testW.json')
  h = hashlib.md5()
  h.update(jstr)
  o = h.hexdigest()[::2]
  print p
  print w
  print o
    



def TestHashstrHashfile():
  h1 = hashlib.md5()
  h2 = hashlib.md5()
  a = {1:2}
  with open('testhash.json','w') as f:
    toolkit.DumpDictToJson(a,f)
   
  h1.update(json.dumps(a,indent=4,sort_keys=True))
  with open('testhash.json','r') as f:
    h2.update(json.dumps(json.loads(f.read()),indent=4,sort_keys=True))

  print h1.hexdigest()
  print h2.hexdigest()

  
def TestJsonLoad():
  f = open('inspe5.log','r')
  parsed = json.loads(f.read())
  for k in parsed:
      print k
  print json.dumps(parsed, indent=4, sort_keys=True)

class CLS(object):
  def __init__(self):
    self.a = 10
    self.B()
  def B(self):
    self.b = 20

def TestInsp():
  example = CLS()
  members = [attr for attr in dir(example) if not callable(getattr(example, attr)) and not attr.startswith("__")]
  print members


def TestIMP():
  Cfg = imp.load_source('Cfg', './libs/cfg.py')
#Cfg = importlib.import_module('libs.cfg')
  print Cfg.a


if __name__ == '__main__':
 main()
