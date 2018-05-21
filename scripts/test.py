import ROOT as R
import math
from array import array
from copy import *
import toolkit

R.gROOT.SetBatch(1)
def Draw():
    canvas = R.TCanvas('c1','A Simple Graph Example',200,10,700,500)
    canvas.SetGrid()
    canvas.DrawFrame(0,0,2.2,12)

    x = [0.1+n*0.1 for n in range(20)]
    ymax = [10*math.sin(x[n])+0.2 for n in range(20)]
    ymin = [8*math.sin(x[n])+0.1 for n in range(20)]
    y = [9*math.sin(x[n]) for n in range(20)]

    grmin = R.TGraph(20,array('d',x),array('d',ymin))
    grmax = R.TGraph(20,array('d',x),array('d',ymax))
    gr    = R.TGraph(20,array('d',x),array('d',y))
    grshade = R.TGraph(40)
    for n in range(20):
        grshade.SetPoint(n,x[n],ymax[n])
        grshade.SetPoint(39-n,x[n],ymin[n])
    grshade.SetFillStyle(3013)
    grshade.SetFillColor(16)
    grshade.Draw('f')
    grmin.Draw('l')
    grmax.Draw('l')
    gr.SetLineColor(R.kRed)
    gr.SetLineWidth(4)
    gr.SetMarkerColor(4)
    gr.Draw('CP')
    canvas.Print('./test/test.png')

def DrawFitResults(f,ferror,x,y,e):
    
    canvas = R.TCanvas('canvas')

    dx = 0.04
    




class ExtroplateErrors(object):
    def __init__(self,xbinsIn,xbinsOut,saveDir='.'):
        self.xbinsIn = copy(xbinsIn)
        self.xbinsOut = copy(xbinsOut)
        self.savePath = '{0:}/Extrapolate'.format(saveDir)
        self.hist = R.TH1F('hist','hist',len(xbinsIn)-1,array('d',xbinsIn))


    def PerformFit(self,name,central,error,systs,isPlot=False):
        
        fun_central = self.__fitCentral(central,error)

        fun_systs = {}
        for sys_name,syst in systs.iteritems():            
            fun_systs[sys_name] = self.__fitSyst(sys_name,syst)
        out_central = self.__getOutBins(fun_central)
        out_systs = {}
        for key,fun in fun_systs.iteritems():
            out_systs[key] = self.__getOutBins(fun)
            out_systs[key].insert(0,0)
        if isPlot:
            saveDir = '{0:}/{1:}'.format(self.savePath,name)
            toolkit.mkdir(saveDir)
            for sys_name in systs.keys():
                fun_syst = fun_systs[sys_name]
                syst = systs[sys_name]
                
                self.__makePlot(saveDir,sys_name,central,error,syst,fun_central,fun_syst)
        out_central.insert(0, 0.)
        return out_central,out_systs        


    def __fitCentral(self,central,error):
        self.__fillHist(central,error)
        fun  = self.__getFunction('central')
        #hist = self.hist.Clone()
        self.hist.Fit(fun,'+')
        fun_central = self.hist.GetFunction('central')
        return fun_central

    def __fillHist(self,value,error=None):

        #self.hist.Reset()
        if error == None:
            error = [0.01] * len(value)
        for n in range(len(self.xbinsIn)-1):
            self.hist.SetBinContent(n+1,value[n])
            self.hist.SetBinError(n+1,error[n])

    def __getFunction(self,name):
        f = R.TF1(name,'[0]+[1]*x+[2]*x*x')
        return f
    
    def __getFunctionSyst(self,name):
        return R.TF1(name,'[0]+[1]*x+[2]*x*2')

    def __fitSyst(self,name,syst):
        fun  = self.__getFunctionSyst(name)

        self.__fillHist(syst)
        #hist = self.hist.Clone()
        self.hist.Fit(fun,'+')
        fun_syst = self.hist.GetFunction(name)

        return fun_syst

    
    def __getOutBins(self,fun):
        res = []
        for n in range(len(self.xbinsOut)-1):
            x = (xbinsOut[n]+xbinsOut[n+1])*0.5
            res.append(fun(x))
        return res

    def __makePlot(self,saveDir,sys_name,central,error,syst,fun_central,fun_syst):
        fun_central.SetRange(0,390)
        gr_band,gr_min,gr_max = self.__getSystBand(fun_central,fun_syst)
        gr_data = self.__getDataGraph(central,syst)
        legend = self.__getLegend(fun_central,gr_band,gr_data,sys_name)
        canvas = R.TCanvas('canvas','canvas',800,600)
        canvas.SetTitle(sys_name)
        gr_band.SetTitle(sys_name)
        draw_objects = {
            'canvas' : canvas,
            'fun_central' : fun_central,
            'gr_band' : gr_band,
            'gr_min' : gr_min,
            'gr_max' : gr_max,
            'gr_data' : gr_data,
            'legend' : legend,
        }
        plot_name = '{0:}/{1:}.png'.format(saveDir,sys_name)

        self.__drawPlot(plot_name,draw_objects)

    def __getSystBand(canvas,fun_central,fun_syst):
        gr = R.TGraph(80)
        gmin = R.TGraph(40)
        gmax = R.TGraph(40)
        x = [10*n for n in range(40)]
        for n in range(40):
            
            y1 = fun_central(x[n]) + fun_syst(x[n])
            y2 = fun_central(x[n]) - fun_syst(x[n])


            #y1 = n
            #y2 = n+1
            ymin = min(y1, y2)
            ymax = max(y1, y2)
            gmin.SetPoint(n,x[n],ymin)
            gmax.SetPoint(n,x[n],ymax)
            gr.SetPoint(n,x[n],max(y1,y2))
            gr.SetPoint(79-n,x[n],min(y1,y2))
        xax = gr.GetXaxis()
        #xax.SetRangeUser(0,600)
        yax = gr.GetYaxis()
        yax.SetRangeUser(0.8,1.1)
        #gr.SetLineColor(R.kYellow)
        gr.SetFillColor(16)
        gr.SetLineColor(R.kBlue)
        gr.SetFillStyle(3013)
        return gr,gmin,gmax


    def __getDataGraph(self,central,error):
        x, ex = self.__getXPosition(self.xbinsIn)
        y, ey =array('d', central), array('d', error)
        graph = R.TGraphErrors( len(x), x, y, ex, ey )
        yax = graph.GetYaxis()
        yax.SetRangeUser(-5,5)
        return graph
        
    def __getXPosition(self,xbins):
        x = []
        ex = []
        for n in range(len(xbins)-1):
            x.append((xbins[n]+xbins[n+1])/2.)
            ex.append((xbins[n+1]-xbins[n])/1.995)
        return array('d',x), array ('d',ex)

    def __getLegend(self,fun_central,gr_band,gr_data,sys_name):
        legend = R.TLegend(0.1,0.1,0.4,0.3)
        legend.AddEntry(fun_central,'Fitted SF','l')
        legend.AddEntry(gr_band,'Fitted Syst','f')
        legend.AddEntry(gr_data,'SF with Syst','lep')
        return legend

    def __drawPlot(self,name,objects):
        objects['canvas'].Clear()
        objects['canvas'].Draw()
        
        objects['gr_band'].Draw()
        #objects['gr_min'].Draw('l')
        #objects['gr_max'].Draw('l')

        objects['gr_data'].Draw('PZSAME')
        objects['fun_central'].Draw('lsame')
        objects['legend'].Draw()

        objects['canvas'].Print(name)




