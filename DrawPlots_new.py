
from AtlasStyle import *
import ROOT as R
import toolkit
import tools
import math
from toolkit import ALG
from array import array
import copy

R.gROOT.SetBatch(True)
#retrieve histograms from root file
#data, mc, errband 

class RetrieveHists(object):
  def __init__(self,tfile,dataHistName,mcHistsName,systsName={},xbins=None):
    self.tfile = tfile
    self.dataHistName = dataHistName 
    self.mcHistsName = mcHistsName
    self.systsName = systsName
    self.xbins = xbins

  def PrintHist(self,hist):
    N = hist.GetNbinsX()
    for n in range(1,N+1):
      c = hist.GetBinContent(n)
      e = hist.GetBinError(n)
      print '{0:10}   {1:5.2f} +-  {2:3.5f}'.format(n,c,e)

  def PrepareHists(self): 
    #get data histogram
    dataHist = self.GetHist(self.dataHistName)

    #get mc histograms and sum of mc histograms
    mcHists = {} 
    mcSum = None
    for name,hists in self.mcHistsName.iteritems():
      hist = self.GetHist(hists)
      if hist == None:
        print '{0:} not exists!'.format(name)
        continue 
      if mcSum == None:
        mcSum = hist.Clone() 
      else: 
        mcSum.Add(hist)
      mcHists[name] = hist

    #get systHists
    systHists = {}
    for name,systs in self.systsName.iteritems():
      try: 
        do = self.GetHist(systs[0])
        up = self.GetHist(systs[1])
      except RuntimeError:
        continue
      systHists[name] = [do,up]

    #get error band
    errbandHist = self.GetErrorBand(mcSum,systHists)    

    return  dataHist,mcHists,errbandHist



  def GetErrorBand(self,mcSum,systHists):
    
    errors = {}

    mcNominal,mcNominal_stat = self.GetHistContent(mcSum)
    
    errors['mcstat'] = mcNominal_stat
   
    Nbins = mcSum.GetNbinsX()
    for name,systs in systHists.iteritems():
      systDown,systDown_stat = self.GetHistContent(systs[0])
      systUp,systUp_stat = self.GetHistContent(systs[1])
      errors[name] = []
      for n in range(Nbins):
        errors[name].append(abs(systUp[n]-systDown[n])/2.)

    errband_tot = [0. for _ in range(Nbins)] 
    for name,syst in errors.iteritems():
      for n in range(Nbins):
        errband_tot[n] = math.sqrt((errband_tot[n]**2 + syst[n]**2))
    
    h_errband = mcSum.Clone()
    h_errband.Reset()
    
    self.FillHistContent(h_errband,mcNominal,errband_tot)

    return h_errband

  def GetErrorBand_new(self,systHists):
    Nbins = mcSum.GetNbinsX()
    errorband = []
    

  @staticmethod
  def GetHistContent(hist):
    Nbins = hist.GetNbinsX()
    bincontents = []
    binerrors = []    
    for n in range(1,Nbins+1):
      content = hist.GetBinContent(n)
      error = hist.GetBinError(n)
      bincontents.append(content)
      binerrors.append(error)
    return bincontents,binerrors 

  @staticmethod
  def FillHistContent(hist,val,err=None):
    if err==None: 
      err = [0.]*len(val)
    Nbins = hist.GetNbinsX()
    if not ((len(val)==len(err)) and (len(val)==Nbins)):
      print 'len of val = {0:}, len of err = {1:}, len of hist = {2}:'.format(len(val),len(err),Nbins)
      raise ValueError('not ((len(val)==len(err)) and (len(val)==Nbins))')
    for n in range(Nbins):
      hist.SetBinContent(n+1,val[n])
      hist.SetBinError(n+1,err[n])
    return hist

  def GetHist(self,names):
    hist = tools.GetHistFromNames(self.tfile,names)
    if not hist :
      raise RuntimeError('hist is empt')
    return hist

