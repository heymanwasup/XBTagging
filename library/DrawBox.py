
from AtlasStyle import *
import ROOT as R
import toolkit
import tools
import math
from toolkit import ALG
from array import array
import copy
import re
import itertools

R.gROOT.SetBatch(True)

def PrintHist(hist,name=''):
  print '\n\n--------------\n',name
  N = hist.GetNbinsX()
  for n in range(1,N+1):
    c = hist.GetBinContent(n)
    e = hist.GetBinError(n)
    w = hist.GetBinWidth(n)
    l = hist.GetBinLowEdge(n)
    print '{0:3} :: {3:3.0f} ~ {4:3.0f} :: \t {1:6.1e} +- {2:3.1e}'.format(n,c,e,l,l+w)
  print '--------------'

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

def FillHistContent(hist,val,err=None):
  if err==None: 
    err = [0.]*len(val)
  Nbins = hist.GetNbinsX()
  if not ((len(val)==len(err)) and (len(val)==Nbins)):
    raise ValueError( 'len(val) {0:}, len(err) {1:}, NbinsX {2}:'.format(len(val),len(err),Nbins) )
  for n in range(Nbins):
    hist.SetBinContent(n+1,val[n])
    hist.SetBinError(n+1,err[n])
  return hist

'''
Get the names of histograms
'''
class RetrieveHistsNames(object):
  def __init__(self,data,samples,nominals,modellings,variations,ptn_nominal): 
    self.data= data
    self.samples = samples
    self.nominals = nominals
    self.modellings = modellings
    self.variations = variations
    self.ptn_nominal = ptn_nominal
    self.is_flav = False # default value = False

  def SetIsFlav(self,is_flav=True):
    self.is_flav = is_flav

  def SetEntries(self,entries):
    self.entries = entries

  def GetDataHistNames(self,dt_fmt):
    data_name = [dt_fmt.format(sample=data) for data in self.data]
    return data_name

  def GetMCNominalNames(self,mc_fmt):
    return self.GetMCNames(mc_fmt,self.nominals)

  def GetMCNames(self,mc_fmt,mc_samples):
    if self.is_flav:
      return self.GetMCHisNames_flav_com(mc_fmt,mc_samples)
    else:
      return self.GetMCHisNames_sample_com(mc_fmt,mc_samples)
  
  def GetMCHisNames_sample_com(self,mc_fmt,mc_samples):
    samples = {sample:self.samples[sample][version] for sample,version in mc_samples.iteritems()}
    entries = { entry[0] : samples[entry[1]] for entry in self.entries}
    hist_names = {}
    for entry,mc_names in entries.iteritems():
      hist_name = [ mc_fmt.format(sample=sample_name) for sample_name in mc_names ]
      hist_names[entry] = hist_name
    return hist_names

  def GetMCHisNames_flav_com(self,mc_fmt,mc_samples):
    samples = [ self.samples[sample][version] for sample,version in mc_samples.iteritems() ]
    mc_samples = list(reduce(lambda x,y:x+y,samples)) 

    entries_flav = { entry[0] : [ [ entry[1] ], mc_samples ] for entry in self.entries }
    hist_names_flav = {}
    for entry,mc_names in entries_flav.iteritems():
      args = list(itertools.product(*mc_names))
      hist_name = [ mc_fmt.format(flav=arg[0], sample=arg[1]) for arg in args]
      hist_names_flav[entry] = hist_name
    return hist_names_flav

  def GetSystNames(self,mc_fmt,mc_var_fmt):
    modelling_names = self.GetModellingNames(mc_fmt)
    variations = self.GetVariationNames(mc_fmt,mc_var_fmt)
    systs = {}
    systs.update(modelling_names)
    systs.update(variations)
    return systs

  def GetModellingNames(self,mc_fmt):
    modellings = {}
    FooExpander = lambda names_dict : list(reduce(lambda x,y:x+y, names_dict.values()))
    for sample,modellings in self.modellings.iteritems():
      for mod_name,items in modellings.iteritems():
        down = copy.deepcopy(self.nominals)
        down[sample] = items[0]
        down_names = FooExpander( self.GetMCNames(mc_fmt,down) )

        up = copy.deepcopy(self.nominals)
        up[sample] = items[1]
        up_names = FooExpander( self.GetMCNames(mc_fmt,up) )

        modellings[mod_name] = [down_names,up_names]
    return modellings

  def GetVariationNames(self,mc_fmt,mc_var_fmt):
    ptn_nominal = re.compile(self.ptn_nominal)
    FooGetFmt = lambda variation : mc_fmt if ptn_nominal.match(variation) else mc_var_fmt
    
    variations = {}
    FooExpander = lambda names_dict : list(reduce(lambda x,y:x+y, names_dict.values()))
    for variation, items in self.variations.iteritems():
      down_var_fmt = toolkit.PartialFormat(FooGetFmt(items[0]),{'variation':items[0]})
      down_names = FooExpander( self.GetMCNames(down_var_fmt,self.nominals) )

      up_var_fmt = toolkit.PartialFormat(FooGetFmt(items[1]),{'variation':items[1]})
      up_names = FooExpander( self.GetMCNames(up_var_fmt,self.nominals) )

      variations[variation] = [down_names,up_names]

    return variations

