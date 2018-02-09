def Init(self):
  self.b = 'b' 
 
def Foo(self):
  print A_CLASS.a
  print self.b
 
A_CLASS = type('A_CLASS',(object,),{'a':'a','__init__':Init,'foo':Foo})

myObj = A_CLASS()
myObj.foo()
