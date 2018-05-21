
import copy
import itertools
import ROOT as R
import toolkit
import DrawBox





def MakeControlPlots(input_file, output_path, cfg_path):


  entries = {}
  entries['sample'] = [
        ['t#bar{t}','tt',R.kWhite],
        ['Diboson','diboson',R.kYellow],
        ['Single top','stop',R.kRed],
        ['Misid. leptons','fake',R.kGreen],
        ['z+jets','zjets',R.kBlue],
  ]
    
  entries['flav'] = [
        ['B-jet','B',R.kWhite],
        ['Charm-jet','C',R.kBlue],
        ['Light-jet','L',R.kRed],        
  ]

  entries['event_flav'] = [
    ['bb','bb',R.kWhite],
    ['bc','bc',R.kBlue],
    ['bl','bl',R.kRed],
    ['cc','cc',R.kOrange],
    ['cl','cl',R.kGreen],
    ['ll','ll',R.kYellow],
  ]

  config_pt = {
    'Config_general':{
      'xRange':[0,600],
      'yRange':None,
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],
      'unit':10.,
      'LogScale':True,
    },
  }

  config_eta = {
    'Config_general':{
      'xRange':[-3.,3.],
      'yRange':None,
      'xBins':[-3+0.5*n for n in range(13)],
      'unit':0.5,
      'LogScale':False,
    },
    'Hist_ratio':{'Xaxis':{ 'Title':['#eta(jet)'] }},
    'Hist_mcStack':{'Yaxis':{ 'Title':['Jets / 0.5'] }},
  }

  config_mv2c10 = {
    'Config_general':{
      'xRange':None,
      'yRange':None,
      'xBins':None,
      'unit':0.1,
      'LogScale':True,
    },
    'Hist_ratio':{'Xaxis': {'Title':['MV2c10'] }},
    'Hist_mcStack':{'Yaxis':{ 'Title':['Jets / 0.1'] }},
  }

  config_bdt = {
    'Config_general':{
      'xRange':[-0.65,0.4],
      'yRange':None,
      'xBins':[-0.65+n*0.05 for n in range(22)],
      'unit':0.1,
      'LogScale':False,
    },
    'Hist_ratio':{'Xaxis':{ 'Title':['D_{bb}^{T&P}'] }},
    'Hist_mcStack':{'Yaxis':{ 'Title':['Events / 0.1'] }},
  }

  config_mll = {
    'Config_general':{
      'xRange':[0.,500.],
      'yRange':None,
      'xBins':[20.*n for n in range(26)],
      'unit':20.,
      'LogScale':False,
    },
    'Hist_ratio':{'Xaxis':{'Title': ['m_{ll} [GeV]'] }},
    'Hist_mcStack':{'Yaxis':{'Title': ['Events / 20 GeV'] }},  
  }

  texts = {
    'ATLAS Label' : ['#font[72]{ATLAS}',0.2,0.844,1,0.05*1.58],
    'Status'      : ['#font[42]{Internal}',0.37, 0.844,1,0.05*1.58],
    'COME & LUMI' : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',0.2, 0.77, 1, 0.0375*1.58],
    'Selection'   : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',0.2, 0.7, 1, 0.03*1.58],
  }

  fmts_sample = {
    'dt_fmt':'SysNominal/{sample:}_{name:}',
    'mc_fmt':'SysNominal/{sample:}_{name:}',
    'mc_var_fmt':'{variation:}/{sample:}_{name:}_{variation:}',  
  }

  fmts_flav = {
    'dt_fmt':'SysNominal/{sample:}_{name:}',
    'mc_fmt':'SysNominal/{sample:}_{flav:}_{name:}',
    'mc_var_fmt':'{variation:}/{sample:}_{flav:}_{name:}_{variation:}',  
  }

  probejet_pt_histname = 'TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetPt'
  probejet_eta_histname = 'TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetEta'
  probejet_mv2c10_histname = 'TP_1ptag2jet_MVA100_XMu_em_xEta_PxT85CalJetMV2c10'
  event_bdt_histname = 'TP_1ptag2jet_MVA100_XMu_em_xEta_BDT'
  event_mll_histname = 'TP_1ptag2jet_MVA100_XMu_em_xEta_Mll'


  draw_api = DrawBox.DrawAPI(input_file, output_path, cfg_path)
  
  draw_api.Draw('probejet_pt_sample',probejet_pt_histname,config_pt, texts,fmts_sample, entries['sample'],is_flav=False)
  draw_api.Draw('probejet_pt_flav',probejet_pt_histname,config_pt,texts, fmts_flav, entries['flav'],is_flav=True)

  draw_api.Draw('probejet_eta_sample',probejet_eta_histname, config_eta, texts, fmts_sample, entries['sample'],is_flav=False)
 
  draw_api.Draw('probejet_eta_flav',probejet_eta_histname, config_eta, texts, fmts_flav, entries['flav'],is_flav=True)
  draw_api.Draw('probejet_mv2c10_sample',probejet_mv2c10_histname,config_mv2c10,texts, fmts_sample, entries['sample'],is_flav=False)
  draw_api.Draw('probejet_mv2c10_flav',probejet_mv2c10_histname,config_mv2c10,texts,fmts_flav, entries['flav'],is_flav=True)
  draw_api.Draw('bdt_sample',event_bdt_histname,config_bdt,texts, fmts_sample, entries['sample'],is_flav=False)
  draw_api.Draw('bdt_flav',event_bdt_histname,config_bdt,texts, fmts_flav, entries['event_flav'],is_flav=True)
  draw_api.Draw('mll_sample',event_mll_histname,config_mll,texts, fmts_sample, entries['sample'],is_flav=False)
  draw_api.Draw('mll_flav',event_mll_histname,config_mll,texts, fmts_flav, entries['event_flav'],is_flav=True)


