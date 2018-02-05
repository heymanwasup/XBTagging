import os,re
from ROOT import *
class Config:
  def __init__(self):

    self.runmode = 'Trk'#TVAR1
    self.runtag = "test2"#TVAR2
    #runtag = "Mar.10.2017.Syst"#TVAR2
    self.tail = 'py6'#TVAR3
    self.nLoop = 10000
    self.onlyNominal      = False
    self.doParallel       = False
    self.makeVarList      = False
    self.is_mu_cali       = False#TVAR6
    self.is_eta_cali      = True#TVAR7
    self.is_old_inputs    = False
    
    self.is_fill_sea      = True
    self.is_fill_datapool = True
    self.is_fill_cdipool  = False
    self.is_one_wp        = False
    self.is_one_mva       = False
    self.run_hybrid       = False
    self.resampling_plots = False
    self.sf_b = {
      'Trk':[0.88,1.16],
      'Cal':[0.84,1.2],
    }
    self.sf_l = {
      'Trk':[0,2.5],
      'Cal':[0,2.3],
    }
    
    self.wt_scale = {
      'up':[re.compile(r'.*stop_Wt.*'),1.+3.9/71.7],
      'do':[re.compile(r'.*stop_Wt.*'),1.-3.9/71.7],
    }
    
    self.diboson_scale = { # TODO norm. factor
      'up':[re.compile(r'.*diboson.*'),1.5],
      'do':[re.compile(r'.*diboson.*'),0.5],
      #'up':[re.compile(r'.*_Pw_.*'),1.5],
      #'do':[re.compile(r'.*_Pw_.*'),0.5],
    }
    
    self.zjets_scale = { # TODO norm. factor
      #'up':[re.compile(r'(.*Zee.*)|(.*Zmm.*)|(.*Ztt.*)'),1.2],
      #'do':[re.compile(r'(.*Zee.*)|(.*Zmm.*)|(.*Ztt.*)'),0.8],
      'up':[re.compile(r'.*MadZ.*'),1.2],
      'do':[re.compile(r'.*MadZ.*'),0.8],
    }
    
    self.lumi_scale = {
      'up':[re.compile(r'.*'),1.+0.032],
      'do':[re.compile(r'.*'),1.-0.032],
    }
     
    self.fake_scale = {
      'up':[re.compile(r'.*fake.*'),1.+0.5],
      'do':[re.compile(r'.*fake.*'),1.-0.5],
    }
    self.mva_wps = ['{0:}'.format(key*5) for key in range(12,21)] # range(12,21)
    self.wps = [ '60', '70', '77', '85' ] #b-tagging wp
    #mva_wps = ['100']
    self.mcsf = 1.
    self.xbinr = { 
              'Trk':[0,10,20,30,60,100,250],#,300], 
              'Cal':[0,20,30,60,90,140,200,300],
    }
    self.mu_bins = ['_XMu']
    # nominal samples
    self.MCSamples = {
                  'diboson'   : ['WW_Pw','ZZ_Pw','WZ_Pw'], # ['diboson_sherpa'],    #   ['diboson_sherpa'],
                  'z+jets'    :  ['Zee','Zmm','Ztt'], # ['MadZee','MadZmumu','MadZtautau'],  #     ['MadZee','MadZmumu','MadZtautau'],
                  'stop'      :          ['stop_s','stop_t','stop_Wt'],
                  'fake'      :          ['fake'],
    }
    
    # mc mis-modelling-configuration : for hybrid
    self.tt_cfg = {
      'ttbarFragmentation' : ['nominal','PowHW'],
      'ttbarHardScatter'   : ['aMcAtNloHW','PowHW'],
      'ttbarRadiation'     : ['radhi', 'radlo'],
      'ttbarPDFRW'     : ['aMcAtNloHW', 'PDFRW'],
    }
    
    # mc mis-modelling
    self.ttbarModelling_py6 = [
                      ['ttbarFragmentation',       ['ttbar'],             ['ttbarPowHW_UEEE5'] ] ,
                      ['ttbarHardScatter',         ['ttbaraMcAtNloHW'],   ['ttbarPowHW_UEEE5'] ] ,
                      ['ttbarRadiation',           ['ttbar_radhi'],       ['ttbar_radlo']    ] ,
                      ['ttbarPDFRW',               ['ttbaraMcAtNloHW'],   ['ttbaraMcAtNloHW_PDFRW']   ],#PDFRW
    ]
    
    
    
    self.ttbarModelling_py8 = [
                      ['ttbarHardScatter',       ['ttbarPy8'],             ['ttbaraMcAtNloPy8'] ] ,
                      ['ttbarFragmentation',         ['ttbarPy8'],   ['ttbarPowHW_H7UE'] ] ,
                      ['ttbarRadiation',           ['ttbarPy8_radhi'],       ['ttbarPy8_radlo']    ] ,
    ]
    
    self.stopModelling = [
                     ['StopDRDS',['stop_Wt'],['stop_Wt_DS'] ] ,
                     ['StopRadiation',['stop_Wt_RadHi'],['stop_Wt_RadLo'] ] ,
                     ['StopFragmentation',['stop_Wt'],['stop_Wt_PowHer'] ] ,
                     ['StopHardScatter',['stop_Wt_PowHer'],['stop_Wt_McAtNlo']],
    ]
    self.zjetsModelling = [
                      ['zjetsModelling',['MadZee','MadZmumu','MadZtautau'],['Zee','Zmumu','Ztautau']],
    ]


  def FixParameters(self):
    self.path = r'{0:}/input.root'.format(self.runmode.lower())#TVAR4
    
    self.ntB_scale = {  
      'up':[re.compile(r'.*SysNominal/(?!ttbar).*PbP.*$'),self.sf_b[self.runmode][0]],
      'do':[re.compile(r'.*SysNominal/(?!ttbar).*PbP.*$'),self.sf_b[self.runmode][1]],
    }

    self.mistag_scale = {
      'up':[re.compile(r'.*PjP.*'),self.sf_l[self.runmode][0]],
      'do':[re.compile(r'.*PjP.*'),self.sf_l[self.runmode][1]],
    }

    self.scales = {
    #  'norm ntB':self.ntB_scale,
      'norm wt':self.wt_scale,
      'norm diboson':self.diboson_scale,
      'norm zjets':self.zjets_scale,
      'Luminosity':self.lumi_scale,
      'FakeScale':self.fake_scale,
    #  'mis tag rate':self.mistag_scale,

    }
    if self.is_one_wp:
      self.wps = [ '85']

    if self.is_one_mva:
      if self.runmode == 'Cal':
        self.mva_wps = ['90']
      elif self.runmode == 'Trk':
        self.mva_wps = ['90']
      else:
        print 'ERROR: check if runmod = Cal/Trk'
        exit(0)



    self.data = TFile(self.path)
    self.mc = TFile(self.path)

    if self.is_mu_cali:
      self.mu_bins = ['_0_18Mu','_18_25Mu','_25_50Mu']
      self.xbinr = { 
                'Trk':[0,20,60,300], 
                'Cal':[0,20,60,300], 
      }

    if self.is_old_inputs:
      self.eta_bins = ['']
    else:
      self.eta_bins = ['_xEta']
      if self.is_eta_cali:
        self.eta_bins = ['_0_7Eta','_7_15Eta','_15Eta']
        self.xbinr = {
                  'Cal':[0,30,60,90,140,200], 
                  'Trk':[0,30,60,100,250], 
        }

    self.xbins = self.xbinr[self.runmode]
    self.nbins = len(self.xbins)-1

    if 'py8' in self.tail.lower():
      self.ttbarModelling = self.ttbarModelling_py8
      self.MCSamples.update({'tt':['ttbarPy8']})
    else:
      self.ttbarModelling = self.ttbarModelling_py6
      self.MCSamples.update({'tt':['ttbar']})

    tempName = "SysNominal/{1:}_TP_1ptag2jet_MVA85_XMu_em_xEta_PxT85{0:}JetPt".format(self.runmode,self.MCSamples['tt'][0])
    print tempName
    print self.mc
    self.htemp = (self.mc.Get(tempName)).Clone()

    self.htemp.Reset()
    self.SysModelling = {'tt':self.ttbarModelling,'stop':self.stopModelling,'z+jets':self.zjetsModelling}

