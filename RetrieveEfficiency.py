import sys,os,time,pickle,imp,hashlib,importlib,json,itertools,re,copy
import ROOT as R
import toolkit

from data.CommonDataInterface import DataConfig


isDebug = True

class RetrieveEfficiency(object):
  def __init__(self,cfg_path):
    Settings = imp.load_source('Settings',cfg_path)
    
    tp_cfg = Settings.Settings()
    cm_cfg = DataConfig()

    Cfg = self.MakeConfigDict(tp_cfg,cm_cfg)
    self.caliber = Caliber(Cfg)


  def Work(self):
    self.caliber.Run()

  def MakeConfigDict(self,sp_cfg,cm_cfg):
    sp = toolkit.Decomposer(sp_cfg)
    cm = toolkit.Decomposer(cm_cfg)

    samples_register = {} 
    for sample,item in sp['samples'].iteritems():
      items = [item]
      if sample in sp['modellings']:
        modelling = cm['modellings'][sample][sp['modellings'][sample]]
        for name,mod_items in modelling.iteritems():
          items += mod_items
      samples_register[sample] = {_item:cm['samples'][sample][_item] for _item in items}    
    
    modellings = { sample : cm['modellings'][sample][items] \
      for sample,items in sp['modellings'].iteritems()}

    nominals = sp['samples']
    scales   = {name:cm['scales'][name] for name in sp['scales']}
    fmt      = cm['format'][sp['format']]
    cats   = cm['cats'][sp['cats']]
    binnings = array.array('d',cm['binnings'][sp['binnings']])
    cats.update(sp.pop('cats_add',{}))

    config = {
      'samples_register' : samples_register, 
      'nominals'         : nominals,
      'modellings'       : modellings,
      'scales'           : scales,
      'format'           : fmt,
      'cats'             : cats,  
      'binnings'         : binnings,
    }

    sp_keys = set(sp.keys()) - set(cm.keys())
    sp_dict = {key:copy.deepcopy(sp[key]) for key in sp_keys}
    config.update(sp_dict)
    #s_config = json.dumps(config,indent=4,sort_keys=True)
    
    return config

class Caliber(object):
  def __init__(self,cfg,wk_dir='./'):
    self.cfg_str  = json.dumps(cfg,indent=4,sort_keys=True)
    self.wk_dir   = wk_dir
    self.LoadingCfg()
    self.Initialize()


  def Initialize(self):
    self.file      = R.TFile(self._input)
    self.Hist = GetHistClass('Hist',len(self._binnings)-1)

    self.init_environment()
    self.init_varList()
    self.init_scales()
    self.init_samples()
    self.init_wrapFoos()
  
  def init_environment(self):
    self.ftag      = toolkit.GetHashFast(self._input)
    hasher = hashlib.md5()
    hasher.update(self.cfg_str)
    self.ctag = hasher.hexdigest()[::2] 
    self.cache_dir = '%s/cache/%s/'%(self.wk_dir,self.ftag,self._rtag)  
    self.out_dir   = os.path.join(self.wk_dir, self._output,self._rtag)
    toolkit.mkdir(self.cache_dir)
    toolkit.mkdir(self.out_dir)
    cfg_json = '%s/config_%s.json'%(self.out_dir,self._rtag)
    with open(cfg_json,'w') as f:
      f.write(self.cfg_str)

  def init_varList(self):
    if not self._nominal:
      vars_json = '%s/variations.json'%(self.cache_dir)
      if not os.path.isfile(vars_json):
        data = Caliber.GetVarsList(self.file,
            self._format['nominal']['var'],
            self._format['variation']['var'])
        with open(vars_json,'w') as f:
          toolkit.DumpDictToJson(data,f)
      with open(vars_json,'r') as f:
        self.varsList = toolkit.json_loads(f.read())

  def init_scales(self):
    for name,scale in self._scales.iteritems():
      if 'samples' in scale:
        scale['samples'] = re.compile(scale['samples'])
      if 'keys' in scale:
        for key,regexp in scale['keys'].iteritems():
          scale['keys'][key] = re.compile(regexp)

  def init_samples(self):
    self.nominal_samples = { sam:{name:self._samples_register[sam][name]} \
      for sam,name in self._nominals.iteritems() }

  def init_wrapFoos(self):
    f = lambda foo,cache:setattr(self,foo,self.LoadFromCache(getattr(self,foo),cache)) 
    f('GetRawNominals')  
    f('GetRawScales')
    f('GetRawVariations')

  def LoadingCfg(self):
    self.gene_cfg = toolkit.json_loads(self.cfg_str)
    toolkit.DumpDictToJson(self.gene_cfg) 

    for key,value in self.gene_cfg.iteritems():
      setattr(self,'_%s'%key,value)

    cat_keys = self._cats.keys()
    cat_vals = (self._cats[key] for key in cat_keys)
    cat_itms = list(itertools.product(*cat_vals))
    
    self.cat_keys = cat_keys
    self.cat_itms = cat_itms
    self.Niter = 0

  def Next(self):
    if self.Niter == len(self.cat_itms):
      status = False
    else:
      cat = self.cat_itms[self.Niter]
      self.cat_itm = dict(zip(self.cat_keys,cat))
      self.cat_str = '_'.join(map(str,cat))
      self.Niter += 1
      status = True
    return status

  def Run(self):
