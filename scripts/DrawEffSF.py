import toolkit
import ROOT as R
from AtlasStyle import *
import math
import DrawBox
from array import array


R.gROOT.SetBatch(True)


def test_sf(project_name,input_json,output_path):
    texts = [
        ['#font[72]{ATLAS}',0.5, 0.85,],
        ['#font[42]{Internal}', 0.664,0.85],
        ['#font[42]{MV2c10, #varepsilon_{b} = 85%, single cut}',0.2,0.30,0.03],
        ['#font[42]{T&P Method}',0.2,0.37,0.03],
        ['#font[42]{Anti-k_{t} R=0.4 calorimeter jets}',0.2,0.23,0.03],
        ['#font[42]{#sqrt{s} = 13 TeV, 79.9 fb^{-1}}',0.5,0.78,0.04],
    ]



    cfg = {
        'errbarName':'Stat. Uncertainty',
        'errbandName':'Total Uncertainty',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'#varepsilon_{b}^{data} / #varepsilon_{b}^{MC}',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.6,0.2,0.93,0.35],
        'yRange':[0.65,1.15],
        'texts':texts,
        'fmt':['png'],
        'name':'sf_test',
    }

    output_path = '{0:}/{1:}/plots_EffSF'.format(output_path,project_name)
    drawer = DrawBox.BtaggingPlots(output_path)
    drawer.DrawSF(input_json,cfg)

def test_eff(project_name,input_json,output_path):
    texts = [
        ['#font[72]{ATLAS}',0.5, 0.85,],
        ['#font[42]{Internal}', 0.664,0.85],
        ['#font[42]{MV2c10, #varepsilon_{b} = 85%, single cut}',0.2,0.30,0.03],
        ['#font[42]{T&P Method}',0.2,0.37,0.03],
        ['#font[42]{Anti-k_{t} R=0.4 calorimeter jets}',0.2,0.23,0.03],
        ['#font[42]{#sqrt{s} = 13 TeV, 79.9 fb^{-1}}',0.5,0.78,0.04],
    ]

    cfg = {
        'effDataName':'Data',
        'effMCName':'MC',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'b-jet tagging efficiency',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.6,0.2,0.93,0.35],
        'yRange':[0.1,1.1],
        'texts':texts,
        'fmt':['png'],
        'name':'eff_test',
    }
    
    output_path = '{0:}/{1:}/plots_EffSF'.format(output_path,project_name)
    drawer = DrawBox.BtaggingPlots(output_path)
    drawer.DrawEff(input_json,cfg)

def test_comparison(project_name,input_json,output_path):
    texts = [
        ['#font[72]{ATLAS}',0.2, 0.85,],
        ['#font[42]{Internal}', 0.2 + 0.164,0.85],
        ['#font[42]{MV2c10, #varepsilon_{b} = 85%, single cut}',0.2,0.30,0.03],
        ['#font[42]{Method A v.s Method B (just for test)}',0.2,0.37,0.03],
        ['#font[42]{Anti-k_{t} R=0.4 calorimeter jets}',0.2,0.23,0.03],
        ['#font[42]{#sqrt{s} = 13 TeV, 79.9 fb^{-1}}',0.2,0.78,0.04],
    ]

    cfg = {
        'nameA':'Method A',
        'nameB':'Method B',
        'errbarName':'Stat.',
        'errbandName':'Total',
        'xTitle':'Jet p_{T} [GeV]',
        'yTitle':'#varepsilon_{b}^{data} / #varepsilon_{b}^{MC}',
        'xBins':[20,30,40,60,85,110,140,175,250,600],
        'LegendPosition':[0.62,0.7,0.95,0.9],
        'yRange':[0.55,1.35],
        'texts':texts,
        'fmt':['png'],
        'name':'com_test',
    }
  
    output_path = '{0:}/{1:}/plots_EffSF'.format(output_path,project_name)
    drawer = DrawBox.BtaggingPlots(output_path)
    drawer.DrawSFcomparison(input_json,input_json,cfg)

if __name__ == '__main__':
    input_json  = './output/test/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
    project_name = 'test'
    output_path = 'output'
    test_sf(project_name,input_json,output_path)
    test_eff(project_name,input_json,output_path)
    test_comparison(project_name,input_json,output_path)

