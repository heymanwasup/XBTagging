import toolkit
class Settings(object):
  def __init__(self):
    self.rtag = 'test'
    self.inputFile  = './input/test.root'
    self.outputPath = './output/'
    self.jet    = 'CalJet'

    self.nToys        = 10000
    self.loadFromJson = True
    self.binnings     = 'CalNew'
    self.onlyNominal      = False
    self.rebinning    = False
    self.format       = 'r21a1'

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
      'tt'      : 'py8',
      'stop'    : 'stop_v1',
      'zjets'   : 'zjets_v1',
    }
    self.scales = [
      'WtScale',
      'dibosonScale',
      'zjetsScale',
      'fakeScale',
      'lumiScale',
    ]

def main(cfg_path_fmt):
  cfg_obj = Settings()
  cfg_path = cfg_path_fmt.format(cfg_obj.jet,cfg_obj.rtag)
  toolkit.DumpClassToJson(cfg_obj,cfg_path)
  return cfg_path

if __name__ == '__main__':
  main('./data/Settings_{0:}_{1:}.json')
