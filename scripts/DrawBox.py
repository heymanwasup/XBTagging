#from AtlasStyle import *
import AtlasStyle
import ROOT as R
import toolkit
import root_toolkit
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
        print '\n\n','-'*18
        print '{0:} \t: skiped systematic in errBand \t: {1:}'.format(self.pic_name,name)
        print 'down',systs[0][0],'......'
        print 'up',systs[1][0],'......'
        print '-'*18
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
    self.y_max_scale = 1.6
  def SetDrawOpts(self,opts):
    self.Opts = copy.deepcopy(opts)

  def SetDrawTexts(self,texts):
    self.Texts = copy.deepcopy(texts)
  
  def Print(self,pic_name,dataHist,mcHists,errBand):
    #Prepare the objects going to be drawn on canvas
    self.pic_name = pic_name
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
    if len(mcHists)>5:
      leg.SetNColumns(2)
    for name,hist,_ in mcHists:
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
      yRange = [1.,ymax**self.y_max_scale]
    else:
      yRange = [0.,ymax*self.y_max_scale]
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
    for name,hist,color in mcHists[-1::-1]:
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
  def __init__(self,tfile_path,output_path,run_cfg_path):
    run_config = toolkit.json_load(run_cfg_path)
    overall_cfg = toolkit.json_load('./data/Overall_Info.json')

    tfile = R.TFile(tfile_path,'read')
    args = self.ReadConfig(overall_cfg,run_config,tfile)
 
    outputDir = '{0:}/plots_ControlPlots'.format(output_path)
    toolkit.mkdir(outputDir)

    self.name_maker = RetrieveHistsNames(**args)
    self.hist_maker = RetrieveHists(tfile)
    self.plots_drawer = DrawControlPlots(outputDir)        

  def ReadConfig(self,overall_cfg,run_cfg,tfile):
    args = {}

    args['data'] = overall_cfg['data'][run_cfg['data']]
    args['nominals'] = run_cfg['nominals']
    args['modellings'] = {}#{sample:overall_cfg['modellings'][sample][version] for sample,version in run_cfg['modellings'].iteritems()}
    
    hist_name_format = overall_cfg['format'][run_cfg['format']]
    ptn_nominal = hist_name_format['nominal']['var']
    ptn_variation = hist_name_format['variation']['var']

    variations = root_toolkit.GetVarsList(tfile,ptn_nominal,ptn_variation) if not run_cfg['onlyNominal'] else {}
    
    args['ptn_nominal'] = ptn_nominal
    args['variations'] = variations

    samples = {} # nominal + modellings
    for sample,version in run_cfg['nominals'].iteritems(): # append nominal
      samples[sample] = [version]

    for sample,modelling_version in run_cfg['modellings'].iteritems(): # append modellings
      modellings = overall_cfg['modellings'][sample][modelling_version]
      for modelling_name,up_down in modellings.iteritems():
        pass
        #samples[sample] += up_down

    args['samples'] = {}
    for sample,versions in samples.iteritems():
      args['samples'][sample] = {}
      for version in set(versions):
        args['samples'][sample][version] = overall_cfg['samples'][sample][version]

    return args



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


def GetSumOfErrors(errors):
    sum_of_err = [0.]*len(errors[0])
    for err in errors:
        for n in range(len(err)):
            sum_of_err[n] = math.sqrt(sum_of_err[n]**2 + err[n]**2)
    return sum_of_err

