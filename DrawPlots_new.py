
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
draw_data = False
deco_new = True

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
    mcNominal,mcNominal_stat = self.GetHistContent(mcSum)
    Nbins = mcSum.GetNbinsX()
    
    errorband = []

    #append mc stat error
    up,down = 0,0
    for n in range(Nbins):
      if mcNominal[n]==0:
        stat_err = 0
      else:  
        up = mcNominal[n]/(mcNominal[n]+mcNominal_stat[n])
        down = mcNominal[n]/(mcNominal[n]-mcNominal_stat[n])
        stat_err = abs(up-down)/2. 
      print 'mc   {0:5.5f}    +-    {1:5.5f}'.format(mcNominal[n],mcNominal_stat[n])
      print 'up   {0:5.5f}    down  {1:5.5f}'.format(up,down)
      print 'stat {0:5.5f}'.format(stat_err)
      print '\n\n\n'
      errorband.append(stat_err)

    #append syst. uncer.
    for name,systs in systHists.iteritems():
      systDown,_ = self.GetHistContent(systs[0])
      systUp,_ = self.GetHistContent(systs[1]) 
      for n in range(Nbins): 
        up = mcNominal[n]/systUp[n]
        down = mcNominal[n]/systDown[n]
        syst_err = abs(up-down)/2.
        errorband[n] = math.sqrt(errorband[n]**2+syst_err**2)

    #fill errorband
    h_errband = mcSum.Clone()
    h_errband.Reset()
    for n in range(Nbins):
      h_errband.SetBinContent(n+1,1)
      h_errband.SetBinError(n+1,errorband[n])
    return h_errband
      
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

  def GetHist(self,names):
    hist = tools.GetHistFromNames(self.tfile,names)
    if not hist :
      raise RuntimeError('hist is empt')
    if self.xbins != None:
      nbins = len(self.xbins)-1
      xbins = array('d',self.xbins) 
      hist = hist.Rebin(nbins,'',xbins)
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
    #get&set maximum/minimum value 
    #get&set range 
    #get ratio histogram
    ratio = self.ProcessHists(dataHist,mcHists,errBand)
    
    #get thstack
    hs = self.GetTHStack(mcHists)

    #set color/marker_size/marker_style/title...
    self.DecorateHists(dataHist,hs,ratio,errBand)
    
    #get canvas
    canvas = self.GetCanvas()

    #get up/down tpad
    pad_up = self.GetPad('upPad')
    pad_do = self.GetPad('downPad')

    #get up/down legend
    leg_up = self.GetUpLegend(dataHist,mcHists)
    leg_do = self.GetDownLegend(ratio,errBand)

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
      'errBand':errBand,
    }
   
  def DrawText(self,text,x,y,color=1,tsize=-1):
    l = R.TLatex()
    if tsize>0:
      l.SetTextSize(tsize)
    l.SetNDC()
    #l.SetTextFont(font)
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

  #Drawing the objects and print plots
  def DrawPlots(self):
    P = self.P
    P['canvas'].Draw()

    P['pad_up'].Draw()
    P['pad_do'].Draw()

    P['pad_up'].cd()

    if draw_data:
      #self.DecorateObjectNew(P['dataHist'],self.Opts['mcHStack_new'])

      if deco_new:
        pass
        self.DecorateObjectNew(P['dataHist'],self.Opts['mcHStack_new'])
      else:
        pass
        self.DecorateHist(P['dataHist'],self.Opts['mcHStack'])


      P['dataHist'].Draw('e')
      P['hs'].Draw('HIST SAME')
      print 'minmimum and maximum for THStack and datahist'
      #print P['hs'].GetMaximum()
      #print P['hs'].GetMinimum()      
      print P['dataHist'].GetMaximum()
      print P['dataHist'].GetMinimum()
    else:

      P['hs'].Draw('HIST')
      if deco_new:
        self.DecorateObjectNew(P['hs'],self.Opts['mcHStack_new'])
      else:
        self.DecorateHist(P['hs'],self.Opts['mcHStack'])
      self.DecorateHist(P['hs'],self.Opts['mcHStack'])
      P['dataHist'].Draw('esame')
      print 'minmimum and maximum for THStack and datahist'
      print P['hs'].GetMaximum()
      print P['hs'].GetMinimum()      
      print P['dataHist'].GetMaximum()
      print P['dataHist'].GetMinimum()



    P['leg_up'].SetTextFont(62)
    P['leg_up'].Draw('same')
    #self.DecorateHist(P['hs'],self.Opts['mcHStack'])
    #P['dataHist'].Draw('esame')

    for name,txts in self.Texts.iteritems():
      self.DrawText(*txts)



    P['pad_do'].cd()
    P['leg_do'].SetTextFont(62)

    P['ratio'].GetYaxis().SetRangeUser(0.5,1.5)
    P['ratio'].Draw('same')

    P['errBand'].Draw('E2same')
    print '\n\nratio'
    self.PrintHist(P['ratio'])
    print '\n\nerrBand'
    self.PrintHist(P['errBand'])
    P['leg_do'].Draw('same')

    for fmt in self.Opts['fmt']:
      P['canvas'].Print('{0:}.{1:}'.format(self.Opts['name'],fmt))

  def PrintHist(self,hist):
    N = hist.GetNbinsX()
    for n in range(1,N+1):
      c = hist.GetBinContent(n)
      e = hist.GetBinError(n)
      print '{0:10}   {1:5.2f} +-  {2:3.5f}'.format(n,c,e)

  def GetPad(self,name):
    opts = self.Opts
    pad = R.TPad(name,name,*opts['%sPosition'%name])  
    for key,value in opts['%sSettings'%name].iteritems():
      getattr(pad,key)(value)

    return pad

  def ProcessAndPrepareHist(self,dataHist,mcHists,errBand):
    mkSize = self.Opts['dataMarkerSize']
    xRange = self.Opts['xRange']
    xBins = Opts['xBins']

    dataHist.SetMarkerSize(mkSize)
    if xRange!=None:
      dataHist.GetXaxis.SetRangeUser(*xRange)
    '''
    if xBins!=None:
      hist = hist.Rebin(len(xBins)-1,array('d',xBins))
    '''

    sumHist = None
    for n,hist in enumerate(mcHists):
      '''
      if xbins!=None:
        hist[1] = hist[1].Rebin(len(xbins)-1,array('d',xbins))
      '''
      if sumHist == None:
        sumHist = hist[1].Clone()
      else:
        sumHist.Add(hist[1])
      hist[1].SetFillColor(color)
      mcHists[n] = hist[0:2]

    ratio = dataHist.Clone()
    ratio.Reset()
    ratio.Divide(dataHist,sumHist)

    '''
    ratio.SetTitle(self.Opts['rTitle'])
    ratio.GetXaxis().SetTitleSize(self.Opts['rXTitleSize'])
    ratio.GetXaxis().SetTitleOffset(self.Opts['rXTitleOffset'])
    ratio.GetXaxis().SetLabelSize(self.Opts['rXLabelSize'])
    ratio.GetYaxis().SetTitleSize(self.Opts['rYTitleSize'])
    ratio.GetYaxis().SetTitleOffset(self.Opts['rYTitleOffset'])
    '''

    errBand.SetFillStyle(self.Opts['errbFillStyle']);
    errBand.SetFillColor(self.Opts['errbFillColor']);
    errBand.SetMarkerColor(self.Opts['errbMarkerColor']);
    '''
    errBand.GetXaxis().SetTitle(self.Opts['errbTitle']);
    errBand.GetXaxis().SetTitleSize(0.1);
    '''
    errBand.SetMarkerSize(0.);
    errBand.SetStats(0);
    errBand.SetLineWidth(1);
    return dataHist,sumHist,mcHists,ratio,errBand

  '''
  def ProcessHists(self,dataHists,mcHists,errBand):
    sumHist = None
    for n,hist in enumerate(mcHists):
      if xbins!=None:
        hist[1] = hist[1].Rebin(len(xbins)-1,array('d',xbins))
      if sumHist == None:
        sumHist = hist[1].Clone()
      else:
        sumHist.Add(hist[1])
      hist[1].SetFillColor(color)
      mcHists[n] = hist[0:2]
  '''
    
  def GetUpLegend(self,dataHist,mcHists):
    position = self.Opts['upLegPosition']
    columns = self.Opts['columns']
    nameD = self.Opts['dataName']
    leg = R.TLegend(*position)
    leg.SetNColumns(columns)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    leg.AddEntry(dataHist,nameD,'p')
    for name,hist,_ in mcHists[-1::-1]:
      leg.AddEntry(hist,name,'f')
    return leg
  
  def GetDownLegend(self,ratio,errBand):
    position = self.Opts['downLegPostion']
    nameB = self.Opts['errBandName']
    leg = R.TLegend(*position)
    leg.AddEntry(errBand,nameB,'f')
