import ROOT as R
import math
canvas = R.TCanvas()
h1 = R.TH1F('h1','h1',10,0,10)
h2 = R.TH1F('h2','h2',10,0,10)
for n in range(10):
    h1.SetBinContent(n+1,math.sin(n))
    h2.SetBinContent(n+1,math.sin(n))

    if n < 5 :
        h1_err = 0.01
        h2_err = 0.001
    else:
        h1_err = 0.1
        h2_err = 0.001
    h1.SetBinError(n,h1_err)
    h2.SetBinError(n,h2_err)
f1 = R.TF1('foo1','[0]+[1]*x+[2]*x*x+[3]*x*x*x')
f2 = R.TF1('foo2','[0]+[1]*x+[2]*x*x+[3]*x*x*x')

#h1.Fit(f1)
#canvas.Print('f1.png')
#canvas.Update()
h2.Fit(f2)
f = h2.GetFunction('foo2')
print f(10)
canvas.Print('f2.png')