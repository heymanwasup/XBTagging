class Settings(object):
  def __init__(self):
    self.rtag = 'test'
    self.input  = './input/test.root'
    self.output = './output/'
    self.jet    = 'CalJet'


    self.nToys      = 10000
    self.loadCache  = False
    self.binnings   = 'CalNew'
    self.nominal    = False
    self.rebinning  = False
    self.format = 'r21a1'

    self.cats     = 'ptCalib'
    self.cats_add = {
      'wp'  : [60,70,77,85],
      'mva' : [80],
    } 

    self.samples = {
      'tt'      : 'py8',
      'stop'    : 'PowPy6',
      'diboson' : 'PowPy8',
      'zjets'   : 'sherpa221',
      'fake'    : 'nominal',
    } 
    
    self.data = 'nominal'
  

    self.modellings = {
      #'tt'      : 'py8',
      #'stop'    : 'stop_v1',
      #'zjets'   : 'zjets_v1',
    }
    self.scales = [
      'WtScale',
      'dibosonScale',
      'zjetsScale',
      'fakeScale',
      'lumiScale',
    ]
