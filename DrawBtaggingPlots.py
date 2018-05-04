import toolkit
import ROOT as R
from AtlasStyle import *
import math
from array import array

R.gROOT.SetBatch(True)

def GetSumOfErrors(errors):
    sum_of_err = [0.]*len(errors[0])
    for err in errors:
        for n in range(len(err)):
            sum_of_err[n] = math.sqrt(sum_of_err[n]**2 + err[n]**2)
    return sum_of_err

class BtaggingPlots(object):
    def __init__(self):
        self.scale_x = 1.05


    def DrawSFcomparison(self,input_json_A,input_json_B,cfg):
        data_A = self.ExtractData_SF(input_json_A,0.05)
        data_B = self.ExtractData_SF(input_json_B)

        objects = self.GetObjects_SFcomparison(data_A,data_B,cfg)
        self.DrawObjects_SFcomparison(objects,cfg)
   
    def GetObjects_SFcomparison(self,data_A,data_B,cfg):                
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
    
        legend = self.GetLegend_SFcomparison(objects_A['central'],objects_A['errband'],objects_B['central'],objects_B['errband'],cfg)
        
        objects = {
            'canvas':objects_B['canvas'],
            'central_A':objects_A['central'],
            'central_B':objects_B['central'],
            'errband':errband,
            'legend':legend,

        }
        return objects
   
    def DrawObjects_SFcomparison(self,objects,cfg):
        objects['canvas'].Draw()
        
        objects['errband'].Draw('A2')
        self.DecorateErrBand_SFcomparison(objects['errband'],cfg)
        objects['central_A'].Draw('PZSAME')
        objects['central_B'].Draw('PZSAME')

        
        objects['legend'].Draw()

        for text in cfg['texts']:
            self.DrawText(*text)

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/{1:}.{2:}'.format(cfg['output_path'],cfg['name'],fmt))
    
    def DecorateErrBand_SFcomparison(self,errband,cfg):
        xax = errband.GetXaxis()
        xax.SetRangeUser(0,cfg['xBins'][-1]*self.scale_x)
        xax.SetTitle(cfg['xTitle'])

        yax = errband.GetYaxis()
        yax.SetNdivisions(507)
        yax.SetRangeUser(*cfg['yRange'])
        yax.SetTitle(cfg['yTitle'])      

    def GetLegend_SFcomparison(self,central_A,errband_A,central_B,errband_B,cfg):
        legend = R.TLegend(*cfg['LegendPosition'])
        cA = '{0:} {1:}'.format(cfg['nameA'],cfg['errbarName'])
        eA = '{0:} {1:}'.format(cfg['nameA'],cfg['errbandName'])
        cB = '{0:} {1:}'.format(cfg['nameB'],cfg['errbarName'])
        eB = '{0:} {1:}'.format(cfg['nameB'],cfg['errbandName'])
        legend.AddEntry(central_A,cA,'lep')
        legend.AddEntry(errband_A,eA,'f')
        
        legend.AddEntry(central_B,cB,'lep')
        legend.AddEntry(errband_B,eB,'f')
        
        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        return legend    
    
    def DrawSF(self,input_json,cfg):
        data = self.ExtractData_SF(input_json)
        objects = self.GetObjects_SF(data,cfg)
        self.DrawObjects_SF(objects,cfg)
    
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

    def DrawObjects_SF(self,objects,cfg):
        objects['canvas'].Draw()
        objects['errband'].Draw('A2')
        objects['central'].Draw('PZSAME')
        objects['legend'].Draw()
        objects['canvas'].Update()

        for text in cfg['texts']:
            self.DrawText(*text)

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/{1:}.{2:}'.format(cfg['output_path'],cfg['name'],fmt))

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

    def DrawEff(self,input_json,cfg):
        data = self.ExtractData_Eff(input_json)
        objects = self.GetObjects_Eff(data,cfg)
        self.DrawObjects_Eff(objects,cfg)
    
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

    def DrawObjects_Eff(self,objects,cfg):
        objects['canvas'].Draw()
        objects['g_e_mc'].Draw('APZ')
        objects['g_e_dt'].Draw('PZSAME')

        objects['legend'].Draw()
        
        for text in cfg['texts']:
            self.DrawText(*text)        

        for fmt in cfg['fmt']:
            objects['canvas'].Print('{0:}/{1:}.{2:}'.format(cfg['output_path'],cfg['name'],fmt))

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

def test_sf():
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
        'output_path':'.',
    }

    drawer = BtaggingPlots()
    input_json = '/Users/cheng/Work/Btagging/workspace/new_btagging_framework/output/test/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
    drawer.DrawSF(input_json,cfg)

def test_eff():
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
        'output_path':'.',
    }

    input_json = '/Users/cheng/Work/Btagging/workspace/new_btagging_framework/output/test/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
    drawer = BtaggingPlots()
    drawer.DrawEff(input_json,cfg)
def test_comparison():
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
        'output_path':'.',
    }
  

    drawer = BtaggingPlots()
    input_json = '/Users/cheng/Work/Btagging/workspace/new_btagging_framework/output/test/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
    drawer.DrawSFcomparison(input_json,input_json,cfg)

if __name__ == '__main__':
    #test_sf()
    #test_eff()
    test_comparison()









