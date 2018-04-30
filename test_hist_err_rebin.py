import ROOT as R
from array import array
def Fun():
  h1 = R.TH1F('h1','h1',2,0,2)
  h1.SetBinContent(1,30)
  h1.SetBinContent(2,40)
  h1.SetBinError(1,3)
  h1.SetBinError(2,4)

  h2 = h1.Rebin(1,'',array('d',[0,2]))
  print h1
  h2.Copy(h1)
  print h1
  print h1.GetBinContent(1)
  print h1.GetBinError(1)


Fun()