def MakeBtaggingPlots(output_path,jsons):
    texts = [
        ['#font[72]{ATLAS}',0.5, 0.85,],
        ['#font[42]{Internal}', 0.664,0.85],
        ['#font[42]{MV2c10, #varepsilon_{b} = 70%, single cut}',0.2,0.30,0.03],
        ['#font[42]{T&P Method}',0.2,0.37,0.03],
        ['#font[42]{Anti-k_{t} R=0.4 calorimeter jets}',0.2,0.23,0.03],
        ['#font[42]{#sqrt{s} = 13 TeV, 36.1 fb^{-1}}',0.5,0.78,0.04],
    ]

    cfg_sf = {
        'errbarName':'Stat. Uncertainty',
        'errbandName':'Total Uncertainty',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'#varepsilon_{b}^{data} / #varepsilon_{b}^{MC}',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.6,0.2,0.93,0.35],
        'yRange':[0.65,1.15],
        'fmt':['png'],
    }
    
    cfg_eff = {
        'effDataName':'Data',
        'effMCName':'MC',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'b-jet tagging efficiency',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.6,0.2,0.93,0.35],
        'yRange':[0.1,1.1],
        'fmt':['png'],
    }    
    
    drawer = DrawBox.BtaggingPlots(output_path)
    for name,json_path in jsons.iteritems():
      drawer.DrawSF(name,json_path,cfg_sf,texts)
      drawer.DrawEff(name,json_path,cfg_eff,texts)

def MakeSFcomparisonPlots(name,output_path,jsonA,jsonB,nameA,nameB):
    texts = [
        ['#font[72]{ATLAS}',0.2, 0.85,],
        ['#font[42]{Internal}', 0.2 + 0.164,0.85],
        ['#font[42]{MV2c10, #varepsilon_{b} = 85%, single cut}',0.2,0.30,0.03],
        ['#font[42]{%s v.s %s}'%(nameA,nameB),0.2,0.37,0.03],
        ['#font[42]{Anti-k_{t} R=0.4 calorimeter jets}',0.2,0.23,0.03],
        ['#font[42]{#sqrt{s} = 13 TeV, 36.1 fb^{-1}}',0.2,0.78,0.04],
    ]

    cfg = {
        'errbarName':'Stat.',
        'errbandName':'Total',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'#varepsilon_{b}^{data} / #varepsilon_{b}^{MC}',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.62,0.7,0.95,0.9],
        'yRange':[0.55,1.35],
        'fmt':['png'],
    }
  
    drawer = DrawBox.BtaggingPlots(output_path)
    drawer.DrawSFcomparison(name,jsonA,jsonB,nameA,nameB,cfg,texts)

def main():
  input_file = './input/CalJetApr.23.2018.MV2c10.FullSys.FxiedWP.root'
  output_path = './output/CalJetApr.23.2018.MV2c10.FullSys.FxiedWP/plots/'
  cfg_path = 'data/Run_CalJet_test.json'

  name = 'test'

  output_path_btagging = '.'
  jsonA = 'output/CalJetApr.23.2018.MV2c10.FullSys.FxiedWP/json_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
  jsonB = './Demo/json_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
  nameA = '70WP'
  nameB = '85WP'

  MakeControlPlots(name, input_file, output_path, cfg_path)
  MakeBtaggingPlots(name, jsonA, output_path_btagging)
  #MakeSFcomparisonPlots(name, output_path_btagging, jsonA, jsonB, nameA, nameB)

if __name__ == '__main__':
  main()
