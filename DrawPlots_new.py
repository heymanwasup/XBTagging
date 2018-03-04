import ROOT as R
import toolkit
from toolkit import ALG
from array import array
import copy

#retrieve histograms from root file
#data, mc, errband 
class RetrieveHists(object):
  def __init__(self,tfile,dataHistName,mcHistsName,systsName={},xbins=None):
    self.tfile = tfile
    self.dataHistName = dataHistName 
    self.mcHistsName = mcHistsName
    self.systsName = systsName
    self.xbins = xbins

  def PrepareHists(self): 
    self.dataHist = self.GetHist([self.dataHistName])
    self.mcHists = {} 
    for name,hists in self.mcHistsName.iteritems():
      self.mcHists[name] = self.GetHist(hists)
    self.GetErrorBand()    

  def GetHist(self,names):
    sumHist = None
    for name in names:
      hist = self.file.Get(name) 
      if hist == None:
        continue
      if sumHist == None:
        sumHist = hist.Clone()
      else:
        sumHist.Add(sumHist)
    if self.xbins != None:
      nbins = len(self.xbins)-1
      xbins = array('d',self.xbins) 
      sumHist = sumHist.Rebin(nbins,'',xbins)
    return sumHist
    
  def GetErrBand(self):



class DrawControlPlots(object):
  def __init__(self,opts,txts={}):
    self.Opts = opts
    self.Texts = txts
  
  def Print(self,dataHist,mcHists,errBand):
    #Prepare the objects going to be draw on canvas
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
    pad_do = self.GetPad('doPad')

    #get up/down legend
    leg_up = self.GetUpLegend(self.dataHist,self.mcHists)
    leg_do = self.GetDownLegend(self.ratio,self.errBand)

    #prepare other objects
   
    #objects going to be draw
    self.P = { 
      'canvas':canvas,
      'pad_up':pad_up,
      'pad_do':pad_do,
      'dataHist':dataHist,
      'hs':hs,
      'ratio':ratio,
      'errBand':errBand
      'leg_up':leg_up,
      'leg_do':leg_do,
    }
    
  #Drawing the objects and print plots
  def DrawPlots(self):
    P = self.P
    P['canvas'].Draw()
    P['pad_up'].Draw()
    P['pad_do'].Draw()

    P['pad_up'].cd()
    P['leg_up'].Draw()
    P['hs'].Draw('HIST')
    P['dataHist'].Draw('esame')
    for name,txts in self.Texts.iteritems():
      self.DrawText(*txts)

    P['pad_do'].cd()
    P['errBand'].Draw('E2same')
    P['ratio'].Draw('same')
    P['leg_do'].Draw('same')

    for fmt in self.Opts['fmt']
      P['canvas'].Print('{0:}.{1:}'.format(self.Opts['name'],fmt))

  def GetPad(self,name):
    opts = self.Opts
    pad = self.TPad(name,name,*opts['%sPosition'%name])  
    pad.SetTopMargin(opts['%sTopMargin'%name]);
    pad.SetBottomMargin(opts['%sBottomMargin'%name]);
    pad.SetLeftMargin(opts['%sLeftMargin'%name]);
    pad.SetRightMargin(opts['%sRightMargin'%name]);
    if 'logy' in opts and opts['%sLogy'%name]:
      pad.SetLogy()
    return pad

  def ProcessAndPrepareHist(self,dataHist,mcHists,errBand):
    mkSize = self.Opts['dataMarkerSize']
    xRange = self.Opts['xRange']
    xBins = Opts['xBins']

    dataHist.SetMarkerSize(mkSize)
    if xRange!=None:
      dataHist.GetXaxis.SetRangeUser(*xRange)
    if xBins!=None:
      hist = hist.Rebin(len(xBins)-1,array('d',xBins))

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

    ratio = dataHist.Clone()
    ratio.Reset()
    ratio.Divide(dataHist,sumHist)
    ratio.SetTitle(self.Opts['rTitle'])
    ratio.GetXaxis().SetTitleSize(self.Opts['rXTitleSize'])
    ratio.GetXaxis().SetTitleOffset(self.Opts['rXTitleOffset'])
    ratio.GetXaxis().SetLabelSize(self.Opts['rXLabelSize'])
    ratio.GetYaxis().SetTitleSize(self.Opts['rYTitleSize'])
    ratio.GetYaxis().SetTitleOffset(self.Opts['rYTitleOffset'])

    errBand.SetFillStyle(self.Opts['errbFillStyle']);
    errBand.SetFillColor(self.Opts['errbFillColor']);
    errBand.SetMarkerColor(self.Opts['errbMarkerColor']);
    errBand.GetXaxis().SetTitle(self.Opts['errbTitle']);
    errBand.GetXaxis().SetTitleSize(0.1);
    errBand.SetMarkerSize(0.);
    errBand.SetStats(0);
    errBand.SetLineWidth(1);
    return dataHist,sumHist,mcHists,ratio,errBand

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
    
  def GetUpLegend(self,dataHist,mcHists):
    position = self.Opts['upLegPosition']
    columns = self.Opts['columns']
    nameD = self.Opts['dataName']
    leg = R.TLegend(*position)
    leg.SetNColumns(*columns)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    leg.AddEntry(dataHist,nameD,'p')
    for name,hist in mcHists:
      hist.AddEntry(hist,name,'f')
    return leg
  
  def GetDownLegend(self,ratio,errBand):
    position = self.Opts['downLegPostion']
    nameB = self.Opts['errBandName']
    leg = R.TLegend(*position)
    leg.AddEntry(errBand,nameB,'f')
    leg.AddEntry(ratio)

   

  def ProcessHists(self,dataHist,mcHists,errBand):
    xRange = self.Opts['xRange']
    yRange = self.Opts['yRange']
    xBins  = self.Opts['xBins']
    isLogy = self.Opts['isLogy']

    FooIsHist = lambda x:isinstance(x,R.TH1)
    FooRebinner = lambda hist,xbins:x.Rebin(len(xbins)-1,'',array('d',xbins))
    FooAddHist = lambda histA,histB:(histA,histA.Add(histB))[0]
    FooFooSetXRange = lambda xRange : lambda hist : hist.GetXaxis().SetRangeUser(*xRange)


    mc_hists = [hist[1] for hist in mcHists]
    all_hists = mc_hists + [dataHists, errBand]

    #rebinning all hists
    if xBins != None:
      ALG().Map(FooIsHist,FooRebinner,all_hists)
    
    #mc sum hist
    sum_start = mc_hits[0].Clone()
    sum_start.Reset()
    sumHist = ALG().Reduce(FooIsHist,FooAddHist,mc_hists,sum_start)

    #get yRange
    ymax = max(sumHist.GetMaximum(),dataHist.GetMaximum)
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
    
    all_hists.append(sumHist,ratio)
     
    #set xRange
    if xRange == None:
      nBins = dataHist.GetNbinsX()
      xMin = dataHist.GetBinLowEdge(1) 
      xMax = dataHist.GetBinLowEdge(nBins) + dataHist.GetBinWidth(nBins)
      xRange = [xMin,xMax]
      self.Opts['xRange'] = xRange
    
    ALG().Map(FooIsHist,FooFooSetXRange(xRange),all_hists)

    return ratio


  def GetTHStack(self,mcHists):
    thstack = R.THStack('hstack','hstack')
    for name,hist,color in mcHists:
      hist.SetFillColor(color)
    for name,hist,color in mcHists:
      thstack.Add(hist)
    thstack.SetMaximum(self.Opts['yRange'][1])
    thstack.SetMinimum(self.Opts['yRange'][0])
    thstack.GetXaxis().SetRangeUser(*self.Opts['xRange'])
    return thstack

  def DecorateHists(self,dataHist,hs,ratio,errBand):
    def DecorateHist(hist,opts):
        xaxis = hist.GetXaxis()
        xaxis.SetTitle(opts['xTitle'])
        xaxis.SetTitleSize(opts['xTitleSize'])
        xaxis.SetTitleOffset(opts['xTitleOffset'])
        xaxis.SetTitleFont(opts['xTitleFont'])
        xaxis.SetLabelSize(opts['xLabelSize']);
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

        hist.SetMarkerSize(opts['MarkerSize'])
        hist.SetMarkerColor(opts['MarkerColor'])
        hist.SetLineWidth(opts['LineWitdth'])
    optsD = self.Opts['dataHist']
    optsM = self.OPts['mcHStack']
    optsR = self.Opts['ratioHist']
    optsB = self.Opts['errBand']
    DecorateHist(dataHist,optsD)
    DecorateHist(hs,optsM )
    DecorateHist(ratio,optsR)
    DecorateHist(errBand,optsB)
    
  def GetCanvas(self):
    canvas = R.TCanvas('canvas','canvas',self.Opts['canvasSize'])
    return canvas 

      