def GetSystsList(mc16a,mc16c,r20):
    dt_a = toolkit.json_load(mc16a)
    dt_c = toolkit.json_load(mc16c)
    dt_r20 = toolkit.json_load(r20)

    new_dt_a = deepcopy(dt_a)
    new_dt_c = deepcopy(dt_c)

    keys_a = set(dt_a['sf'].keys())
    keys_c = set(dt_c['sf'].keys())
    keys_r20 = set(dt_r20['sf'].keys())

    c_a = keys_a - keys_c
    a_r20 = keys_r20 - keys_a
    a_r20 = a_r20 - set(['SysJvtEfficiency'])
    print a_r20
    print c_a

    xbinsIn = [20,30,60,90,140,200,300]
    xbinsOut = [20,30,40,60,85,110,140,175,250,600]
    central = dt_r20['sf']['nominal']
    error = dt_r20['sf']['mc stats']
    
    extroplator = ExtroplateErrors(xbinsIn, xbinsOut)
    
    systs = {}
    for entry in a_r20:
        systs[entry] = dt_r20['sf'][entry][1:]
    central_new_a_r20,systs_new_a_r20 =  extroplator.PerformFit('test1',central[1:], error[1:], systs,True)

    systs = {}
    for entry in c_a:
        systs[entry] = dt_r20['sf'][entry][1:]
    central_new_c_a,systs_new_c_a =  extroplator.PerformFit('test2',central[1:], error[1:], systs,True)

    for entry in a_r20:
        new_dt_a['sf'][entry] = systs_new_a_r20[entry]
        new_dt_c['sf'][entry] = systs_new_a_r20[entry]
    
    for entry in c_a:
        new_dt_c['sf'][entry] = systs_new_c_a[entry]
    with open('mc16a_extraplote.json','w') as fa,open('mc16c_extraplote.json','w') as fc:
        toolkit.DumpToJson(new_dt_a,fa)
        toolkit.DumpToJson(new_dt_c,fc)

if __name__ == '__main__':
    mc16a = './output/CalJetMay.13.MC16a.Full/jsons_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
    mc16c = './output/CalJetMay.13.MC16c.Full/jsons_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
    r20 = './output/CalJetDec.01.AddStopNlo/jsons_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
    xbinsIn = [20,30,60,90,140,200,300]
    xbinsOut = [20,30,40,60,85,110,140,175,250,600]
    GetSystsList(mc16a, mc16c, r20)




    sf = [0.9,0.95,0.9,0.98,1.03,1.02]
    er = [0.1,0.04,0.03,0.03,0.09,0.1]

    #systs = {'testSyst':[0.04,0.02,0.01,0.01,0.01,0.02]}
    #extroplator = ExtroplateErrors(xbinsIn, xbinsOut)
    #c,e =  extroplator.PerformFit('test',sf, er, systs,True)

    #Draw()