#leg.AddEntry(ratio)
    return leg

   

  def ProcessHists(self,dataHist,mcHists,errBand):
    xRange = self.Opts['xRange']
    yRange = self.Opts['yRange']
    xBins  = self.Opts['xBins']
    isLogy = self.Opts['isLogy']
    funit  = self.Opts['funit']

    FooIsHist = lambda x:isinstance(x,R.TH1)
    FooRebinner = lambda hist,xbins:x.Rebin(len(xbins)-1,'',array('d',xbins))
    FooAddHist = lambda histA,histB:(histA,histA.Add(histB))[0]
    FooFooSetXRange = lambda xRange : lambda hist : hist.GetXaxis().SetRangeUser(*xRange)

    mc_hists = [hist[1] for hist in mcHists]
    all_hists = mc_hists + [dataHist, errBand]

    #rebinning all hists
    '''
    if xBins != None:
      ALG().Map(FooIsHist,FooRebinner,all_hists)
      NbinsX = errBand.GetNbinsX()
      for n in range(NbinsX):
        errBand.SetBinContent(n+1,1)
    '''
      
    if funit != None:
      dtmcHists = mc_hists + [dataHist]
      NbinsX = dataHist.GetNbinsX() 
      for hist in dtmcHists:
        for n in range(NbinsX):
          c = hist.GetBinContent(n+1)
          e = hist.GetBinError(n+1)
          w = hist.GetBinWidth(n+1)
          c_new = c/(w/funit) 
          e_new = e/(w/funit) 
          hist.SetBinContent(n+1,c_new)
          hist.SetBinError(n+1,e_new)




           
    #mc sum hist
    sum_start = mc_hists[0].Clone()
    sum_start.Reset()
    sumHist = ALG().Reduce(FooIsHist,FooAddHist,mc_hists,sum_start)

    #get yRange
    ymax = max(sumHist.GetMaximum(),dataHist.GetMaximum())
    if yRange == None:
      if isLogy:
        yRange = [1.,ymax**1.5]
      else:
        yRange = [0.,ymax*1.5]
      self.Opts['yRange'] = yRange

    #data/mc ratio hist
    ratio = sumHist.Clone()
    ratio.Reset()
    ratio.Divide(dataHist,sumHist)
    
    all_hists += [sumHist,ratio]
     
    #set xRange
    if xRange == None:
      nBins = dataHist.GetNbinsX()
      xMin = dataHist.GetBinLowEdge(1) 
      xMax = dataHist.GetBinLowEdge(nBins) + dataHist.GetBinWidth(nBins)
      xRange = [xMin,xMax]
      self.Opts['xRange'] = xRange
    dataHist.SetMaximum(self.Opts['yRange'][1])
    dataHist.SetMinimum(self.Opts['yRange'][0])
    print 'max min for data'
    print self.Opts['yRange']


    
    ALG().Map(FooIsHist,FooFooSetXRange(xRange),all_hists)

    return ratio


  def GetTHStack(self,mcHists):
    thstack = R.THStack('','')
    for name,hist,color in mcHists:
      hist.SetFillColor(color)
    for name,hist,color in mcHists:
      if name == 'z+jets':
        print name
        self.PrintHist(hist)
      thstack.Add(hist)

    thstack.SetMaximum(self.Opts['yRange'][1])
    thstack.SetMinimum(self.Opts['yRange'][0])
    print 'max min for thstack'
    print self.Opts['yRange']
