import toolkit

class A(toolkit.IOHandler):
    def Redirect(self):
        self.BindOutput('Warning', 'Warning 0', '/dev/fd/0')
        self.BindOutput('Stdout', 'Stdout 1', '/dev/fd/1')
        self.BindOutput('FBIWarning', 'FBIWarning 2', '/dev/fd/2')
    def G(self):
        self.H()
    def H(self):
        self.Redirect()

    def fun(self,n):
        if n > 0:
            n-=1
            self.fun(n)
        else:

            self.Stdout('got it !')
def main():
    a = A()
    #a.G()
    a.fun(10)
main()
