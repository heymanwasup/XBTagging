import ROOT as R

    
def ControlPlots(object):
  def __init__(self,dataHist,mcHists,errband,opts={},txts={}):
    self.Options = {
     'ratioXTitle'       : 'MV2c10',
     'ratioYTitle'       : 'Data/Pred.',
     'yTitle'            : 'Jets / 0.10',
     'errband'           : 'Syst. + MC Stat. Uncertainty',
     'leg_up'            : [0.65,0.75,0.9,0.95],
     'leg_do'            : [0.35,0.8,0.8,0.95],
     'logScale'          : True,
     'xRange'            : None,
     'xBins'             : None,
     'yRange'            : None,

     'ratioMarkerSize'   : 0.6,
     'ratioXTitleSize'   : 0.13,
     'ratioXTitleOffset' : 1.2, 
     'ratioXLabelOffset' : 1.2, 
     'ratioYTitleSize'   : 0.13,
     'ratioYTitleOffset' : 1.2, 
     'ratioYLabelOffset' : 1.2, 
     'xTitleSize'        : 0.13,
     'xTitleOffset'      : 1.2, 
     'xLabelOffset'      : 1.2, 
     'yTitleSize'        : 0.13,
     'yTitleOffset'      : 1.2, 
    }

    #['text',[x,y],size=1,color=1]
    self.Texts = { 
      'ATLAS'  : ['#font[72]{ATLAS}',[0.2,0.9]],
      'status' : ['#font[42]{Internal}',[0.37,0.9]], 
      'Lumi'   : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',[0.2,0.85],0.0375],
      'region' : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',[0.2,0.8],0.03],
    }

    self.Options.update(opts)
    self.Texts.update(texts)
  
    self.dataHist = dataHist
    self.mcHists  = mcHists
    self.errband = errband

  def GetPad(self,opts):
    pad = TPad(name,name,*opts['position'])  
    pad.SetTopMargin(opts['TopMargin']);
    pad.SetBottomMargin(opts['BottomMargin']);
    pad.SetLeftMargin(opts['LeftMargin']);
    pad.SetRightMargin(opts['RightMargin']);
    if 'logy' in opts and opts['logy']:
      pad.SetLogy()
    return pad

  def ProcessAndPrepareHist(self,dataHist,mcHists,errband):

    mkSize = self.Options['dataMarkerSize']
    xRange = self.Options['xRange']
    xBins = Options['xBins']

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
    ratio.SetTitle(self.Options['rTitle'])
    ratio.GetXaxis().SetTitleSize(self.Options['rXTitleSize'])
    ratio.GetXaxis().SetTitleOffset(self.Options['rXTitleOffset'])
    ratio.GetXaxis().SetLabelSize(self.Options['rXLabelSize'])
    ratio.GetYaxis().SetTitleSize(self.Options['rYTitleSize'])
    ratio.GetYaxis().SetTitleOffset(self.Options['rYTitleOffset'])

    errband.SetFillStyle(self.Options['errbFillStyle']);
    errband.SetFillColor(self.Options['errbFillColor']);
    errband.SetMarkerColor(self.Options['errbMarkerColor']);
    errband.GetXaxis().SetTitle(self.Options['errbTitle']);
    errband.GetXaxis().SetTitleSize(0.1);
    errband.SetMarkerSize(0.);
    errband.SetStats(0);
    errband.SetLineWidth(1);
    
    return dataHist,sumHist,mcHists,ratio,errband

  def ProcessHists(self,dataHists,mcHists,errband):
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
    
  def GetLegend(self,opts):
    leg = TLegend(*opts['position'])
    if 'NColumns' in opts:
      leg.SetNColumns(opts['NColumns'])
    else:
      leg.SetNColumns(1)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    return leg

  def Prepare(self):

    #rebining
    #get&set maximum/minimum value 
    #get&set range 
    #get ratio histogram
    self.ratio = self.ProcessHists(self.dataHist,self.mcHists,self.errband)
    
    #set color/marker_size/marker_style/title...
    self.DecorateHists(self.dataHist,self.mcHists,self.ratio,self.errband)
    
    #get canvas
    canvas = self.GetCanvas()

    #get thstack
    hs = self.GetTHStack(self.mcHists)

    #get up/down tpad
    pad_up = self.GetPad('upPad')
    pad_do = self.GetPad('doPad')

    #get up/down legend
    leg_up = self.GetUpLegend(self.dataHist,self.mcHists)
    leg_do = self.GetDownLegend(self.ratio,self.errband)

    #prepare other objects
   
    #objects going to be draw
    self.P = { 
      'canvas':canvas,
      'pad_up':pad_up,
      'pad_do':pad_do,
      'dataHist':dataHist,
      'hs':hs,
      'ratio':ratio,
      'errband':errband
      'leg_up':leg_up,
      'leg_do':leg_do,
    }
    
  #drawing the objects and print plots
  def Draw(self):
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
    P['errband'].Draw('E2same')
    P['ratio'].Draw('same')
    P['leg_do'].Draw('same')

    for fmt in self.Options['fmt']
      P['canvas'].Print('{0:}.{1:}'.format(self.Options['name'],fmt))

