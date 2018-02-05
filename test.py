from copy import deepcopy
import re
import importlib

import libs.cfg as Cfg
import imp,json
import hashlib
import toolkit

class Template(object):
  a = 'a'
  def __init__(self):
    self.b = 'b'
  def foo(self):
    print Template.a
    print self.b
  def test(self):
    print a

def __init__(self):
  self.b = 'B'
  self.c = 'C'
  
class H(object):
  a = 1
  b = 2
  def __init__(self):
    print H.a
    print H.b

def main():
  MyCls = type('F',(H,),{})
  MyCls()

  MyCls2 = type('F',(H,),{})
  MyCls2.a = 100
  MyCls2()
  


def TestMetaCls_1():
  MyCls = type('MyCls',(Template,),{'__init__':__init__,'a':'A'})
  a = MyCls()
  a.foo()
  
  b = Template()
  b.foo()

  A = Template
  A.a = 10
  print Template.a
  
  c = Template()
  c.test()
  
def TestStaticMember():
  A.x = 10
  print A.x#10
  a = A()
  print a.x#10
  a.x = 100
  print A.x#10
  A.x=100
  print a.x#100
  b = A()
  print b.x#100
  

class A(object):


  @staticmethod
  def foo():
    print 'hello'
  

  def goo(self,data):
    data[10] = 20
    print data

  @toolkit.CopyParameters()
  def hoo(self,data):
    data[10] = 20
    print data

def _testCP(a,b,c):
  b[10] = 100
  print a
  print b
  print c

def testCP(fun):
  a = 10
  b = {}
  c = 'hello'
  fun(a,b,c)
  print a
  print b
  print c
  

def TestCopyParametes():
  testCP(_testCP)
  testCP(toolkit.CopyParameters()(_testCP))
  a = {}
  b = {}
  A().goo(a)
  A().hoo(b)
  print 
  print a
  print b

  

def TestStaticMethod():
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
