
import copy
import itertools
import ROOT as R
import toolkit
import DrawBox


def DrawProbeJetPt(name,input_file,output_path,cfg_path,is_modelling,is_variation):
  


plotConfig = 'data/PlotInfo_default.json'
fmt = ['png']

entries_sample = [
    ['z+jets','zjets',R.kBlue],
    ['Misid. leptons','fake',R.kGreen],
    ['Single top','stop',R.kRed],
    ['Diboson','diboson',R.kYellow],
    ['t#bar{t}','tt',R.kWhite],
]

entries_flav = [
    ['Light-jet','L',R.kRed],
    ['Charm-jet','C',R.kBlue],
    ['B-jet','B',R.kWhite],
]

canvasSize = [800,800]
dataName = 'Data'



def ErrBandName(is_modelling,is_variation):
  res = 'MC stat.'
  if is_modelling:
    res += ' + modellings'
  if is_variation:
    res += ' + syst. unc.'
  return res

def DrawProbeJetPt(name,input_file,output_path,cfg_path,is_modelling,is_variation):  
  errBandName = ErrBandName(is_modelling, is_variation)

  config_user = {
    'Config_general':{
      'xRange':[0,600],
      'yRange':None,
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],
      'unit':10.,
      'LogScale':True,
      'fmt':fmt,
      'canvasSize':canvasSize,
      'errBandName':errBandName,
      'dataName':dataName,
    }
  }

  config_default = toolkit.json_load(plotConfig)
  config = toolkit.MergeDict_recurssive(config_default, config_user)


  texts = {
    'ATLAS Label' : ['#font[72]{ATLAS}',0.2,0.844,1,0.05*1.58],
    'Status'      : ['#font[42]{Internal}',0.37, 0.844,1,0.05*1.58],
    'COME & LUMI' : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',0.2, 0.77, 1, 0.0375*1.58],
    'Selection'   : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',0.2, 0.7, 1, 0.03*1.58],
  }

  dt_fmt_sample = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_fmt_sample = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_var_fmt_sample = '{variation:}/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt_{variation:}'  


  dt_fmt_flav = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_fmt_flav = 'SysNominal/{sample:}_{flav:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_var_fmt_flav = '{variation:}/{sample:}_{flav:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt_{variation:}' 





  args_sample = {
    'pic_name':'ProbeJetPt_Sample',
    'entries':entries_sample,
    'dt_fmt':dt_fmt_sample,
    'mc_fmt':mc_fmt_sample,
    'mc_var_fmt':mc_var_fmt_sample,
    'texts':texts,
    'draw_opts':config,
    'is_flav':False,
  }

  args_flav = {
    'pic_name':'ProbeJetPt_Flav',
    'entries':entries_flav,
    'dt_fmt':dt_fmt_flav,
    'mc_fmt':mc_fmt_flav,
    'mc_var_fmt':mc_var_fmt_flav,
    'texts':texts,
    'draw_opts':config,
    'is_flav':True,
  }
  
  printer = DrawBox.MakeControlPlots(name,input_file,output_path,cfg_path,is_modelling,is_variation)
  
  
  printer.DrawPlots(**args_sample)
  printer.DrawPlots(**args_flav)

def main():
  input_file = './input/test.root'
  output_path = './plots/'
  cfg_path = './data/Run_CalJet_test.json'
  is_modelling = False
  is_variation = True
  name = 'test'
  DrawProbeJetPt(name,input_file,output_path,cfg_path,is_modelling,is_variation)

  
if __name__ == '__main__':
  main()