class BtaggingPlots(object):
    def __init__(self,output_path):
        self.scale_x = 1.05
        self.output_path = '{0:}/plots_BtaggingPlots'.format(output_path)
        
        toolkit.mkdir(self.output_path)
    def DrawSFcomparison(self,plot_name,input_json_A,input_json_B,nameA,nameB,cfg,texts):
        data_A = self.ExtractData_SF(input_json_A,0.05)
        data_B = self.ExtractData_SF(input_json_B)

        objects = self.GetObjects_SFcomparison(data_A,data_B,nameA,nameB,cfg)
        self.DrawObjects_SFcomparison(plot_name,objects,cfg,texts)
        
    def GetObjects_SFcomparison(self,data_A,data_B,nameA,nameB,cfg):                
        objects_A = self.GetObjects_SF(data_A,cfg)
        objects_A['central'].SetLineColor(R.kBlue)
        objects_A['central'].SetMarkerColor(R.kBlue)
        objects_A['central'].SetMarkerStyle(4)
        objects_A['errband'].SetFillColorAlpha(R.kBlue,0.55)
        objects_A['errband'].SetFillStyle(3335)
        
        objects_B = self.GetObjects_SF(data_B,cfg)
        objects_B['central'].SetLineColor(R.kRed)
        objects_B['central'].SetMarkerColor(R.kRed)
        objects_B['central'].SetMarkerStyle(8)
        objects_B['errband'].SetFillColorAlpha(R.kRed,0.55)
        objects_B['errband'].SetFillStyle(3353)

        errband = R.TMultiGraph('errband','errband')
        errband.Add(objects_A['errband'])
        errband.Add(objects_B['errband'])
    
        legend = self.GetLegend_SFcomparison(objects_A['central'],objects_A['errband'],objects_B['central'],objects_B['errband'],nameA,nameB,cfg)
        
        objects = {
            'canvas':objects_B['canvas'],
            'central_A':objects_A['central'],
            'central_B':objects_B['central'],
            'errband':errband,
            'legend':legend,

        }
        return objects
   
    def DrawObjects_SFcomparison(self,plot_name,objects,cfg,texts):
        objects['canvas'].Draw()

        objects['errband'].Draw('A2')
        self.DecorateErrBand_SFcomparison(objects['errband'],cfg)

        objects['central_A'].Draw('PZSAME')
        objects['central_B'].Draw('PZSAME')
        objects['legend'].Draw()

        for text in texts:
            self.DrawText(*text)

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/comparison_sf_{1:}.{2:}'.format(self.output_path,plot_name,fmt))
    
    def DecorateErrBand_SFcomparison(self,errband,cfg):
        xax = errband.GetXaxis()
        xax.SetRangeUser(0,cfg['xBins'][-1]*self.scale_x)
        xax.SetTitle(cfg['xTitle'])

        yax = errband.GetYaxis()
        yax.SetNdivisions(507)
        yax.SetRangeUser(*cfg['yRange'])
        yax.SetTitle(cfg['yTitle'])      

    def GetLegend_SFcomparison(self,central_A,errband_A,central_B,errband_B,nameA,nameB,cfg):
        legend = R.TLegend(*cfg['LegendPosition'])
        cA = '{0:} {1:}'.format(nameA,cfg['errbarName'])
        eA = '{0:} {1:}'.format(nameA,cfg['errbandName'])
        cB = '{0:} {1:}'.format(nameB,cfg['errbarName'])
        eB = '{0:} {1:}'.format(nameB,cfg['errbandName'])
        legend.AddEntry(central_A,cA,'lep')
        legend.AddEntry(errband_A,eA,'f')
        
        legend.AddEntry(central_B,cB,'lep')
        legend.AddEntry(errband_B,eB,'f')
        
        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        return legend    
    
    def DrawSF(self,plot_name,input_json,cfg,texts):
        data = self.ExtractData_SF(input_json)
        objects = self.GetObjects_SF(data,cfg)

        self.DrawObjects_SF(plot_name,objects,cfg,texts)
    
    def ExtractData_SF(self,input_json,shift=0.):
        results = toolkit.json_load(input_json)['sf']
        data = {}
        FooShift = lambda x : list(map(lambda y:y+shift, x))
        data['sf'] = FooShift(results.pop('nominal'))
        data['stat err'] = results['data stats']
        data['tot err'] = GetSumOfErrors(results.values())
        return data
 
    def GetObjects_SF(self,data,cfg):
        sf = data['sf'][1:]
        tot_err = data['tot err'][1:]
        stat_err = data['stat err'][1:]

        canvas = self.GetCanvas()
        errband = self.GetErrbandGraph_SF(sf, tot_err ,cfg)
        central = self.GetCentralGraph_SF(sf, stat_err ,cfg)
        legend = self.GetLegend_SF(central,errband,cfg)
        line_one = self.GetLineOne(0,cfg['xBins'][-1])

        objects = {
            'canvas' : canvas,
            'errband' : errband,
            'central' : central,
            'legend' : legend,
            'line_one' : line_one,
        }
        return objects

    def DrawObjects_SF(self,plot_name,objects,cfg,texts):
        objects['canvas'].Draw()
        objects['errband'].Draw('A2')
        objects['central'].Draw('PZSAME')
        objects['legend'].Draw()
        objects['canvas'].Update()

        for text in texts:
            self.DrawText(*text)

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/sf_{1:}.{2:}'.format(self.output_path,plot_name,fmt))

    def GetErrbandGraph_SF(self,sf,tot_err,cfg):
        error_graph = self.GetErrorGraph(sf,tot_err,cfg['xBins'])

        error_graph.SetMarkerSize(1);
        error_graph.SetFillColor(416)
        error_graph.SetFillStyle(1001)
        error_graph.SetLineWidth(2)        
        

        xax = error_graph.GetXaxis()
        xax.SetRangeUser(0,cfg['xBins'][-1]*self.scale_x)
        xax.SetTitle(cfg['xTitle'])

        yax = error_graph.GetYaxis()
        yax.SetNdivisions(507)
        yax.SetRangeUser(*cfg['yRange'])
        yax.SetTitle(cfg['yTitle'])
        return error_graph

    def GetLegend_SF(self,central,errBand,cfg):
        legend = R.TLegend(*cfg['LegendPosition'])
        legend.AddEntry(central, cfg['errbarName'],'lep')
        legend.AddEntry(errBand, cfg['errbandName'],'f')
        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        return legend

    def GetCentralGraph_SF(self,sf, stat_err,cfg):
        central_graph = self.GetErrorGraph(sf,stat_err,cfg['xBins'])
        central_graph.SetLineWidth(2)
        return central_graph

    def DrawEff(self,plot_name,input_json,cfg,texts):
        data = self.ExtractData_Eff(input_json)
        objects = self.GetObjects_Eff(data,cfg)
        self.DrawObjects_Eff(plot_name,objects,cfg,texts)
    
    def ExtractData_Eff(self,input_json):
        results = toolkit.json_load(input_json)
        data = {}
        data['e_dt'] = results['e_dt']['nominal']
        data['e_dt_data_stat'] = results['e_dt']['data stats']
        data['e_mc'] = results['e_mc']['nominal']
        data['e_mc_mc_stat'] = results['e_mc']['mc stats']
        return data    
    
    def GetObjects_Eff(self,data,cfg):
        e_dt = data['e_dt'][1:]
        e_dt_err = data['e_dt_data_stat'][1:]
        e_mc = data['e_mc'][1:]
        e_mc_err = data['e_mc_mc_stat'][1:]

        canvas = self.GetCanvas()
        g_e_dt = self.GetGraphEffData(e_dt,e_dt_err,cfg)
        g_e_mc = self.GetGraphEffMC(e_mc,e_mc_err,cfg)
        legend = self.GetLegend_Eff(g_e_dt,g_e_mc,cfg)
        objects = {
            'canvas':canvas,
            'g_e_dt':g_e_dt,
            'g_e_mc':g_e_mc,
            'legend':legend,
        }
        return objects

    def DrawObjects_Eff(self,plot_name,objects,cfg,texts):
        objects['canvas'].Draw()
        objects['g_e_mc'].Draw('APZ')
        objects['g_e_dt'].Draw('PZSAME')

        objects['legend'].Draw()
        
        for text in texts:
            self.DrawText(*text)        

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/eff_{1:}.{2:}'.format(self.output_path,plot_name,fmt))

    def GetGraphEffData(self,central,error,cfg):
        g_e_dt = self.GetErrorGraph(central,error,cfg['xBins'])
        g_e_dt.SetLineWidth(2)
        return g_e_dt

    def GetGraphEffMC(self,central,error,cfg):
        g_e_mc = self.GetErrorGraph(central,error,cfg['xBins'])
        g_e_mc.SetLineColor(R.kRed)
        g_e_mc.SetMarkerColor(R.kRed)
        g_e_mc.SetMarkerStyle(24)
        g_e_mc.SetLineWidth(2)

        xax = g_e_mc.GetXaxis()
        xax.SetTitle(cfg['xTitle'])
        xax.SetRangeUser(0,cfg['xBins'][-1]*self.scale_x)

        yax = g_e_mc.GetYaxis()
        yax.SetNdivisions(505)
        yax.SetTitle(cfg['yTitle'])
        yax.SetRangeUser(*cfg['yRange'])
        return g_e_mc
 
    def GetLegend_Eff(self,g_e_dt,g_e_mc,cfg):
        legend = R.TLegend(*cfg['LegendPosition'])
        legend.AddEntry(g_e_dt,cfg['effDataName'],'p')
        legend.AddEntry(g_e_mc,cfg['effMCName'],'p')

        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        return legend

    def DrawText(self,text,x,y,tsize=-1,color=1):
        l = R.TLatex()
        if tsize>0:
          l.SetTextSize(tsize)
        l.SetNDC()
        l.SetTextColor(color)
        l.DrawLatex(x,y,text)

    def GetLineOne(self,xmin,xmax):
        line_one = R.TLine(xmin,1.,xmax*self.scale_x,1)
        line_one.SetLineColor(R.kGreen)
        line_one.SetLineStyle(2)
        line_one.SetLineWidth(3)
        return line_one

    def GetErrorGraph(self,central,error,xBins):
        x, ex = self.GetXPosition(xBins)
        y, ey =array('d', central), array('d', error)
        graph = R.TGraphErrors( len(x), x, y, ex, ey )
        return graph

    def GetXPosition(self,xbins):
        x = []
        ex = []
        for n in range(len(xbins)-1):
            x.append((xbins[n]+xbins[n+1])/2.)
            ex.append((xbins[n+1]-xbins[n])/1.995)
        return array('d',x), array ('d',ex)

    def GetCanvas(self):
        canvas = R.TCanvas('c1','c1',800,800)
        canvas.SetTopMargin(0.05)
        return canvas

