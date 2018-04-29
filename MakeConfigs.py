import toolkit
import TPConfig
import CommonDataInterface


def MakeConfigForCalib(overall_info_cfg,run_info_cfg,cfg_path_fmt):
  overall_info = toolkit.json_load(overall_info_cfg)
  run_info = toolkit.json_load(run_info_cfg)

  samples_register = {} 
  for sample,item in run_info['samples'].iteritems():
    items = [item]
    if sample in run_info['modellings']:
      modelling = overall_info['modellings'][sample][run_info['modellings'][sample]]
      for name,mod_items in modelling.iteritems():
        items += mod_items
    samples_register[sample] = {_item:overall_info['samples'][sample][_item] for _item in items}    
  
  modellings = { sample : overall_info['modellings'][sample][items] \
    for sample,items in run_info['modellings'].iteritems()}

  nominals = run_info['samples']
  scales   = {name:overall_info['scales'][name] for name in run_info['scales']}
  fmt      = overall_info['format'][run_info['format']]
  data     = overall_info['data'][run_info['data']]
  cats   = overall_info['cats'][run_info['cats']]
  binnings = overall_info['binnings'][run_info['binnings']]
  cats.update(run_info.pop('cats_add',{}))
  nToys = run_info['nToys']
  rebinning = run_info['rebinning']
  jet = run_info['jet']
  loadFromJson = run_info['loadFromJson']
  onlyNominal = run_info['onlyNominal']
  rtag = run_info['rtag'] 
  inputFile = run_info['inputFile']  
  outputPath = run_info['outputPath']

  config = {
    #nominal+modelling samples
    'samples_register' : samples_register, 

    #nominal samples
    'nominals'         : nominals,

    #modelling samples
    'modellings'       : modellings,

    #Xsection uncertainties estimated by normalizing samples 
    'scales'           : scales,

    #format for histograms of nominal and variations
    'format'           : fmt,

    #data name
    'data'             : data,

    #categories to be calibrated
    'cats'             : cats,  

    #binning scheme of pT range
    'binnings'         : binnings,

    #MC toys for estimating statistical uncertainties
    'nToys'            : nToys,

    #whether or not rebinning histograms
    'rebinning'        : rebinning,

    #Jet author to be calibrated 
    'jet'              : jet,

    #whether or not read raw data directly from saved json file
    #could save the running time
    'loadFromJson'     : loadFromJson,
    
    #if true, systematics estimated from variations won't be considered 
    'onlyNominal'      : onlyNominal,

    #name of this run
    'rtag'             : rtag,

    #input root file 
    'inputFile'        : inputFile,
    
    #path of output json files
    'outputPath'       : outputPath,
  }

  cfg_path = cfg_path_fmt.format(config['jet'],config['rtag'])
  toolkit.DumpToJson(config,open(cfg_path,'w'))
   
  return cfg_path


def main():
  #make general info cfg
  overall_cfg_path = './data/Overall_Info.json'
  CommonDataInterface.main(overall_cfg_path)
  print '{0:}\n  Generated!\n'.format(overall_cfg_path)

  #make settings cfg
  settings_cfg_path = TPConfig.main('./data/Settings_{0:}_{1:}.test.json')
  print '{0:}\n  Generated!\n'.format(settings_cfg_path)

  #make calibration info cfg
  run_cfg_path = MakeConfigForCalib(overall_cfg_path,settings_cfg_path,'./data/Run_{0:}_{1:}.test.json')
  print '{0:}\n  Generated!\n'.format(run_cfg_path)
  

if __name__ == '__main__':
  main()