class DrawControlPlots(object):
  def __init__(self,opts,txts={}):
    self.Opts = copy.deepcopy(opts)
    self.Texts = copy.deepcopy(txts)
  
  def Print(self,dataHist,mcHists,errBand):
    #Prepare the objects going to be drawn on canvas
    self.Prepare(dataHist, mcHists, errBand)

    #Print the canvas to imagine files
    self.DrawPlots()

  def Prepare(self,dataHist,mcHists,errBand):

    #rebining
    #reunit
    #get&set maximum/minimum value 
    #get&set range 
    #get ratio histogram
    #get ratio error band histogram
    #set marker color/marker offset/title size/label size/...
    ratio,ratioErrorBand = self.ProcessHists(dataHist,mcHists,errBand)
    
    #get thstack
    hs = self.GetTHStack(mcHists,self.Opts['mcHStack_new'])
    
    #get canvas
    canvas = self.GetCanvas()

    #get up/down tpad
    pad_up = self.GetPad('upPad')
    pad_do = self.GetPad('downPad')

    #get up/down legend
    leg_up = self.GetUpLegend(dataHist,mcHists)
    leg_do = self.GetDownLegend(ratio,ratioErrorBand)

    #prepare other objects
   
    #objects going to be draw
    self.P = { 
      'canvas':canvas,
      'pad_up':pad_up,
      'pad_do':pad_do,
      'dataHist':dataHist,
      'hs':hs,
      'ratio':ratio,
      'leg_up':leg_up,
      'leg_do':leg_do,
      'errBand':ratioErrorBand,
    }
   
  def DrawText(self,text,x,y,color=1,tsize=-1):
    l = R.TLatex()
    if tsize>0:
      l.SetTextSize(tsize)
    l.SetNDC()
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

  #Drawing the objects and print plots
  def DrawPlots(self):
    P = self.P
    P['canvas'].Draw()

    P['pad_up'].Draw()
    P['pad_do'].Draw()

    P['pad_up'].cd()



    P['hs'].Draw('HIST')
    self.DecorateObjectNew(P['hs'],self.Opts['mcHStack_new'])
    P['dataHist'].Draw('esame')

    print 'P 0'
    print P['dataHist']
    self.PrintHist(P['dataHist'])
    P['leg_up'].SetTextFont(62)
    P['leg_up'].Draw('same')

    for name,txts in self.Texts.iteritems():
      self.DrawText(*txts)



    P['pad_do'].cd()
    P['leg_do'].SetTextFont(62)

    P['ratio'].GetYaxis().SetRangeUser(0.5,1.5)
    P['ratio'].Draw('same')

    P['errBand'].Draw('E2same')
    P['leg_do'].Draw('same')

    for fmt in self.Opts['fmt']:
      P['canvas'].Print('{0:}.{1:}'.format(self.Opts['name'],fmt))


  @staticmethod
  def GetHistContent(hist):
    Nbins = hist.GetNbinsX()
    bincontents = []
    binerrors = []    
    for n in range(1,Nbins+1):
      content = hist.GetBinContent(n)
      error = hist.GetBinError(n)
      bincontents.append(content)
      binerrors.append(error)
    return bincontents,binerrors 

  def PrintHist(self,hist):
    N = hist.GetNbinsX()
    for n in range(1,N+1):
      c = hist.GetBinContent(n)
      e = hist.GetBinError(n)
      w = hist.GetBinWidth(n)
      l = hist.GetBinLowEdge(n)

      print '{0:10} {3:.0f}_{4:.0f}   {1:5.2f} +-  {2:3.5f}'.format(n,c,e,l,l+w)

  def GetPad(self,name):
    opts = self.Opts[name]
    pad = self.ConstructRootObject(R.TPad,opts)
    return pad
    
  def ConstructRootObject(self,Cls,opts):
    constructor = opts['constructor']
    settings = None if not 'settings' in opts else opts['settings']
    if isinstance(constructor,dict):
      obj = Cls(**constructor)
    else:
      obj = Cls(*constructor)
    if not settings == None:
      self.DecorateObjectNew(obj,settings)
    return obj

  def GetUpLegend(self,dataHist,mcHists):
    leg = self.ConstructRootObject(R.TLegend,self.Opts['upLeg'])
    leg.AddEntry(dataHist,'Data','p')
    for name,hist,_ in mcHists[-1::-1]:
      leg.AddEntry(hist,name,'f')
    return leg
  
  def GetDownLegend(self,ratio,errBand):
    leg = self.ConstructRootObject(R.TLegend,self.Opts['downLeg'])
    nameB = self.Opts['errBandName']
    leg.AddEntry(errBand,nameB,'f')
    return leg

  def Buger1(self,dataHist,name):
    self.Opts['xRange'] = self.GetXRange(dataHist)
    print 'xRange {0:}'.format(name)
    print self.Opts['xRange']

  def ProcessHists(self,dataHist,mcHists,errBand):

    self.ReBinning(dataHist,mcHists,errBand)

    self.ReUnit(dataHist,mcHists,errBand)

    sumHist = self.GetMCSum(mcHists)
    ratio = self.GetRatioHist(dataHist,sumHist)
    ratioErrorBand = self.GetRatioErrorBand(errBand)

    if self.Opts['xRange'] == None:
      self.Opts['xRange'] = self.GetXRange(dataHist)

    isLogy = self.Opts['isLogy']
    if self.Opts['yRange'] == None:
      self.Opts['yRange'] = self.GetYRange(dataHist,sumHist,isLogy)


    self.SetXRange(self.Opts['xRange'], dataHist, mcHists, ratio, ratioErrorBand)
    self.SetYRange(self.Opts['yRange'], dataHist)


    optsBnew = self.Opts['errBandnew']
    optsRnew = self.Opts['ratioHist_new']
    optsDnew = self.Opts['dataHist_new']
    self.DecorateObjectNew(ratio,optsRnew)
    self.DecorateObjectNew(ratioErrorBand,optsBnew)
    self.DecorateObjectNew(dataHist,optsDnew)

    return ratio,ratioErrorBand

  def GetRatioErrorBand(self,errBand):
    NbinsX = errBand.GetNbinsX()
    errb_vals,errb_errs = self.GetHistContent(errBand)

    ratio_errb_vals = [1.]*NbinsX
    ratio_errb_errs = []
    for n in range(NbinsX):
      if errb_vals[n]==0.:
        ratio_errb_errs.append(0.)
      else:
        ratio_errb_errs.append(errb_errs[n]/errb_vals[n])
    h_ratio_errb = errBand.Clone()
    h_ratio_errb.Reset()
    self.FillHistContent(h_ratio_errb,ratio_errb_vals,ratio_errb_errs)
    return h_ratio_errb

  @staticmethod
  def FillHistContent(hist,val,err=None):
    if err==None: 
      err = [0.]*len(val)
    Nbins = hist.GetNbinsX()
    if not ((len(val)==len(err)) and (len(val)==Nbins)):
      print 'len of val = {0:}, len of err = {1:}, len of hist = {2}:'.format(len(val),len(err),Nbins)
      raise ValueError('not ((len(val)==len(err)) and (len(val)==Nbins))')
    for n in range(Nbins):
      hist.SetBinContent(n+1,val[n])
      hist.SetBinError(n+1,err[n])
    return hist

  def ReUnit(self,dataHist,mcHists,errBand):
    if self.Opts['funit'] == None:
      return 
    hists = [dataHist, errBand] + [hist[1] for hist in mcHists]
    funit = self.Opts['funit']
    NbinsX = hists[0].GetNbinsX() 
    print 'In R 0'
    print dataHist
    self.PrintHist(dataHist)
    for hist in hists:
      for n in range(NbinsX):
        c = hist.GetBinContent(n+1)
        e = hist.GetBinError(n+1)
        w = hist.GetBinWidth(n+1)
        c_new = c/(w/funit) 
        e_new = e/(w/funit) 
        hist.SetBinContent(n+1,c_new)
        hist.SetBinError(n+1,e_new)
    print 'In R 1'
    print dataHist
    self.PrintHist(dataHist)
  def ReBinning(self,dataHist,mcHists,errBand):
    if self.Opts['xBins'] == None:
      return dataHist,mcHists,errBand

    xBins = array('d',self.Opts['xBins'])
    print 'I 0'
    print dataHist
    self.PrintHist(dataHist)
    dataHist.Rebin(len(xBins)-1,'',xBins).Copy(dataHist)
    print 'I 1'
    print dataHist
    for hist in mcHists:
      hist[1] = hist[1].Rebin(len(xBins)-1,'',xBins)
    errBand = errBand.Rebin(len(xBins)-1,'',xBins)
    return dataHist,mcHists,errBand

  def GetMCSum(self,mcHists):
    #mc sum hist
    mc_hists = [hist[1] for hist in mcHists]
    sumHist = mc_hists[0].Clone()
    sumHist.Reset()
    for hist in mc_hists:
      sumHist.Add(hist)
    return sumHist

  def GetYRange(self,dataHist,sumHist,isLogy):
    ymax = max(sumHist.GetMaximum(),dataHist.GetMaximum())
    if isLogy:
      yRange = [1.,ymax**1.5]
    else:
      yRange = [0.,ymax*1.5]
    return yRange

  def GetXRange(self,dataHist):
    nBins = dataHist.GetNbinsX()
    xMin = dataHist.GetBinLowEdge(1) 
    xMax = dataHist.GetBinLowEdge(nBins) + dataHist.GetBinWidth(nBins)
    xRange = [xMin,xMax]
    return xRange

  def SetXRange(self,xRange, dataHist, mcHists, ratio, ratioErrorBand):

    #hists = [ dataHist,] + [hist[1] for hist in mcHists]
    hists = [ dataHist, ratio, ratioErrorBand] + [hist[1] for hist in mcHists]
    #print hists
    for hist in hists:
        hist.GetXaxis().SetRangeUser(*xRange)

  def SetYRange(self,yRange,dataHist):
    dataHist.SetMaximum(yRange[0])
    dataHist.SetMaximum(yRange[1])

  def GetRatioHist(self,dataHist,sumHist):
    ratio = sumHist.Clone()
    ratio.Reset()
    ratio.Divide(dataHist,sumHist)
    return ratio


  def GetTHStack(self,mcHists,Opts):
    thstack = R.THStack('','')
    for name,hist,color in mcHists:
      hist.SetFillColor(color)
    for name,hist,color in mcHists:
      if name == 'z+jets':
        pass
      thstack.Add(hist)

    Opts['Minimum'] = self.Opts['yRange'][0]
    Opts['Maximum'] = self.Opts['yRange'][1]
    Opts['Xaxis']['RangeUser'] = tuple(self.Opts['xRange'])

    return thstack

  def DecorateObjectNew(self,obj,opts):
    for key,value in opts.iteritems():
      if not isinstance(value,dict):
        setter = getattr(obj,'Set{0:}'.format(key))
        if not isinstance(value,tuple):
          setter(value)
        else:
          setter(*value)
      else:
        getter = getattr(obj,'Get{0:}'.format(key))
        _obj = getter()
        self.DecorateObjectNew(_obj,value)


  def DecorateHists(self,dataHist,hs,ratio,errBand):

    optsBnew = self.Opts['errBandnew']
    optsRnew = self.Opts['ratioHist_new']
    optsDnew = self.Opts['dataHist_new']

    self.DecorateObjectNew(ratio,optsRnew)
    self.DecorateObjectNew(errBand,optsBnew)
    self.DecorateObjectNew(dataHist,optsDnew)

  def GetCanvas(self):
    canvas = R.TCanvas('canvas','canvas',*self.Opts['canvasSize'])
    return canvas 