#self.LoadingCfg()
#self.Initialize()

    while self.Next():
      print self.cat_itm
      print self.cat_str
      self.PerformTagAndProbe()

  def PerformTagAndProbe(self):

    raw_nominal = self.GetRawNominals()
    raw_scales = self.GetRawScales()
    raw_variations = self.GetRawVariations()

    str_nominal = json.dumps(raw_nominal,indent=4,sort_keys=True)
    str_scales = json.dumps(raw_scales,indent=4,sort_keys=True)
    str_variations = json.dumps(raw_variations,indent=4,sort_keys=True)

    with open('{0:}/raw_nominal')


    dish_nominal = self.CookNominal(raw_nominal)  
    dish_modellings = self.CookModellings(raw_nominal)
    dish_scales = self.CookScales(raw_scales)
    dish_variations = self.CookVariations(raw_variations,raw_nominal['data'])
      
    err_stat = self.ErrorNominal(raw_nominal)  
    err_modellings = self.ErrorModellings(raw_nominal)
    err_scales = self.ErrorScales(raw_scales)
    err_variations = self.ErrorVariations(raw_variations)
    
    self.DumpResuls(dish_nominal,
        err_stat,err_modellings,err_scales,err_variations)

  def GetRawNominals(self):
    samples = self._samples_register
    scale   = {}
    raw = self.GetRawDataMC(samples,scale)
    return raw

  def GetRawDataMC(self,samples,scale):
    fmt  = self._format['nominal']['hist']
    var  = self._format['nominal']['var']
    data = self.GetRawData(scale)
    mc   = self.GetRawMC(fmt,var,samples,scale)
    data.update(mc)
    return data

  def GetRawScales(self):
    samples = self.nominal_samples
    res = {}
    for name,scale in self._scales.iteritems():
      scale['status'] = 0
      down = GetRawDataMC(samples,scale)
      scale['status'] = 1
      up = GetRawDataMC(samples,scale)
      res[name] = [down,up]
    return res

  def GetRawVariations(self):
    if self._nominal:
      return {}
    fmt  = self._format['variation']['hist']
    samples = self.nominal_samples
    res = {}
    for variation,up_down in self.varsList.iteritems():
      down = self.GetRawMC(fmt,up_down[0],samples)
      up   = self.GetRawMC(fmt,up_down[1],samples)
      res[variation] = [down,up]
    return res

  @toolkit.CopyParameters()
  def GetRawMC(self,fmt,var,samples,scale={}):
    keys = {
      'var' : var,
      'jet' : self._jet,
    }
    raw = {}
    for sample, entries in samples.iteritems():
      raw[sample] = {}
      scale['sample'] = sample
      for name, items in entries.iteritems():
        raw[sample][name] = {}
        for key in ['PxT','PxP','PjT','PjP','PbT','PbP']:
          _keys = copy.deepycopy(keys)
          _keys['tp'] = key
          raw[sample][name][key] = self.GetRawEntries(fmt,_keys,items,scale)

  @toolkit.CopyParameters()       
  def GetRawData(self,scale={}):
    
    scale['sample'] = 'data' 
    fmt = self._format['nominal']
    hfmt = fmt['hist']
    keys = {
      'var' : fmt['var'],
      'jet' : self._jet,
    }
    raw = {'data':{}}
    for tp in ['PxT','PxP']:
      keys['tp'] = tp
      raw['data'][tp] = self.GetRawEntries(hfmt,_keys,self._data,scale)
    return raw
      
   
  @toolkit.CopyParameters()
  def GetRawEntries(self,fmt,keys,samples,scale):
    keys.update(self.cat_itm)
    hist = self.Hist()
    for sample in samples:
      keys['sample'] = sample
      hsf = self.GetHistSF(scale,keys)
      hname = fmt.format(**keys)
      th1 = self.file.Get(hname)
      if not th1:
        continue
      else:
        if self._rebinning:
          th1 = th1.Rebin(len(self._binnings)-1,'',self._binnings)
        hist_temp = self.Hist(th1)
        hist_temp.Scale(hsf)
        hist.Add(hist_temp)
    hist.Report()    
    return hist
      
    
  @staticmethod
  def GetHistSF(scale,keys):
    sample = scale['sample'] 
    if len(scale.keys())<2:
      return 1.
    if not scale['samples'].match(sample):
      return 1.
    if 'keys' in scale:
      for key,reg in scale['keys']:
        if not reg.match(keys[key]):
          return 1.
    return scale['scale'][scale['up_down']]      
    
  def LoadFromCache(self,name):
    json_name = '%s/%s___%s.json'%(self.cache_dir,self.ctag,name)
    def Wraper(fun): 
      @functools.wraps(fun)
      def newFun(*args,**kw):
        if os.path.isfile(json_name):
          with open(json_name,'r') as f:
            res = toolkit.json_loads(f.read())
        else:
          res = fun(*args,**kw)
        return res
      return newFun
    return Wraper

  @staticmethod
  @toolkit.TimeCalculator(isDebug) 
  def GetVarsList(rfile,Pnominal,Pvars):
    Rvars      = re.compile(Pvars)
    Rnominal  = re.compile(Pnominal)

    Vars = {}
    for key in rfile.GetListOfKeys():
      obj      = key.ReadObj()
      obj_name = obj.GetName()
      cls_name = obj.ClassName()

      if Rnominal.match(obj_name) \
        or (cls_name.find('TDirectory')==-1) \
        or (obj_name.find('SysLUMI')!=-1):
        continue

      var = Rvars.split(obj_name)[0]
      if var in Vars:
        Vars[var].append(obj_name)
      else:
        Vars[var] = [obj_name]
    for var in Vars: 
      if len(Vars[var])==1:
        Vars[var].append(Pnominal)
    return Vars

def GetHistClass(name,nbins):
  attrs = {
    'nbins'         : nbins ,
    'do_gurantee'   : True,
    'do_warnings'   : True,
    'do_assert'     : True,
    'report_always' : False,
    'Gurantee'      : Gurantee_1,
    'Assert'        : Assert_1,
    'Warnings'      : Warnings_1,
  }
  Hist = toolkit.FooCopyClass(name,toolkit.TemplateHist,new_attrs=attrs)
  return Hist

def Gurantee_1(self):
  self.vars[0], self.errs[0] = 0, 0
def Assert_1(self):
  for val in self.val:
    assert not math.isnan(val)
def Warnings_1(self):
  isEmpty = True
  for n in range(1,type(self).nbins):
    isEmpty &= (self.vars[n]==0)
  if isEmpty:
    print 'empty histogram fined!'
  return (not isEmpty)
  
def main():
  pass
  worker = RetrieveEfficiency('./XBTagging/data/TPConfig.py')
  worker.Work()
 
if __name__ == '__main__':
  main()