'''
get the histograms objects from root file
'''
class RetrieveHists(object):
  def __init__(self,tfile):
    self.is_debug = False
    self.tfile = tfile

  def GetHists(self,data_hist_name,mc_hist_names,syst_hist_names):
    
    dataHist = self.GetHist(data_hist_name)
   
    mcHists,mcSumHist = self.GetMCHists(mc_hist_names)
    
    variationHists = self.GetVariationHists(syst_hist_names)
    
    errbandHist = self.GetErrorBand(mcSumHist,variationHists)
    return dataHist,mcHists,errbandHist

  #get mc histograms and sum of mc histograms
  def GetMCHists(self,mc_hist_names):
    mcHists = {} 
    mcSum = None
    for name,hists in mc_hist_names.iteritems():
      hist = self.GetHist(hists)
      if hist == None:
        raise RuntimeError( '{0:} not exists!'.format(name))
      if mcSum == None:
        mcSum = hist.Clone() 
      else: 
        mcSum.Add(hist)
      mcHists[name] = hist
    return mcHists,mcSum
  
  #get variation hists   
  def GetVariationHists(self,syst_hist_names):  
    systHists = {}
    for name,systs in syst_hist_names.iteritems():
      try:
        #self.is_debug = True 
        do = self.GetHist(systs[0])
        up = self.GetHist(systs[1])
      except RuntimeError:
        print 'skiped systematic : {0:}'.format(name)
        continue

      systHists[name] = [do,up]
    return systHists

  def GetHistFromNames(self,names):
    sumHist = None
    for name in names:
      hist = self.tfile.Get(name) 
      if hist == None:
        continue
      if sumHist == None:
        sumHist = hist.Clone()
      else:
        sumHist.Add(hist)
      if self.is_debug:
        print '\nadd {1:} \n \t\t {2:5.2e}'.format(sumHist.Integral(),name,hist.Integral())
    if self.is_debug:
      print '\nTOTAL: {:6.2e}'.format(sumHist.Integral())
    return sumHist

  #get error band : mc stat. + systs.(modelling/variations)
  def GetErrorBand(self,mcSum,systHists):
    errors = {}
    mcNominal,mcNominal_stat = GetHistContent(mcSum)
    errors['mcstat'] = mcNominal_stat
    Nbins = mcSum.GetNbinsX()
    
    FooPrint = lambda fvals : ' '.join(map(lambda fval:'{0:<8s}'.format('{0:5.1e}'.format(fval)), fvals))

    for name,systs in systHists.iteritems():
      systDown,systDown_stat = GetHistContent(systs[0])
      systUp,systUp_stat = GetHistContent(systs[1])

      error_syst = []
      for n in range(Nbins):
        error_syst.append(abs(systUp[n]-systDown[n])/2.)
      errors[name] = error_syst

      if self.is_debug:
        print '\n\n\n---------------'
        print '{0:s}'.format(name)
        print '\t Down:  {1:}'.format(FooPrint(systDown))
        print '\t   Up:  {1:}'.format(FooPrint(systUp))
        print '\t \t err.  {1:}'.format(FooPrint(error_syst))
        print '---------------'

    errband_tot = [ 0. ] * Nbins
    
    for name,syst in errors.iteritems():
      for n in range(Nbins):
        errband_tot[n] = math.sqrt((errband_tot[n]**2 + syst[n]**2))

    h_errband = mcSum.Clone()
    h_errband.Reset()
    
    FillHistContent(h_errband,mcNominal,errband_tot)

    return h_errband

  def GetHist(self,names):
    hist = self.GetHistFromNames(names)
    if not hist :
      raise RuntimeError('histograms not exist in root file:\n\n\t{0:}\n\n{1:}'.format(str(self.tfile),str(names)))
    return hist


