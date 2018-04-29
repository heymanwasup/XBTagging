
import copy,itertools

import ROOT as R
import toolkit
import tools


import DrawPlots_new as DB

from drawopts import OPts

'''
    'entries' = 
      [
        ['Light-flavour jet',Color1,[('L'),('ttbar','stop_Wt','diboson_sherpa')]],
        ['Charm-flavour jet',Color2,[('C'),('ttbar','stop_Wt','diboson_sherpa')]],
        ['B-flavour jet',    Color3,[('B'),('ttbar','stop_Wt','diboson_sherpa')]],
      ]
'''

class MakeControlPlots(object):
  def __init__(self,tfile_path,output_path,cfg_path):
    cfg = toolkit.json_load(cfg_path)
    ptn_nominal =cfg['format']['nominal']['var']
    ptn_variation = cfg['format']['variation']['var']
    toolkit.mkdir('{0:}/{1:}'.format(output_path,cfg['rtag']))

    self.tfile = R.TFile(tfile_path)
    self.output_path = output_path
    self.jet = cfg['jet']
    self.rtag = cfg['rtag']
    self.data = cfg['data']
    self.nominals = cfg['nominals']
    self.modellings = cfg['modellings']
    self.vars_list = tools.GetVarsList(self.tfile,ptn_nominal,ptn_variation)
    self.samples = cfg['samples_register']
    

  #entries = [[NameInLeg, NameInHist, Color],[]...]
  def SetupDraw(self,entries,is_modelling,is_variation,is_flav):
    self.entries = entries
    self.is_modelling = is_modelling
    self.is_variation = is_variation
    self.is_flav = is_flav


  #draw the plots
  def DrawPlots(self,draw_opts,texts,dt_fmt,mc_fmt,mc_var_fmt=None):
    
    #get the names of the histograms 
    data_hist_name = self.GetDataNames(dt_fmt)
    mc_hist_names = self.GetMCNames(mc_fmt,self.nominals)
    syst_hist_names = self.GetSystNames(mc_fmt,mc_var_fmt)
    
#    P(data_hist_name)
#    P(mc_hist_names)
#    P(syst_hist_names)
#    return 

    #get the histograms 
    xbins = draw_opts['xBins']
    hist_maker = DB.RetrieveHists(self.tfile,data_hist_name,mc_hist_names,syst_hist_names,xbins) 

    dt_hist,mc_hists,errband_hist = hist_maker.PrepareHists()

#print mc_hists
    mc_hists_organ = [ [entry[0],mc_hists[entry[0]],entry[2]] for entry in self.entries ]

    
    print '\n\n\n-----------------------------------------------------------'
    print mc_hists

    '''
    f = R.TFile('plots.root','recreate')
    dt_hist.Write()
    for name,hist in mc_hists.iteritems():
      hist.SetName(name)
      hist.Write()
    errband_hist.SetName('herrband')
    errband_hist.Write()
    f.Close()
    return 
    '''
  
    #draw the histograms
    plots_drawer = DB.DrawControlPlots(draw_opts,texts)
    plots_drawer.Print(dt_hist,mc_hists_organ,errband_hist)

  def GetDataNames(self,dt_fmt):
    data_name = [dt_fmt.format(sample=data) for data in self.data]
    return data_name

  def GetMCNames(self,mc_fmt,mc_samples):
    samples = self.GetMCSamples(self.entries,mc_samples)
    mc_names = {}
    for name,entry in samples.iteritems():
      mc_names[name] = []
      values = list(itertools.product(*entry))
      for value in values:
        if self.is_flav:
          key_value = {'flav':value[0],'sample':value[1]}
        else:
          key_value = {'sample':value[0]}
        mc_names[name].append(mc_fmt.format(**key_value)) 
    return mc_names 
     
  def GetSystNames(self,mc_fmt,mc_var_fmt):
    systs = {}
    if self.is_modelling:
      for sample,modellings in self.modellings.iteritems():
        for mod_name,items in modellings.iteritems():
          samples = copy.deepcopy(self.nominals)
          up = toolkit.MergeDict(self.nominals,{sample:items[0]})
          down = toolkit.MergeDict(self.nominals,{sample:items[1]})
          up_names = self.GetMCNames(mc_fmt,up)
          down_names = self.GetMCNames(mc_fmt,down)
          systs[mod_name] = [up_names,down_names]
    
    FooExpander = lambda systs:[reduce(lambda x,y:x+y,systs.values())]
    if self.is_variation:
      FooFmt = lambda variation : mc_fmt if variation == 'SysNominal' else mc_var_fmt
      for variation, items in self.vars_list.iteritems():
        up_var_fmt = toolkit.PartialFormat(FooFmt(items[0]),{'var':items[0]})
        _up_names = self.GetMCNames(up_var_fmt,self.nominals)
        up_names = FooExpander(_up_names) 

        down_var_fmt = toolkit.PartialFormat(FooFmt(items[1]),{'var':items[1]})
        _down_names = self.GetMCNames(down_var_fmt,self.nominals)
        down_names = FooExpander(_down_names) 
        systs[variation] = [up_names,down_names]
    return systs

  def GetMCSamples(self,entries,mc_samples): 
    _samples = {sample:self.samples[sample][version] for sample,version in mc_samples.iteritems()}
    samples = {}
    if not self.is_flav:
      for entry in entries:
        samples[entry[0]] = [ _samples[entry[1]] ]
    else:
      mc_samples = [ name for name in names for _,names in samples.iteritems()]
      for entry in self.entries:
        samples[entry[0]] = [ [ entry[1] ], mc_samples ]
    return samples

def P(names):
    for name,hnames in names.iteritems():
      for s in hnames:
        pass
#        print name,s

def main():
  entries = [
    ['z+jets','zjets',R.kBlue],
    ['Misid. leptons','fake',R.kGreen],
    ['Single top','stop',R.kRed],
    ['Diboson','diboson',R.kYellow],
    ['t#bar{t}','tt',R.kWhite],
  ]

  draw_opts = OPts().drawopts
  texts = {
    'ATLAS Label' : ['#font[72]{ATLAS}',0.2,0.844,1,0.05*1.58],
    'Status'      : ['#font[42]{Internal}',0.37, 0.844,1,0.05*1.58],
    'COME & LUMI' : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',0.2, 0.77, 1, 0.0375*1.58],
    'Selection'   : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',0.2, 0.7, 1, 0.03*1.58],
  }

  dt_fmt = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_fmt = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_var_fmt = '{var:}/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt_{var:}' 

  printer = MakeControlPlots('../input/test.root','../plots/','../data/Run_CalJet_test.json')
  printer.SetupDraw(entries,True,True,False)
  printer.DrawPlots(draw_opts,texts,dt_fmt,mc_fmt,mc_var_fmt)

if __name__ == '__main__':
  main()
