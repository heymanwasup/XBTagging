def fun(a):
    def f():
        print b
    b = a
    return f

f1 = fun(1)
f2 = fun(2)
f1()
f2()
