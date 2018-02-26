import sys,os,time,pickle,imp,hashlib,importlib,json,itertools,re,copy,array,functools,math,operator
import ROOT as R
import toolkit
from toolkit import ALG

from data.CommonDataInterface import DataConfig


isDebug = False

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
    data     = cm['data'][sp['data']]
    cats   = cm['cats'][sp['cats']]
    binnings = cm['binnings'][sp['binnings']]
    cats.update(sp.pop('cats_add',{}))

    config = {
      'samples_register' : samples_register, 
      'nominals'         : nominals,
      'modellings'       : modellings,
      'scales'           : scales,
      'format'           : fmt,
      'data'             : data,
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
    self._binnings = array.array('d',self._binnings)
    self.HistR = GetHistClass('Raw',len(self._binnings)-1)
    self.HistD = GetHistClass('Dish',len(self._binnings)-1)
    self.HistE = GetHistClass('Error',len(self._binnings)-1)

    self.init_io()
    self.init_environment()
    self.init_varList()
    self.init_scales()
    self.init_samples()
    self.init_wrapFoos()

  def init_io(self):
    def PrintToFd(fd,name):
      head = '{0:<15}'.format('[{0:} {1:}]'.format(name,fd))
      def Print(*args):
        with open('/dev/fd/%s'%(fd),'a') as f:
          print >>f,'\n','-'*12
          for arg in args:
            print >>f,'{0:} {1:}'.format(head,arg.__str__())
          print >>f,'-'*12,'\n'
      return Print
    self.Warning    = PrintToFd(0,'Warning') 
    self.FBIWarning = PrintToFd(2,'FBIWarning')
#    self.CCPWarning = PrintToFd(2,'CCPWarning')
#    self.STDOUT     = PrintToFd(1,'STDOUT')
      
  def init_environment(self):
    self.ftag      = toolkit.GetHashFast(self._input)[::2]
    hasher = hashlib.md5()
    hasher.update(self.cfg_str)
    self.ctag = hasher.hexdigest()[::4] 
    self.cache_dir = '%s/cache/%s/'%(self.wk_dir,self.ftag)  
    self.out_dir   = os.path.join(self.wk_dir, self._output,self._rtag)
    toolkit.mkdir(self.cache_dir)
    toolkit.mkdir(self.out_dir)
    cfg_json = '%s/config_%s.json'%(self.out_dir,self._rtag)
    with open(cfg_json,'w') as f:
      f.write(self.cfg_str)

  def init_varList(self):
    if not self._nominal:
      vars_json = '%s/variations.json'%(self.out_dir)
      if not os.path.isfile(vars_json):
        data = Caliber.GetVarsList(self.file,
            self._format['nominal']['var'],
            self._format['variation']['var'])
        with open(vars_json,'w') as f:
          toolkit.DumpToJson(data,f)
      with open(vars_json,'r') as f:
        self.varsList = toolkit.json_loads(f.read())

  def init_scales(self):
    for name,scale in self._scales.iteritems():
      scale['status'] = None
      scale['pass'] = False
      if 'samples' in scale:
        scale['samples'] = re.compile(scale['samples'])
      if 'keys' in scale:
        for key,regexp in scale['keys'].iteritems():
          scale['keys'][key] = re.compile(regexp)


  def init_samples(self):
    self.nominal_samples = { sam:{name:self._samples_register[sam][name]} \
      for sam,name in self._nominals.iteritems() }

  def init_wrapFoos(self):
    self.isHist = lambda hist : True if hist.__doc__ == '__MetaHistogram__' else False
    f = lambda foo,name,Hist:setattr(self,foo,self.LoadFromJson(name,Hist)(getattr(self,foo))) 
    f('GetRaw','raw',self.HistR)  
    f('GetRawScales','raw_scales',self.HistR)
    f('GetRawVariations','raw_variations',self.HistR)


  def LoadingCfg(self):
    self.gene_cfg = toolkit.json_loads(self.cfg_str)
    #toolkit.DumpToJson(self.gene_cfg) 

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
#self.STDOUT(self.cat_itm, self.cat_str)
      self.PerformTagAndProbe()

  def PerformTagAndProbe(self):

    raw = self.GetRaw()
    raw_nominal = self.LoadNominal(raw)

    raw_scales = self.GetRawScales()
    raw_variations = self.GetRawVariations()

    dish_nominal = self.CookNominal(raw_nominal)  
    dish_modellings = self.CookModellings(raw,raw_nominal)
    dish_scales = self.CookScales(raw_scales)
    dish_variations = self.CookVariations(raw_variations,raw_nominal['data'])
      
    err_stat = self.ErrorStat(raw_nominal)  
    err_modellings = self.ErrorModellings(dish_modellings)
    err_scales = self.ErrorScales(dish_scales)
    err_variations = self.ErrorVariations(dish_variations)
    
    self.DumpResults(dish_nominal,
        err_stat,err_modellings,err_scales,err_variations)

  def GetRaw(self):
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
    for name,scale in self._scales.items():
      scale['status'] = 0
      down = self.LoadNominal(self.GetRawDataMC(samples,scale))
      scale['status'] = 1
      up   = self.LoadNominal(self.GetRawDataMC(samples,scale))
      res[name] = [down,up]
    return res

  def GetRawVariations(self):
    if self._nominal:
      return {}
    fmt  = self._format['variation']['hist']
    samples = self.nominal_samples
    res = {}
    for variation,up_down in self.varsList.iteritems():
      down = self.LoadNominal(self.GetRawMC(fmt,up_down[0],samples))
      up   = self.LoadNominal(self.GetRawMC(fmt,up_down[1],samples))
      res[variation] = [down,up]
    return res

  def GetRawMC(self,fmt,var,samples,scale={}):
    keys = {
      'var' : var,
      'jet' : self._jet,
    }
    raw = {}
    mcEmpty = True
    for sample, entries in samples.iteritems():
      raw[sample] = {}
      scale['pass'] = False if not 'samples' in scale else scale['samples'].match(sample)
      for name, items in entries.iteritems():
        raw[sample][name] = {}
        isEmpty = True
        for key in ['PxT','PxP','PjT','PjP','PbT','PbP']:
          keys['tp'] = key
          raw[sample][name][key],status = self.GetRawEntries(fmt,keys,items,scale)
          isEmpty &= not status
        mcEmpty &= isEmpty
        if isEmpty:
          self.FBIWarning('Sample Empty',var,sample,name)
    if mcEmpty:
      samples_used = ['<%s> %s'%(sample,name) for name in entries \
                     for sample,entries in samples.iteritems()]
      self.FBIWarning('MC Empty!',var,*samples_used)
    return raw

  def GetRawData(self,scale={}):
    if 'samples' in scale:
      scale['pass'] = scale['samples'].match('data')
    else:
      scale['pass'] = False

    fmt = self._format['nominal']
    hfmt = fmt['hist']
    keys = {
      'var' : fmt['var'],
      'jet' : self._jet,
    }
    raw = {'data':{}}
    bad = True 
    
    isEmpty = True 
      
    for tp in ['PxT','PxP']:
      keys['tp'] = tp
      raw['data'][tp],status = self.GetRawEntries(hfmt,keys,self._data,scale)
      isEmpty &= not status
   
    if isEmpty:
      raise RuntimeError('data is empty')

    return raw

  def Cook(self,entry):
    keys = entry.keys() 
    ntKeys = set(keys) - set(['data','tt'])
    dt = entry['data']
    tt = entry['tt']
    
    nt = ALG().Reduce(
        lambda obj:True if isinstance(obj,self.HistR) else False,
        operator.add,
        [entry[key] for key in ntKeys])
    self.HistR.altHist = self.HistD
    I = self.HistD(vals=[1]*self.HistR.nbins)
    dish = {}
    dish['f_tb'] = tt['PbT']/(tt['PbT']+tt['PjT'])
    dish['e_nb'] = tt['PjP']/tt['PjT']
    dish['e_mc'] = tt['PbP']/tt['PbT'] 
    dish['e_tt'] = (dt['PxP']-nt['PxP'])/(dt['PxT']-nt['PxT'])
    dish['e_dt'] = (dish['e_tt']-dish['e_nb']*(I-dish['f_tb']))/dish['f_tb']
    dish['sf'] = dish['e_dt']/dish['e_mc']
    self.HistR.altHist = None
    return dish

  def LoadNominal(self,raw): 
    samples = {}
    for sample,entries in raw.iteritems():
      if sample == 'data':
        samples['data'] = raw['data']
      else:
        samples[sample] = entries[self._nominals[sample]]
    return samples

  def CookNominal(self,raw_nominal):
    dish = self.Cook(raw_nominal)
    return dish
 
  def CookModellings(self,raw,raw_nominal):
    modellings = {}
    for sample,modelling in self._modellings.iteritems():
      for name,samples in modelling.iteritems():
        down = samples[0] 
        up   = samples[1] 
        sam_down = toolkit.MergeDict(raw_nominal,{sample:raw[sample][samples[0]]})
        sam_up   = toolkit.MergeDict(raw_nominal,{sample:raw[sample][samples[1]]})
        dish_down = self.Cook(sam_down)
        dish_up = self.Cook(sam_up)
        modellings[name] = [dish_down, dish_up] 
    return modellings  

  def CookScales(self,raw_scale):  
    scales = {}
    for scale, entries in raw_scale.iteritems():
      down = self.CookNominal(entries[0])
      up   = self.CookNominal(entries[1])
      scales[scale] = [down,up]
    return scales    

  def CookVariations(self,raw_var,raw_data):
    variations = {}
    for var,entries in raw_var.iteritems():
      sam_down = toolkit.MergeDict({'data':raw_data},entries[0])
      sam_up   = toolkit.MergeDict({'data':raw_data},entries[1])
      try:
        dish_up = self.Cook(sam_up)
        dish_down = self.Cook(sam_down)
        variations[var] = [dish_down,dish_up]
      except ValueError:
        self.FBIWarning ('%s is empty,skip it'%(var))
        continue
    return variations

  def CookRandom(self,r,orig):
    def gwalker(tot,pas,toterr,paserr):
      tot = [t if t>0 else 0 for t in tot ]
      pas = [p if p>0 else 0 for p in pas ]
      gaus = lambda x,y:r.Gaus(x,y) if r.Gaus(x,y)>0 else 0

      ratio = [ float(pas[n])/tot[n] if tot[n]!=0 else 0 for n in range(len(pas)) ]
      p = lambda x:list(map(lambda y:'{0:.3f}'.format(y),x))
      paserr = list(map(lambda x,y:x*math.sqrt(y*(1-y)),toterr,ratio))
      Rtot = list(map(gaus,tot,toterr))
      Rpas = list(map(lambda x,y,z:gaus(x*y,z),Rtot,ratio,paserr))
      return Rtot,Rpas
    def pwalker(tot,pas,toterr,paserr):
      ratio    = [ float(pas[n])/tot[n] if tot[n]!=0 else 0 for n in range(len(pas)) ]
      Rtot     = list(map(lambda x:int(round(r.Poisson(x))),tot))
      Rpas     = list(map(r.Binomial,Rtot,ratio))
      return Rtot,Rpas
    def Toss(r,walker,entries,key_pairs):
      Rentries = copy.copy(entries)
      for ktot,kpas in key_pairs:
        tot, toterr = entries[ktot].vals, entries[ktot].errs
        pas, paserr = entries[kpas].vals, entries[kpas].errs

        Rtot, Rpas = walker(tot,pas,toterr,paserr)
        Rentries[ktot], Rentries[kpas] = self.HistR(vals=Rtot),self.HistR(vals=Rpas)
      return Rentries
    R_raw_dt = {}
    R_raw_mc = {}
    for sample, entries in orig.iteritems():
      if sample == 'data':
        R_entries = Toss(r,pwalker,entries,[('PxT','PxP')])
        R_raw_dt[sample] = R_entries
      else:
        R_entries = Toss(r,gwalker,entries,[('PxT','PxP'),('PbT','PbP'),('PjT','PjP')])
        R_raw_mc[sample] = R_entries
    R_dt = toolkit.MergeDict(orig,R_raw_dt)
    R_mc = toolkit.MergeDict(orig,R_raw_mc)
    return self.Cook(R_dt),self.Cook(R_mc)

  def ErrorStat(self,raw):
    self.HistD.do_assert = False 
    isHist = lambda hist : True if hist.__doc__ == '__MetaHistogram__' else False
    emptyH = lambda hist : type(hist)(vals=[0]*type(hist).nbins)
    emptyD = lambda data : ALG().Map(isHist,emptyH,self.Cook(data))
    add    = lambda x,y : ALG().Map(isHist,lambda x,y:x+y/self._nToys,x,y)
    sub    = lambda x,y : ALG().Map(isHist,operator.sub,x,y)
    square = lambda x : ALG().Map(isHist,lambda x:x**2,x)
    sqt   = lambda x : ALG().Map(isHist,lambda x:x.sqrt(),x)
    r = R.TRandom3() 
    m1_mc = emptyD(raw) 
    m2_mc = emptyD(raw) 
    m1_dt = emptyD(raw) 
    m2_dt = emptyD(raw) 
    for _ in range(self._nToys):
      Rm1_dt, Rm1_mc = self.CookRandom(r,raw) 
      Rm2_dt, Rm2_mc = square(Rm1_dt),    square(Rm1_mc)
      m1_dt,  m1_mc  = add(m1_dt,Rm1_dt), add(m1_mc,Rm1_mc) 
      m2_dt,  m2_mc  = add(m2_dt,Rm2_dt), add(m2_mc,Rm2_mc) 
    m1_mc_pow = square(m1_mc)
    m1_dt_pow = square(m1_dt)

    stat_dt   = sqt(sub(m2_dt,m1_dt_pow))
    stat_mc   = sqt(sub(m2_mc,m1_mc_pow))

    stats     = {'data stats':stat_dt, 'mc stats':stat_mc}
    self.HistD.do_assert = True
    return stats
      
  def GetRawEntries(self,fmt,keys,samples,scale):
    keys.update(self.cat_itm)
    hist = self.HistR()
    entries = []
    for sample in samples:
      keys['sample'] = sample
      hsf = self.GetHistSF(scale,keys)
      hname = fmt.format(**keys)
      entries.append((hname,hsf))
    for hname,hsf in entries:
      th1 = self.file.Get(hname)
      if not th1:
        continue
      else:
        if self._rebinning:
          th1 = th1.Rebin(len(self._binnings)-1,'',self._binnings)
        hist_temp = self.HistR(th1)
        hist_temp.Scale(hsf)
        hist.Add(hist_temp)
    status, verbose = hist.Report()    
    if not status:
      self.Warning(verbose,*[entry[0] for entry in entries])
    return hist,status
      
  @staticmethod
  def GetHistSF(scale,keys):
    if not scale['pass'] \
      or len(scale.keys())<4:
      return 1.
    if 'keys' in scale:
      for key,reg in scale['keys'].iteritems():
        if not reg.match(keys[key]):
          return 1.
    return scale['scale'][scale['status']]      
 
  def JsonToHist(self,data,Hist,inverse=False):
    isHist = lambda hist : True if hist.__doc__ == '__MetaHistogram__' else False
    isAtom = lambda atom : True if 'vals' in atom else False

    atomToHist = lambda atom : Hist(**atom)
    histToAtom = lambda hist : {'vals':hist.vals, 'errs':hist.errs}

    wraper = lambda stop,alg:lambda entry:alg(entry) if stop(entry) else entry
    algHistToAtom = wraper(isHist,histToAtom) 
    algAtomToHist = wraper(isAtom,atomToHist)

    if not inverse:
      out = ALG().Map(isAtom,atomToHist,data)
    else:
      out = ALG().Map(isHist,histToAtom,data)
    return out

  def ErrorModellings(self,dishes):
    return self.ErrorAlter(dishes)

  def ErrorScales(self,dishes):
    return self.ErrorAlter(dishes)

  def ErrorVariations(self,dishes):
    return self.ErrorAlter(dishes)

  def ErrorAlter(self,dishes):
    isHist = lambda hist : True if hist.__doc__ == '__MetaHistogram__' else False
    self.HistD.altHist = self.HistE
    errorAlter = {}
    for name,entries in dishes.iteritems():
      errorAlter[name] = ALG().Map(isHist,lambda x,y:((x-y)/2).abs(),*entries)
    self.HistD.altHist = None
    return errorAlter

  def DumpResults(self,results,err_stat,err_mod,err_scal,err_var):
    def dump_err(data,errs,key):
      for name in errs.keys():
        data[key][name] = errs[name][key].vals
    keys = results.keys()
    data = {} 
    for key in keys:
      data[key] = {}
      data[key]['nominal'] = results[key].vals
      dump_err(data,err_stat,key)
      dump_err(data,err_mod,key)
      dump_err(data,err_scal,key)
      dump_err(data,err_var,key)
    with open('%s/output_%s.json'%(self.out_dir,self.cat_str),'w') as f:
      for d in data:
        for _d in data[d]:
          pass
      toolkit.DumpToJson(data,f)
      
  def LoadFromJson(self,name,Hist):
    json_name = '%s/%s.json'%(self.out_dir,name)
    def Wraper(fun): 
      @functools.wraps(fun)
      def newFun(*args,**kw):
        if not self._loadFromJson or not os.path.isfile(json_name):
          self.STDOUT('Producing json file :','\t%s'%(json_name))
          res_h = fun(*args,**kw)
          res_j = self.JsonToHist(res_h,Hist,inverse=True)
          with open(json_name,'w') as f:
            toolkit.DumpToJson(res_j,f)
        with open(json_name,'r') as f:
          res_j = toolkit.json_loads(f.read())
        res_h = self.JsonToHist(res_j,Hist)  
        return res_h
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
  def Gurantee_raw(self):
    self.vals[0], self.errs[0] = 0, 0
  def Assert_raw(self):
    for val in self.vals:
      assert not math.isnan(val)
  def Warnings_raw(self):
    isEmpty,verbose = self.IsEmpty()
    return not isEmpty, verbose
  def Gurantee_dish(self):
    self.vals[0], self.errs[0] = 0, 0
    for n in range(1,type(self).nbins):
      if math.isnan(self.vals[n]) or self.vals[n]<0:
        self.vals[n] = 0
  def Assert_dish(self):
    isEmpty,verbose = self.IsEmpty()
    if isEmpty:
      raise ValueError("is empty")
  def Warnings_dish(self):
    good = True
    for n in range(1,type(self).nbins):
      good &= (self.vals[n]>0.) and (not math.isnan(self.vals[n])) and (not self.vals[n]<0)
    return good,' 0 or nan or negative founded %s'%self.vals.__str__()
    

  report_raw = {
    'nbins'         : nbins ,
    'do_gurantee'   : True,
    'do_warnings'   : True,
    'do_assert'     : True,
    'always_report' : False,
    'Gurantee'      : Gurantee_raw,
    'Assert'        : Assert_raw,
    'Warnings'      : Warnings_raw,
  }
  report_dish = {
    'nbins'         : nbins ,
    'do_gurantee'   : True,
    'do_warnings'   : False,
    'do_assert'     : True,
    'always_report' : True,
    'Gurantee'      : Gurantee_dish,
    'Assert'        : Assert_dish,
    'Warnings'      : Warnings_dish,
  }
  report_error = {
    'nbins'         : nbins ,
    'always_report' : False,
  }
 
  if name == 'Dish':
    Hist = toolkit.FooCopyClass(name,toolkit.TemplateHist,new_attrs=report_dish)
  elif name == 'Raw':
    Hist = toolkit.FooCopyClass(name,toolkit.TemplateHist,new_attrs=report_raw)
  elif name == 'Error':
    Hist = toolkit.FooCopyClass(name,toolkit.TemplateHist,new_attrs=report_error)
  else:
    raise ValueError('histogram name not found: {0:}'.format(name))
  return Hist

  
def main():
  worker = RetrieveEfficiency('./XBTagging/data/TPConfig.py')
  worker.Work()
 
if __name__ == '__main__':
  main()
