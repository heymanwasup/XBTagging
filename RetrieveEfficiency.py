import sys,os,time,pickle,imp,hashlib,importlib,json,itertools,re
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
    sp      = toolkit.Decomposer(sp_cfg)
    cm      = toolkit.Decomposer(cm_cfg)
    sp_keys = set(sp.keys()) - set(cm.keys())
    cm_keys = set(sp.keys()).intersection(set(cm.keys()))

    sp_dict = {key:sp[key] for key in sp_keys}
    cm_dict = {key:self.Trans(sp[key],cm[key]) for key in cm_keys}
    for key,value in cm_dict['modellings'].iteritems():
      for _key,_value in value.iteritems():
        for n,name in enumerate(_value):
          _value[n] = cm['samples'][key][name]

    cm_dict.update(sp_dict)
    cm_dict['cats'].update(cm_dict['cats_add']) 
    cm_dict.pop('cats_add',None)

    return cm_dict
    
  def Trans(self,sp,cm):
    if isinstance(sp,str):
      res = cm[sp]
    elif isinstance(sp,dict):
      res = {}
      for _key in sp:
        res[_key] = self.Trans(sp[_key],cm[_key])
    else:
      try:
        iterator = iter(sp)
      except TypeError:
        raise TypeError('sp,\n\t{0:}\ncm,\n\t{1:}\n\
            sp not str or dict or other_iterable_obj.'.format(str(sp),str(cm)))
      else:
        res = []
        for _key in sp:
          res.append(self.Trans(_key,cm))
    return res   



class Caliber(object):
  def __init__(self,cfg,wk_dir='./'):
    self.cfg_str  = json.dumps(cfg,indent=4,sort_keys=True)
    self.wk_dir   = wk_dir
    
    self.LoadingCfg()
    self.Initialize()

  def Initialize(self):
    self.file      = R.TFile(self._input)
    self.ftag      = toolkit.GetHashFast(self._input)
    
    hasher = hashlib.md5()
    hasher.update(self.cfg_str)
    self.ctag = hasher.hexdigest()[::2] 
    
    self.cache_dir = '%s/cache/%s/'%(self.wk_dir,self.ftag)  
    self.out_dir   = os.path.join(self.wk_dir, self._output,self._rtag)

    toolkit.mkdir(self.out_dir)
    toolkit.mkdir(self.cache_dir)

    if not self._nominal:
      vars_json = '%s/variations.json'%(self.cache_dir)
      if not os.path.isfile(vars_json):
        data = Caliber.GetVarsList(self.file,
            self._format['nominal']['var'],
            self._format['variation']['var'])
        with open(vars_json,'w') as f:
          toolkit.DumpDictToJson(data,f)
      with open(vars_json,'r') as f:
        self.varsList = json.loads(f.read())

    cfg_json = '%s/config_%s.json'%(self.out_dir,self._rtag)
    with open(cfg_json,'w') as f:
      f.write(self.cfg_str)

    
    ''' 
      foo = lambda x:'' if x==0 else x
      n = 0
      while os.path.isfile(toolkit.format(cfg_json,{'t':foo(n)})):
        with open(toolkit.format(cfg_json,{'t':foo(n)}),'r') as f:
          cfg_str = json.dumps(json.loads(f.read()),indent=4,sort_keys=True)
    '''     
    

  def LoadingCfg(self):
    self.gene_cfg = json.loads(self.cfg_str)
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
      self.cat = self.cat_itms[Niter]
      Niter += 1
      status = True
    return status

  def Run(self):
    #self.LoadingCfg()
    #self.Initialize()

    while self.Next():
      self.PerformTagAndProbe()

  def PerformTagAndProbe(self):
    raw  = self.Retrieve_raw()
    dish = self.Cook(raw) 

    raw_var   = self.Retrieve_raw_var()
    dish_var  = self.CookVar(raw_var) 
    error_var = self.ErrorVar(dish_var)
      
    statError  = self.StatError(raw)
    scaleError = self.ScaleError(raw) 
    modelError = self.ModelError(raw)

    self.DumpResuls(dish,
        error_var,errorStat,errorScale,errorModel)

  #def  Retrieve_raw(self):
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






def main():
  worker = RetrieveEfficiency('./XBTagging/data/TPConfig.py')
 
if __name__ == '__main__':
  main()
