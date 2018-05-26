import toolkit 

class MyClass(toolkit.IOHandler):
    def __init__(self):
        self.Warning('tesst','warning')
        self.Stdout('test','haha')
        self.FBIWarning('test','FBIwarning')

myobj = MyClass()
