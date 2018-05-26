import toolkit

class A(toolkit.IOHandler):
    def fun(self,n):
        if n > 0:
            n-=1
            self.fun(n)
        else:

            self.Stdout('got it !')
def main():
    a = A()
    a.fun(10)
main()