class DrawAPI(object):
  def __init__(self,input_file,output_path,cfg_path):

    self.printer = MakeControlPlots(input_file,output_path,cfg_path)

    errBandName = 'MC stat.'
    cfg = toolkit.json_load(cfg_path)
    if not cfg['onlyNominal']:
      errBandName += ' + syst. unc.'
    if len(cfg['modellings'])!=0:
      samples = ' / '.join(cfg['modellings'].keys())
      errBandName += ' + {0:} modellings'.format(samples)

    #can overide some settings in config file
    settings = {
      'errBandName': errBandName,
    }

    self.config_default = toolkit.json_load('./data/PlottingConfig_default.json')
    self.config_default['Config_general'].update(settings)


  def Draw(self,pic_name,hist_name,config_user,texts,fmts,entries,is_flav):
    kw= dict(name=hist_name)
    args = {
      'dt_fmt':toolkit.PartialFormat(fmts['dt_fmt'],kw),
      'mc_fmt':toolkit.PartialFormat(fmts['mc_fmt'],kw),
      'mc_var_fmt':toolkit.PartialFormat(fmts['mc_var_fmt'],kw),
    }

    args['texts'] = texts
    args['is_flav'] = is_flav
    args['entries'] = entries
    args['pic_name'] = pic_name

    config = toolkit.MergeDict_recursive(self.config_default, config_user)
    args['draw_opts'] = config
    self.printer.DrawPlots(**args) 