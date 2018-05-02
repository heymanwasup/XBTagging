
import copy,itertools

import ROOT as R
import toolkit
import tools


import DrawPlots_new as DB

from drawopts import OPts




def DrawProbeJetPt():

  
  input_file = '../input/test.root'
  output_path = '../plots/'
  cfg_path = '../data/Run_CalJet_test.json'
  is_modelling = True
  is_variation = True

  printer = DB.MakeControlPlots(input_file,output_path,cfg_path,is_modelling,is_variation)

  texts = {
    'ATLAS Label' : ['#font[72]{ATLAS}',0.2,0.844,1,0.05*1.58],
    'Status'      : ['#font[42]{Internal}',0.37, 0.844,1,0.05*1.58],
    'COME & LUMI' : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',0.2, 0.77, 1, 0.0375*1.58],
    'Selection'   : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',0.2, 0.7, 1, 0.03*1.58],
  }
  
  draw_opts = OPts().drawopts

  entries_sample = [
    ['z+jets','zjets',R.kBlue],
    ['Misid. leptons','fake',R.kGreen],
    ['Single top','stop',R.kRed],
    ['Diboson','diboson',R.kYellow],
    ['t#bar{t}','tt',R.kWhite],
  ]

  dt_fmt_sample = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_fmt_sample = 'SysNominal/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt' 
  mc_var_fmt_sample = '{variation:}/{sample:}_TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt_{variation:}'  

  entries_flav = [
    ['Light-jet','L',R.kRed],
    ['Charm-jet','C',R.kBlue],
    ['B-jet','B',R.kWhite],
  ]  

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
    'draw_opts':draw_opts,
    'is_flav':False,
  }

  args_flav = {
    'pic_name':'ProbeJetPt_Flav',
    'entries':entries_flav,
    'dt_fmt':dt_fmt_flav,
    'mc_fmt':mc_fmt_flav,
    'mc_var_fmt':mc_var_fmt_flav,
    'texts':texts,
    'draw_opts':draw_opts,
    'is_flav':True,
  }

  printer.DrawPlots(**args_sample)
  printer.DrawPlots(**args_flav)


def main():
  DrawProbeJetPt()
  #DrawProbeFlavourComb()

if __name__ == '__main__':
  main()
