from copy import deepcopy
import re
import importlib

import libs.cfg as Cfg
import imp,json
import hashlib
import toolkit,os,sys
import functools
import numpy as np

def main():
  print sys.argv

  with os.fdopen(3,'w') as f:
    print >>f,f.fileno()
    print >>f,'hello'
    
outfiles = {} 
for _ in range(3): 
    fd = os.dup(1)
    outfiles[fd] = os.fdopen(fd, 'w')

def PrintToFD():
  for no in outfiles.keys(): 
    print >>outfiles[no], "foo"
    print >>outfiles[no], outfiles[no].fileno()


def fd1():
  with open('/dev/fd/1', 'w') as fd1, open('/dev/fd/2', 'w') as fd2, open('/dev/fd/3', 'w') as fd3:
    print >>fd1,'100'
    print >>fd2,'200'
    print >>fd3,'300'


class A(object):
  def __init__(self):
    self.words = 'Hello'
    self.a = 'Bye'

  def InnerDecorator(self,words):
    def wraper(fun):
      @functools.wraps(fun)
      def foo(*args,**kw):
        print self.words
        print words
        fun(*args,**kw)
      return foo
    return wraper

#@self.TestWraper('world')
  def foo(self):
    print self.a

def InnerWrapper():
  a = A()
  a.foo()



def TestCopyFoo():

  class A(object):
    a = 1
    def __init__(self):
      self.b = 10
    def foo(self):
      print type(self).a
      print self.b

  A_dummy = type('A_dummy',(object,),{})
#  A_attrs = {attr:getattr(A,attr) for attr in vars(A).copy()}
  attrs = vars(A)#.copy()
  print attrs.copy()
  print attrs


  test = True
  if test:
    B = type('B',(object,),dict(attrs))
    B.a = 2

    b = B()
    b.foo()
    
    a = A()
    a.foo()

'''
  B = type('B',(object,),A_attrs)
  b = B()
  b.foo()
'''
  
def TestCopyClass_1():
  class A(object):
    a = 1
    def __init__(self):
      self.b = 10
    def foo(self):
      print type(self).a
      print self.b

  A_dummy = type('A_dummy',(object,),{})
  A_attrs = {attr:getattr(A,attr)  for attr in dir(A) if (not attr in dir(A_dummy))}

  B = type('B',(object,),A_attrs)
  B.a = 2
  
  a = A()
  a.foo()

  b = B()
  b.foo()
  
  

class CLS(object):
  a = 1.
  def __init__(self):
    self.b = 2
  def foo(self):
    print type(self).a
    print self.b

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

def TestMetaCls():
  def Init(self):
    self.b = 'b'

  def Foo(self):
    print type(self).a
    print self.b

  MyCls = type('MyCls',(object,),{'a':'a','__init__':Init,'foo':Foo})
  myObj = MyCls()
  myObj.foo()

def TestMeta2():
  MyCls = type('F',(object,),{'a':1,'b':2})

  MyCls()

  MyCls2 = type('F',(H,),{})
  MyCls2.a = 100
  MyCls2()

  data = dir(Template)
  for d in data:
    print d
    print type(d).__name__

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
    toolkit.DumpToJson(a,f)
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
    toolkit.DumpToJson(a,f)
   
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
