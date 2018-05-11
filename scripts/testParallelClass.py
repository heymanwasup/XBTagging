import multiprocessing
def SubRun(self,args):
    self.args = args
    self.Work()

class A(object):
    def __init__(self):
        self.args_list = range(100)

    def Run(self):
        for args in self.args_list:
            self.args = args
            self.Work()
    def Work(self):
        print self.args
    def RunParallel(self):
        p = multiprocessing.Pool(8)

        for args in self.args_list:
            p.apply_async(SubRun, args=(self,args,))
        p.close()
        p.join()
        print 'done'

    def SubRun(self,args):
        self.args = args
        print 'a'
        self.Work()


a = A()
a.RunParallel()