#thstack.GetXaxis().SetRangeUser(*self.Opts['xRange'])
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
         
  def DecorateHist(self,hist,opts):
    if isinstance(hist,R.TH1):
      hist.SetStats(0)
    xaxis = hist.GetXaxis()
    xaxis.SetTitle(opts['xTitle'])
    xaxis.SetTitleSize(opts['xTitleSize'])
    xaxis.SetTitleOffset(opts['xTitleOffset'])
    xaxis.SetTitleFont(opts['xTitleFont'])
    xaxis.SetLabelSize(opts['xLabelSize'])
    xaxis.SetLabelFont(opts['xLabelFont']);
    xaxis.SetLabelOffset(opts['xLabelOffset']);
    xaxis.SetNdivisions(opts['xNdiv'])

    yaxis = hist.GetYaxis()
    yaxis.SetTitle(opts['yTitle'])
    yaxis.SetTitleSize(opts['yTitleSize'])
    yaxis.SetTitleOffset(opts['yTitleOffset'])
    yaxis.SetTitleFont(opts['yTitleFont'])
    yaxis.SetLabelSize(opts['yLabelSize']);
    yaxis.SetLabelFont(opts['yLabelFont']);
    yaxis.SetLabelOffset(opts['yLabelOffset']);
    yaxis.SetNdivisions(opts['yNdiv'])

    if 'MarkerSize' in opts:
      hist.SetMarkerSize(opts['MarkerSize'])
    if 'MarkerColor' in opts:
      hist.SetMarkerColor(opts['MarkerColor'])
    if 'LineWitdth' in opts:
      hist.SetLineWidth(opts['LineWitdth'])
    if 'FillColor' in opts:
      hist.SetFillColor(opts['FillColor'])
    if 'FillStyle' in opts:
      hist.SetFillStyle(opts['FillStyle'])

  def DecorateHists(self,dataHist,hs,ratio,errBand):

    optsD = self.Opts['dataHist']
    optsDnew = self.Opts['dataHist_new']
    optsM = self.Opts['mcHStack']
    optsR = self.Opts['ratioHist']
    optsB = self.Opts['errBand']
    optsBnew = self.Opts['errBandnew']
    optsRnew = self.Opts['ratioHist_new']

    print 'optsD'
    print optsD

    print '\noptsDnew'
    print optsDnew
    self.DecorateHist(dataHist,optsD)
    #self.DecorateObjectNew(dataHist,optsDnew)
    self.DecorateObjectNew(ratio,optsRnew)
    self.DecorateObjectNew(errBand,optsBnew)

  def GetCanvas(self):
    canvas = R.TCanvas('canvas','canvas',*self.Opts['canvasSize'])
    return canvas 
