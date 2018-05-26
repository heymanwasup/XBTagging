class A(object):
    n = 1
    def __init__(self):
        print type(self).n
a = A()
A.n+=1
b = A()
print a.n
a.n = 100
print A.n
print a.n