'''
Drawing those histograms
'''
class DrawControlPlots(object):
  def __init__(self,output_path):
    self.output_path = output_path

  def SetDrawOpts(self,opts):
    self.Opts = copy.deepcopy(opts)

  def SetDrawTexts(self,texts):
    self.Texts = copy.deepcopy(texts)
  
  def Print(self,pic_name,dataHist,mcHists,errBand):
    #Prepare the objects going to be drawn on canvas
    objects = self.GetObjects(dataHist, mcHists, errBand)

    #Print the canvas to imagine files
    self.DrawObjects(pic_name,objects)

  def GetObjects(self,dataHist,mcHists,errBand):

    #rebining
    #reunit
    #get&set maximum/minimum value 
    #get&set range 
    #get ratio histogram
    #get ratio error band histogram
    #set marker color/marker offset/title size/label size/...
    ratio,ratioErrorBand = self.ProcessHists(dataHist,mcHists,errBand)
    
    #get thstack
    hs = self.GetTHStack(mcHists,self.Opts['Hist_mcStack'])
    
    #get canvas
    canvas = self.GetCanvas()

    #get up/down tpad
    pad_up = self.GetPad('TPad_up')
    pad_do = self.GetPad('TPad_down')

    #get up/down legend
    leg_up = self.GetUpLegend(dataHist,mcHists)
    leg_do = self.GetDownLegend(ratio,ratioErrorBand)

    #prepare other objects
   
    #objects going to be draw
    objects = { 
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
    return objects

  def DrawText(self,text,x,y,color=1,tsize=-1):
    l = R.TLatex()
    if tsize>0:
      l.SetTextSize(tsize)
    l.SetNDC()
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

  #Drawing the objects and print plots
  def DrawObjects(self,pic_name,P):
    P['canvas'].Draw()

    P['pad_up'].Draw()
    P['pad_do'].Draw()

    P['pad_up'].cd()

    P['hs'].Draw('HIST')
    self.DecorateObject(P['hs'],self.Opts['Hist_mcStack'])
    P['dataHist'].Draw('esame')

    P['leg_up'].Draw('same')

    for name,txts in self.Texts.iteritems():
      self.DrawText(*txts)

    P['pad_do'].cd()

    P['ratio'].Draw('same')

    P['errBand'].Draw('E2same')
    P['leg_do'].Draw('same')

    for fmt in self.Opts['Config_general']['fmt']:
      P['canvas'].Print('{0:}/{1:}.{2:}'.format(self.output_path,pic_name,fmt))

  def GetPad(self,name):
    opts = self.Opts[name]
    pad = self.ConstructRootObject(R.TPad,opts)
    if self.Opts['Config_general']['LogScale'] and name == 'TPad_up' :
      pad.SetLogy(True)
    return pad
    
  def ConstructRootObject(self,Cls,opts):
    constructor = opts['constructor']
    settings = None if not 'settings' in opts else opts['settings']
    if isinstance(constructor,dict):
      obj = Cls(**constructor)
    else:
      obj = Cls(*constructor)
    if not settings == None:
      self.DecorateObject(obj,settings)
    return obj

  def GetUpLegend(self,dataHist,mcHists):
    leg = self.ConstructRootObject(R.TLegend,self.Opts['Legend_up'])
    leg.AddEntry(dataHist,self.Opts['Config_general']['dataName'] ,'p')
    for name,hist,_ in mcHists[-1::-1]:
      leg.AddEntry(hist,name,'f')
    return leg
  
  def GetDownLegend(self,ratio,errBand):
    leg = self.ConstructRootObject(R.TLegend,self.Opts['Legend_down'])
    nameB = self.Opts['Config_general']['errBandName']
    leg.AddEntry(errBand,nameB,'f')
    return leg

  def ProcessHists(self,dataHist,mcHists,errBand):

    self.ReBinning(dataHist,mcHists,errBand)
    self.ReUnit(dataHist,mcHists,errBand)

    sumHist = self.GetMCSum(mcHists)
    ratio = self.GetRatioHist(dataHist,sumHist)
    ratioErrorBand = self.GetRatioErrorBand(errBand)

    cfg = self.Opts['Config_general']
    if cfg['xRange'] == None:
      cfg['xRange'] = self.GetXRange(dataHist)

    isLogScale = cfg['LogScale']
    if cfg['yRange'] == None:
      cfg['yRange'] = self.GetYRange(dataHist,sumHist,isLogScale)


    self.SetXRange(cfg['xRange'], dataHist, mcHists, ratio, ratioErrorBand)
    self.SetYRange(cfg['yRange'], dataHist)

    optsBnew = self.Opts['Hist_ratioErrBand']
    optsRnew = self.Opts['Hist_ratio']
    optsDnew = self.Opts['Hist_data']
    self.DecorateObject(ratio,optsRnew)
    self.DecorateObject(ratioErrorBand,optsBnew)
    self.DecorateObject(dataHist,optsDnew)

    return ratio,ratioErrorBand

  def GetRatioErrorBand(self,errBand):
    NbinsX = errBand.GetNbinsX()
    errb_vals,errb_errs = GetHistContent(errBand)

    ratio_errb_vals = [1.]*NbinsX
    ratio_errb_errs = []
    for n in range(NbinsX):
      if errb_vals[n]==0.:
        ratio_errb_errs.append(0.)
      else:
        ratio_errb_errs.append(errb_errs[n]/errb_vals[n])
    h_ratio_errb = errBand.Clone()
    h_ratio_errb.Reset()
    FillHistContent(h_ratio_errb,ratio_errb_vals,ratio_errb_errs)
    

    return h_ratio_errb


  def ReUnit(self,dataHist,mcHists,errBand):
    cfg = self.Opts['Config_general']
    if cfg['unit'] == None:
      return 
    hists = [dataHist, errBand] + [hist[1] for hist in mcHists]
    unit = cfg['unit']
    NbinsX = hists[0].GetNbinsX() 
    for hist in hists:
      for n in range(NbinsX):
        c = hist.GetBinContent(n+1)
        e = hist.GetBinError(n+1)
        w = hist.GetBinWidth(n+1)
        c_new = c/(w/unit) 
        e_new = e/(w/unit) 
        hist.SetBinContent(n+1,c_new)
        hist.SetBinError(n+1,e_new)

  def ReBinning(self,dataHist,mcHists,errBand):
    xBins = self.Opts['Config_general']['xBins']
    if xBins != None:
      xBins = array('d', xBins)
      FooRebinner = lambda hist:hist.Rebin(len(xBins)-1,'',xBins).Copy(hist)
      FooRebinner(dataHist)
      FooRebinner(errBand)
      for hist in mcHists:
        FooRebinner( hist[1] )
  
  def GetMCSum(self,mcHists):
    #mc sum hist
    mc_hists = [hist[1] for hist in mcHists]
    sumHist = mc_hists[0].Clone()
    sumHist.Reset()
    for hist in mc_hists:
      sumHist.Add(hist)
    return sumHist

  def GetYRange(self,dataHist,sumHist,isLogScale):
    ymax = max(sumHist.GetMaximum(),dataHist.GetMaximum())
    if isLogScale:
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
    hists = [ dataHist, ratio, ratioErrorBand] + [hist[1] for hist in mcHists]
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
      thstack.Add(hist)

    cfg = self.Opts['Config_general']
    Opts['Minimum'] =  [cfg['yRange'][0]]
    Opts['Maximum'] = [cfg['yRange'][1]]
    Opts['Xaxis']['RangeUser'] = cfg['xRange']
    return thstack

  def DecorateObject(self,obj,opts):
    for key,value in opts.iteritems():
      if not isinstance(value,dict):
        getattr(obj,'Set{0:}'.format(key))(*value)
      else:
        getter = getattr(obj,'Get{0:}'.format(key))
        _obj = getter()
        self.DecorateObject(_obj,value)

  def GetCanvas(self):
    canvas = R.TCanvas('canvas','canvas',*self.Opts['Config_general']['canvasSize'])
    return canvas 

'''
Draw the plots
'''
class MakeControlPlots(object):
  def __init__(self,tfile_path,output_path,cfg_path,is_modelling,is_variation):
    cfg = toolkit.json_load(cfg_path)
    toolkit.mkdir(output_path)

    self.output_path = output_path
    tfile = R.TFile(tfile_path,'read')

    data = cfg['data']
    samples = cfg['samples_register']
    nominals = cfg['nominals']
    modellings = cfg['modellings'] if is_modelling else {}

    ptn_nominal =cfg['format']['nominal']['var']
    ptn_variation = cfg['format']['variation']['var']
    variations = tools.GetVarsList(tfile,ptn_nominal,ptn_variation) if is_variation else {}

    self.name_maker = RetrieveHistsNames(data,samples,nominals,modellings,variations,ptn_nominal)
    self.hist_maker = RetrieveHists(tfile)
    self.plots_drawer = DrawControlPlots(output_path)        

  #draw the plots
  def DrawPlots(self,pic_name,dt_fmt,mc_fmt,mc_var_fmt,\
    draw_opts,texts,entries,is_flav):


    #get the names of the histograms 
    self.name_maker.SetIsFlav(is_flav)
    self.name_maker.SetEntries(entries)
    data_hist_name = self.name_maker.GetDataHistNames(dt_fmt)
    mc_hist_names = self.name_maker.GetMCNominalNames(mc_fmt)
    syst_hist_names = self.name_maker.GetSystNames(mc_fmt,mc_var_fmt)
    
    debug = False
    if debug:
      print data_hist_name
      for name,value in mc_hist_names.iteritems() :
        print name,value[0],'\n'

      for name,syst_hist_names in syst_hist_names.iteritems() :
        print '\n\n----------------------------------------'
        print name
        print syst_hist_names[0][0]
        print syst_hist_names[1][0]
        print '----------------------------------------'

      raise ValueError('CC-DBEBUGGING')

    #get the histograms
    dt_hist,mc_hists,errband_hist= self.hist_maker.GetHists(data_hist_name, mc_hist_names,syst_hist_names)

    #draw the histograms
    mc_hists_ordered = [ [entry[0],mc_hists[entry[0]],entry[2]] for entry in entries ]
    self.plots_drawer.SetDrawOpts(draw_opts)
    self.plots_drawer.SetDrawTexts(texts)
    self.plots_drawer.Print(pic_name,dt_hist,mc_hists_ordered,errband_hist)
