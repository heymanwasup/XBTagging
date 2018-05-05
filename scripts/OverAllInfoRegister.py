import toolkit

class DataConfig(object):
  def __init__(self):

    self.data, self.samples = self.Samples()

    self.modellings = self.Modellings()

    self.scales = self.Scales()

    self.format = self.HistFormats()

    self.cats = self.Categories()

    self.binnings = self.Binnings()

  def Scales(self):
    scales = {}
    scales['ntBCal'] = {
      'samples' : '(?!tt)',
      'keys'    : {'tp':'PbP','jet':'Cal.*'},
      'scale'   : [0.84,1.2], 
    }

    scales['ntBTrk'] = {
      'samples' : '(?!tt)',
      'keys'    : {'tp':'PbP','jet':'Trk.*'},
      'scale'   : [0.84,1.2], 
    }

    scales['mistagTrk'] = {
      'keys'    : {'tp':'PjP','jet':'Trk.*'},
      'scale'   : [0,2.5], 
    }

    scales['mistagCal'] = {
      'keys'    : {'tp':'PjP','jet':'Cal.*'},
      'scale'   : [0,2.3], 
    }

    scales['WtScale'] = {
      'samples' : 'stop',
      'keys'    : {'sample':'.*Wt.*'},
      'scale'   : [0.5,1.5],
    }

    scales['dibosonScale'] = {
      'samples' : 'diboson',
      'scale'   : [0.5,1.5],
    }
    
    scales['zjetsScale'] = {
      'samples' : 'zjets',
      'scale'   : [0.5,1.5],
    }
    
    scales['fakeScale'] = {
      'samples' : 'fake',
      'scale'   : [0.5,1.5],
    }

    scales['lumiScale'] = {
      'samples' : '.*',
      'scale'   : [1.032,9.968],
    }
    return scales
  
  def Binnings(self):
    binnings = {}
    binnings['CalOld'] = [0,20,30,60,90,140,200,300]
    binnings['CalNew'] = [0,20,30,40,60,85,110,140,175,250,600]
    binnings['CalEta'] = [0,30,60,90,140,200] 
    binnings['TrkOld'] = [0,10,20,30,60,100,250] 
    binnings['TrkEta'] = [0,30,60,100,250] 
    binnings['Mu']     = [0,20,60,300]
    return binnings
  
  def HistFormats(self):
    fmt = {}

    r21a1_nominal = {
      'hist' : '{var:}/{sample:}_TP_1ptag2jet_MVA{mva:}_{mu:}_em_{eta:}_{tp:}{wp:}{jet:}Pt',
      'var'  : 'SysNominal',
    }
    r21a1_variation = {
      'hist' : '{var:}/{sample:}_TP_1ptag2jet_MVA{mva:}_{mu:}_em_{eta:}_{tp:}{wp:}{jet:}Pt_{var:}', 
      'var'  : r'(.*[^_])(_+[0-9]*)(up|down)',
    }
    r21a1 = {
      'nominal'   : r21a1_nominal,
      'variation' : r21a1_variation,
    }
    fmt['r21a1'] = r21a1

    return fmt

  def Categories(self):  
    cats = {}
    cats['ptCalib']  = {'mu' : ['XMu'], 'eta' : ['xEta'],}
    cats['muCalib']  = {'mu' : ['_0_18Mu','_18_25Mu','_25_50Mu'], 'eta' : ['xEta'], }
    cats['etaCalib'] = {'mu' : ['XMu'], 'eta' : ['_0_7Eta','_7_15Eta','_15Eta'], }
    return cats
    
  def Samples(self):
    data = {
      'nominal':['data'],
    } 

    mc_samples    = {}

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
    mc_samples['tt'] = tt

    stop = {}
    stop['PowPy6']   = ['stop_s','stop_t','stop_Wt']
    stop['DS']       = ['stop_Wt_DS']
    stop['radlo']    = ['stop_Wt_RadLo']
    stop['radhi']    = ['stop_Wt_RadHi']
    stop['PowHW']    = ['stop_Wt_PowHer']
    stop['aMCAtNlo'] = ['stop_Wt_McAtNlo']
    mc_samples['stop'] = stop

    diboson = {}
    diboson['PowPy8']   = ['WW_Pw','ZZ_Pw','WZ_Pw'] 
    diboson['sherpa'] = ['diboson_sherpa']
    mc_samples['diboson'] = diboson
    
    zjets = {}
    zjets['sherpa221'] = ['Zee','Zmm','Ztt'] 
    zjets['madgraph']  = ['MadZee','MadZmumu','MadZtautau' ]
    mc_samples['zjets'] = zjets

    fake = {}
    fake['nominal'] = ['fake']
    mc_samples['fake'] = fake
    return data, mc_samples
    

  def Modellings(self):
    modellings = {}
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
    modellings['tt'] = tt

    #v1: the as same as r20.7 and r21
    stop = {}
    stop['stop_v1'] = { 
                     'stop DRDS'          :['PowPy6','DS'],
                     'stop Radiation'     :['radhi','radlo'],
                     'stop Fragmentation' :['PowPy6','PowHW'],
                     'stop HardScatter'   :['PowHW','aMCAtNlo'],
    }

    modellings['stop'] = stop

    zjets = {}
    zjets['zjets_v1'] = {
      'zjets Modelling' : ['madgraph','sherpa221'], 
    }
    modellings['zjets'] = zjets

    return modellings

def main(cfg_path):
  cfg_obj = DataConfig()
  toolkit.DumpClassToJson(cfg_obj,cfg_path)
  return cfg_path

if __name__ == '__main__':
  main()
  
