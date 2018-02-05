class DataConfig(object):
  def __init__(self):
    self.Samples()
    self.Modellings()
    self.Scales()
    self.HistFormats()
    self.Categories()
    self.Binnings()

  def Scales(self):
    self.scales = {}
    self.scales['ntBCal'] = {
      'samples' : '(?!tt)',
      'keys'    : {'tp':'PbP','jet':'Cal*'},
      'scale'   : [0.84,1.2], 
    }

    self.scales['ntBTrk'] = {
      'samples' : '(?!tt)',
      'keys'    : {'tp':'PbP','jet':'Trk*'},
      'scale'   : [0.84,1.2], 
    }

    self.scales['mistagTrk'] = {
      'keys'    : {'tp':'PjP','jet':'Trk*'},
      'scale'   : [0,2.5], 
    }

    self.scales['mistagCal'] = {
      'keys'    : {'tp':'PjP','jet':'Cal*'},
      'scale'   : [0,2.3], 
    }

    self.scales['WtScale'] = {
      'samples' : 'stop',
      'keys'    : {'sample':'*Wt*'},
      'scale'   : [0.5,1.5],
    }

    self.scales['dibosonScale'] = {
      'samples' : 'diboson',
      'scale'   : [0.5,1.5],
    }
    
    self.scales['zjetsScale'] = {
      'samples' : 'zjets',
      'scale'   : [0.5,1.5],
    }
    
    self.scales['fakeScale'] = {
      'samples' : 'fake',
      'scale'   : [0.5,1.5],
    }

    self.scales['lumiScale'] = {
      'samples' : '*',
      'scale'   : [1.032,9.968],
    }
  
  def Binnings(self):
    self.binnings = {}
    self.binnings['CalOld'] = [0,20,30,60,90,140,200,300]
    self.binnings['CalNew'] = [0,20,30,40,60,85,110,140,175,250,600]
    self.binnings['CalEta'] = [0,30,60,90,140,200] 
    self.binnings['TrkOld'] = [0,10,20,30,60,100,250] 
    self.binnings['TrkEta'] = [0,30,60,100,250] 
    self.binnings['Mu']     = [0,20,60,300]
  
  def HistFormats(self):
    self.format = {}
    r21a1_nominal = {
      'hist' : '{var:}/{sample:}_TP_1ptag2jet_{mva:}_{mu:}_em_{eta:}_{tp:}{wp:}{jet:}Pt',
      'var'  : 'SysNominal',
    }
    r21a1_variation = {
      'hist' : '{var:}/{sample:}_TP_1ptag2jet_{mva:}_{mu:}_em_{eta:}_{tp:}{wp:}{jet:}Pt_{var:}', 
      'var'  : r'_*1*up$|_*1*down$',
    }
    r21a1 = {
      'nominal'   : r21a1_nominal,
      'variation' : r21a1_variation,
    }

    self.format['r21a1'] = r21a1

  def Categories(self):  
    self.cats = {}
    self.cats['ptCalib']  = {'mu' : ['XMu'], 'eta' : ['xEta'],}
    self.cats['muCalib']  = {'mu' : ['_0_18Mu','_18_25Mu','_25_50Mu'], 'eta' : ['xEta'], }
    self.cats['etaCalib'] = {'mu' : ['XMu'], 'eta' : ['_0_7Eta','_7_15Eta','_15Eta'], }
    
  def Samples(self):
    self.samples    = {}

    tt = {}
    tt['py6']             = ['ttbar']
    tt['py6_PDFRW']       = ['ttbaraMcAtNloHW_PDFRW']
    tt['py6_PowHW']       = ['ttbarPowHW_UEEE5'] 
    tt['py6_aMcAtNloHW']  = ['ttbaraMcAtNloHW'] 
    tt['py6_radhi']       = ['ttbar_radhi']
    tt['py6_radlo']       = ['ttbar_radlo']
    tt['py8']             = ['ttbarPy8']
    tt['py8_PowHW']       = ['ttbarPowHW_H7UE'] 
    tt['py8_aMcAtNloPy8'] = ['ttbaraMcAtNloPy8'] 
    tt['py8_radhi']       = ['ttbarPy8_radhi']
    tt['py8_radlo']       = ['ttbarPy8_radlo']
    self.samples['tt'] = tt

    stop = {}
    stop['PowPy6']  = ['stop_s','stop_t','stop_Wt']
    stop['DS']       = ['stop_Wt_DS']
    stop['radlo']    = ['stop_Wt_RadLo']
    stop['radhi']    = ['stop_Wt_RadHi']
    stop['PowHW']    = ['stop_Wt_PowHer']
    stop['aMCAtNlo'] = ['stop_Wt_McAtNlo']
    self.samples['stop'] = stop

    diboson = {}
    diboson['PowPy8']   = ['WW_Pw','ZZ_Pw','WZ_Pw'] 
    diboson['sherpa'] = ['diboson_sherpa']
    self.samples['diboson'] = diboson
    
    zjets = {}
    zjets['sherpa221'] = ['Zee','Zmm','Ztt'] 
    zjets['madgraph']  = ['MadZee','MadZmumu','MadZtautau' ]
    self.samples['zjets'] = zjets

    fake = {}
    fake['nominal'] = ['fake']
    self.samples['fake'] = fake
    

  def Modellings(self):
    self.modellings = {}
    tt = {}
    tt['py6'] = {
      'tt Fragmentation' : ['py6','py6_PowHW'],
      'tt Radiation'     : ['py6_radhi', 'py6_radlo'],
      'tt HardScatter'   : ['py6_aMcAtNloHW','py6_PowHW'],
      'tt PDFRW'         : ['py6_aMcAtNloHW', 'py6_PDFRW'],
    } 
    tt['py8'] = {
      'tt Fragmentation' : ['py8','py8_aMcAtNloPy8'],
      'tt Radiation'     : ['py8_radhi', 'py8_radlo'],
      'tt HardScatter'   : ['py8','py8_aMcAtNloPy8'],
    }
    self.modellings['tt'] = tt

    #v1: the as same as r20.7 and r21 by Jan-26-2018
    stop = {}
    stop['stop_v1'] = { 
                     'StopDRDS'          :['PowPy6','DS'],
                     'StopRadiation'     :['radhi','radlo'],
                     'StopFragmentation' :['PowPy6','PowHW'],
                     'StopHardScatter'   :['PowHW','aMCAtNlo'],
    }
    self.modellings['stop'] = stop

    zjets = {}
    zjets['zjets_v1'] = {
      'zjetsModelling' : ['madgraph','sherpa221'], 
    }
    self.modellings['zjets'] = zjets

if __name__ == '__main__':
  a = DataConfig()
