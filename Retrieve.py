#!/usr/bin/python
import sys, time
import ROOT as R
import tool as T
import pickle
import re,copy,array,operator,functools,math,itertools,multiprocessing,os,commands

def mysum2(*args):  
  pass


def FillDeepDict(Mom,Son,keys): 
  #reductible funtion
  if len(keys)==1:
    Mom[key] = Son
  else:
    for key in keys:
      if not key in Mom:
        Mom[key] = {}
      FillDeepDict(Mom,Son,keys[1:])

def MergeDict(Mom,Son):
  if (not isinstance(Mom,dict)) or (not isinstance(Son,dict)):
    raise ValueError('The twp parameters should be dict!  Mom:{0:} Son:{1:}'.format(Mom.__str__(),Son.__str__()))
  for key,value in Son.iteritems():
    if not key in Mom:
      Mom[key] = value
    else:
      MergeDict(Mom[key],Son[key])

def MergePickles(inpath,outpath):
  if not os.path.isdir(outpath):
    os.system('mkdir {0:}'.format(outpath))
  
  files = commands.getstatusoutput('ls {0:}/*.pickle'.format(inpath))[1].split('\n') 
  collection = {}
  for f in files:
    ftag = re.sub('_[0-9]+MVA_[0-9]+','',f)
    if not ftag in collection:
      collection[ftag] = []
    collection[ftag].append(f)
  for ftag,pickles in collection.iteritems():
    newData = {}
    for ps in pickles:
      print ps
      with open(ps,'rb') as f:
        data = pickle.load(f)
      MergeDict(newData,data)
    fname = outpath+'/'+ftag.rsplit('/')[-1]
        
    with open(fname,'wb') as f:
      pickle.dump(newData,f)
      

        
    
    


#don't read these functions, not interesting
def ErrorHandler(err,defaultOut):
  def DecInside(fun):
    @functools.wraps(fun)
    def wrap(*args,**kw):
      try:
        out = fun(*args,**kw)
      except err:
        out = defaultOut
      return out
    return wrap
  return DecInside

def Dec(fun):
  @functools.wraps(fun)
  def fun_wrapper(*args,**kw):
    return list(fun(*args,**kw))
  return fun_wrapper
def update(x,y):
  z=copy.deepcopy(x)
  z.update(y)
  return z
def div(x,y):
    try:
        a = x/y
    except ZeroDivisionError:
        a = 0.0
    return a

#used to store data, same as TH1F, but lighter than
class Hist:
  def __init__(self,th1=None,bincontent=None,binerror=None):
    self.bincontent = []
    self.binerror = []
    self.stat = None
    if th1 != None:
      for i in range(0, th1.GetNbinsX()):
        self.bincontent.append(th1.GetBinContent(i+1))
        self.binerror.append(th1.GetBinError(i+1))
    elif bincontent!=None:
        self.bincontent.extend(bincontent)
        if binerror!=None:
          self.binerror.extend(binerror)
  def Getnbins(self):
    return len(self.bincontent)
  def Clear(self,v=0):
    self.binerror=[0]*self.Getnbins()
    self.bincontent=[v]*self.Getnbins()
  def sqrt(self):
    return Hist(bincontent = map(math.sqrt,self.bincontent))
  def ABS(self):
    binc = map(lambda x: x if x>0 else 0, self.bincontent)
    return Hist(bincontent = binc,binerror = self.binerror)
  def __add__(self,other):
    return Hist(bincontent=map(operator.add,self.bincontent,other.bincontent))
  def __sub__(self,other):
    return Hist(bincontent=map(operator.sub,self.bincontent,other.bincontent))
  def __mul__(self,other):
    if isinstance(other,Hist):
      return Hist(bincontent=map(operator.mul,self.bincontent,other.bincontent))
    else:
      return Hist(bincontent=map(lambda x:x*other,self.bincontent))
  def __div__(self,other):
    if isinstance(other,Hist):
      return Hist(bincontent=map(div,self.bincontent,other.bincontent))
    else:
      return Hist(bincontent=map(lambda x:x/other,self.bincontent))
  def __pow__(self,n):
    return Hist(bincontent=map(lambda x:x**n,self.bincontent))
  def __str__(self):
    return str(map('{0:.8f}'.format,self.bincontent))


class ResamplingHolder:
  def __init__(self,name,hist,tfile=None):
    assert(isinstance(hist,Hist))
    self.hists = []
    if not tfile == None:
      self.tfile = tfile
      self.tfile.cd()
    for n,value in enumerate(hist.bincontent):
      hname = '{0:}_bin{1:}'.format(name,n+1) 
      temp = R.TH1F(hname,hname,1000,0,2)
      temp.Fill(value)
      self.hists.append(temp)
  def Fill(self,hist):
    assert(isinstance(hist,Hist))
    assert(len(hist.bincontent)==len(self.hists))
    for n,value in enumerate(hist.bincontent):
      self.hists[n].Fill(value)
  def WriteToFile(self,tfile = None):
    if tfile != None or self.tfile != None:
      f = tfile if tfile != None else self.tfile
      f.cd()
    for hist in self.hists:
      hist.Write()

#returen a map(dict) which connect a key in lis to sum of fmts histos
#input: fmts = ['WW...{reg}','WZ...{reg}',...]  lis = ['PxP','PxT'...]
#output: {'PxT':Hist, 'PxP':Hist, ... } 
def RetrieveH(fmts,lis,tfile,scale_info=None):
  #Get the sum of a list(hnames) of histograms in 'tfile', could scale or rebin it
  def Gethist(tfile,hnames,scale_info=None):
    h = C.htemp.Clone()
    xbins = array.array('d',C.xbins)
    for hname in hnames:
      temp =  tfile.Get(hname)
      if temp == None:
        print 'not found ',hname
        continue
      if (scale_info != None) and scale_info[0].match(hname):
        if 'fake' in hname:
          print hname
          print scale_info[1]
        temp = temp.Clone()
        temp.Scale(scale_info[1])
      h.Add(temp)
    h = h.Rebin(C.nbins,'',xbins)
    h.SetBinContent(1,0.)
    h.SetBinError(1,0.)
    if hnames[0].find('data')==-1:
      h.Scale(C.mcsf)
    H = Hist(h).ABS()
    del h
    return H
  return { cat:Gethist(tfile,map(lambda x: x.format(cat),fmts),scale_info) for cat in lis }


#input:  fmt = '...{sam}...{{reg}}...' sam_lis = ['ZZ','WW','WZ'] reg_lis=['PxT','PxP'...]  
#output: {'PxT':Hist , 'PxP':Hist , ...}
def Retrieve(fmt,sam_lis_s,reg_lis,tfile,scale_info=None):
  if isinstance(sam_lis_s[0],list):
    tfile   = sam_lis_s[1]
    sam_lis = sam_lis_s[0]
  else:
    sam_lis = sam_lis_s
  fmts = map(lambda x:fmt.format(x),sam_lis)
  return RetrieveH(fmts,reg_lis,tfile,scale_info)

#input:
#  fmt = '...{sam}...{{reg}}...'  samples = {'ttbar':['ttbar'],'stop':['stopWt','stop_t'...],...}
#output:[ref_raw] 
#{
#  'tt':   {'PxP':Hist,  'PxT':Hist, ...}
#  'stop': {'PxP':Hist,  'PxT':Hist, ...},
#  'other':{'PxP':Hist,  'PxT':Hist, ...},
#}
def RetrieveMC(fmt,samples,scale_info=None):
  sam_o = []
  for sam in samples:
    if sam != 'tt' and sam != 'stop' and sam != 'z+jets':
      if isinstance(samples[sam][0],list):
        samlis = samples[sam][0]
      else:
        samlis = samples[sam]
      sam_o = sam_o + samlis
  rawmc = {}
  rawmc['tt'] = Retrieve(fmt,samples['tt'],['PxT','PxP','PbT','PbP','PjT','PjP'],C.mc,scale_info)
  rawmc['stop'] = Retrieve(fmt,samples['stop'],['PxT','PxP','PbT','PbP','PjT','PjP'],C.mc,scale_info)
  rawmc['z+jets'] = Retrieve(fmt,samples['z+jets'],['PxT','PxP','PbT','PbP','PjT','PjP'],C.mc,scale_info)
  rawmc['other'] = Retrieve(fmt,sam_o,['PxT','PxP','PbT','PbP','PjT','PjP'],C.mc,scale_info)
  return rawmc


#Random Generator for re-sampling ['PxP','PxT',...]
#input: raw = [ref_raw], wine = TRandom3()
#output:[ref_raw]
def Drunkwalker_x(raw,wine):
  def pwalker(tot,pas):
    Rtot = map(wine.Poisson,tot.bincontent)
    round_Rtot = map(lambda x:int(round(x)),Rtot)
    Rpas = map(wine.Binomial,round_Rtot,(pas/tot).bincontent)
    return Hist(bincontent=Rtot),Hist(bincontent=Rpas)
  def gwalker(tot,pas):
    Rtot = map(wine.Gaus,tot.bincontent,tot.binerror)
    ratio = (pas/tot).bincontent
    trans_0 = lambda args:map(lambda x:x if x>0 else 0,args)
    trans_1 = lambda args:map(lambda x:x if x<1 else 1,args)
    ratio = trans_0(trans_1(ratio))
    gerr = map(lambda x,y:x*math.sqrt(y*(1-y)),tot.binerror,ratio)
    Rpas = map(lambda x,y,z:wine.Gaus(x*y,z),Rtot,ratio,gerr)
    return Hist(bincontent=Rtot),Hist(bincontent=Rpas)
  Rraw = copy.deepcopy(raw)
  Rraw['tt']['PxT'],Rraw['tt']['PxP'] = gwalker(raw['tt']['PxT'],raw['tt']['PxP'])
  Rraw['tt']['PbT'],Rraw['tt']['PbP'] = gwalker(raw['tt']['PbT'],raw['tt']['PbP'])
  Rraw['tt']['PjT'],Rraw['tt']['PjP'] = gwalker(raw['tt']['PjT'],raw['tt']['PjP'])
  return Rraw

def Drunkwalker(raw,wine):
  def pwalker(tot,pas):
    Rtot = map(wine.Poisson,tot.bincontent)
    round_Rtot = map(lambda x:int(round(x)),Rtot)
    Rpas = map(wine.Binomial,round_Rtot,(pas/tot).bincontent)
    return Hist(bincontent=Rtot),Hist(bincontent=Rpas)
  def gwalker(tot,pas):
    Rtot = map(wine.Gaus,tot.bincontent,tot.binerror)
    ratio = (pas/tot).bincontent
    trans_0 = lambda args:map(lambda x:x if x>0 else 0,args)
    trans_1 = lambda args:map(lambda x:x if x<1 else 1,args)
    ratio = trans_0(trans_1(ratio))
    gerr = map(lambda x,y:x*math.sqrt(y*(1-y)),tot.binerror,ratio)
    Rpas = map(lambda x,y,z:wine.Gaus(x*y,z),Rtot,ratio,gerr)
    return Hist(bincontent=Rtot),Hist(bincontent=Rpas)
  Rraw = {'dt':{},'tt':{},'stop':{},'z+jets':{},'other':{}}
  Rraw['dt']['PxT'],Rraw['dt']['PxP'] = pwalker(raw['dt']['PxT'],raw['dt']['PxP'])
  Rraw['tt']['PxT'],Rraw['tt']['PxP'] = gwalker(raw['tt']['PxT'],raw['tt']['PxP'])
  Rraw['tt']['PbT'],Rraw['tt']['PbP'] = gwalker(raw['tt']['PbT'],raw['tt']['PbP'])
  Rraw['tt']['PjT'],Rraw['tt']['PjP'] = gwalker(raw['tt']['PjT'],raw['tt']['PjP'])
  Rraw['stop']['PxT'],Rraw['stop']['PxP'] = gwalker(raw['stop']['PxT'],raw['stop']['PxP'])
  Rraw['stop']['PbT'],Rraw['stop']['PbP'] = gwalker(raw['stop']['PbT'],raw['stop']['PbP'])
  Rraw['stop']['PjT'],Rraw['stop']['PjP'] = gwalker(raw['stop']['PjT'],raw['stop']['PjP'])
  Rraw['z+jets']['PxT'],Rraw['z+jets']['PxP'] = gwalker(raw['z+jets']['PxT'],raw['z+jets']['PxP'])
  Rraw['z+jets']['PbT'],Rraw['z+jets']['PbP'] = gwalker(raw['z+jets']['PbT'],raw['z+jets']['PbP'])
  Rraw['z+jets']['PjT'],Rraw['z+jets']['PjP'] = gwalker(raw['z+jets']['PjT'],raw['z+jets']['PjP'])
  Rraw['other']['PxT'],Rraw['other']['PxP'] = gwalker(raw['other']['PxT'],raw['other']['PxP'])
  Rraw['other']['PbT'],Rraw['other']['PbP'] = gwalker(raw['other']['PbT'],raw['other']['PbP'])
  Rraw['other']['PjT'],Rraw['other']['PjP'] = gwalker(raw['other']['PjT'],raw['other']['PjP'])
  return Rraw

#input:[ref_raw]
#output:[ref_dish]
#  {'sf':Hist', e_tt':Hist, 'f_tb':Hist }
def Cook(raw,is_fake=False):
  dt = raw['dt']
  tt = raw['tt']
  nt = {}
  for key in raw['stop']:
    nt[key] = raw['z+jets'][key] +  raw['stop'][key]+raw['other'][key]
  dish = {}
  if is_fake:
    dish['e_tt'] = (dt['PxP']-nt['PxP'])/(dt['PxT']-nt['PxT'])
  else:
    dish['e_tt'] = (dt['PxP']-nt['PbP']-nt['PjP'])/(dt['PxT']-nt['PbT']-nt['PjT'])

  dish['f_tb'] = tt['PbT']/(tt['PbT']+tt['PjT'])
  dish['e_nb'] = tt['PjP']/tt['PjT']
  dish['e_mc'] = tt['PbP']/tt['PbT'] 
  I = Hist(bincontent=[1]*(dish['f_tb'].Getnbins()))
  dish['e_dt'] = (dish['e_tt']-dish['e_nb']*(I-dish['f_tb']))/dish['f_tb']
  dish['sf'] = dish['e_dt']/dish['e_mc']
  return dish


def StatCalculator_x(raw,walker_x):
  holder = {} 
  r = R.TRandom3()
  for i in xrange(C.nLoop):
    Rraw = walker_x(raw,r)
    Rdish = Cook(Rraw)
    for item in Rdish:
      if item not in holder:
        holder[item]={'m1':Rdish[item]/C.nLoop,'m2':(Rdish[item]**2)/C.nLoop}
      else:
        holder[item]['m1']+=(Rdish[item]/C.nLoop)
        holder[item]['m2']+=(Rdish[item]**2)/C.nLoop
  disherr={}
  for key in Rdish:
    var=(holder[key]['m2']-holder[key]['m1']**2).bincontent
    var=map(lambda x:0.0 if x>-1e-12 and x<1e-12 else x,var)
    disherr[key] = Hist(bincontent=map(math.sqrt,var))
  return disherr



#Get stat error by resampling
#input: raw = [ref_raw]  walker = Drunkwalker
#output:[ref_stat] { 'dt':[ref_dish] 'mc':[ref_dish] }  
def StatCalculator(raw,walker):
  holder = {'dt':{},'mc':{}} #dt/mc->e_tt/f_tb/.../->m1/m2
  if C.resampling_plots:
    r_holder = {'dt':{},'mc':{}}

  r = R.TRandom3()
  for i in xrange(C.nLoop):
    Rraw = walker(raw,r)
    dtraw = update(raw,{'dt':Rraw['dt']})
    mcraw = update(Rraw,{'dt':raw['dt']})
    Rdish = {  'dt':Cook(dtraw), 'mc':Cook(mcraw)  }
    for key in Rdish:
      for item in Rdish[key]:
        if item not in holder[key]:
          if C.resampling_plots:r_holder[key][item] = ResamplingHolder('R_MVA%s_WP%s_%s_%s'%(C.currentMVA,C.currentWP,key,item),Rdish[key][item])
          holder[key][item]={'m1':Rdish[key][item]/C.nLoop,'m2':(Rdish[key][item]**2)/C.nLoop}
        else:
          if C.resampling_plots:r_holder[key][item].Fill(Rdish[key][item])
          holder[key][item]['m1']+=(Rdish[key][item]/C.nLoop)
          holder[key][item]['m2']+=(Rdish[key][item]**2)/C.nLoop
  if C.resampling_plots:
    for key,value in r_holder.iteritems():
      for _key,_value in value.iteritems():
        _value.WriteToFile(C.resampling_out)
          
  disherr={}
  for stat in Rdish:
    disherr[stat]={}
    for key in Rdish[stat]:
      var=(holder[stat][key]['m2']-holder[stat][key]['m1']**2).bincontent
      var=map(lambda x:0.0 if x>-1e-12 and x<1e-12 else x,var)
      disherr[stat][key] = Hist(bincontent=map(math.sqrt,var))
  return disherr

#Get the detector related systematic items from the TDirectories in the mc input file.
#output: {'EL_MUON_SYS': ['EL_MUON_SYS_1down', 'EL_MUON_SYS_1up'], ... } 
def Getvars(tfile):
  systs_var = {}
  ptn = re.compile(r'_*1*up$|_*1*down$')
  for i in tfile.GetListOfKeys():
    obj = i.ReadObj()
    name = obj.GetName()
    cls_name = obj.ClassName()
    if name.find('Nominal')!=-1 or cls_name.find('TDirectory')==-1:
      continue
    if name.find('SysLUMI')!=-1:
      continue
    key = ptn.split(name)[0]
    if (key in systs_var):
      systs_var[key].append(name)
    else:
      systs_var[key] = [name]
  for key in systs_var: 
    if len(systs_var[key])==1:
      systs_var[key].append('Nominal')
  return systs_var

#Calculate the detector related systematics 
#output:[ref_syst] { 'EL_MUON_SYS':[ref_dish], ... }
def SystCalculator(dt,systs):
  systs_err = {}
  for item in systs:
    raw_pair = [ update(systs[item][key],{'dt':dt}) for key in [0,1] ]
    systs_err[item] = DifferCalculator(raw_pair)
  return systs_err

#Calculate the systematics from mc mis-modelling
#input: nominal = [ref_dish]  
#input: models = { 
#  'stop':{'radioation':[ref_dish, ref_dish],  'fragmetation':[...]},
#  'ttbar':... 
#}
#output[ref_model]:
#{
#  'stop':{'redioation':[ref_dish], 'fragmetation':[ref_dish], ... },
#  'ttbar':{...},
#}
def ModellingCalculator(nominal,models):
  modelling_err = {}
  for mod in models:
    modelling_err[mod]={}
    for item in models[mod]:
      raw_pair = [ update(nominal,{mod:models[mod][item][key]}) for key in [0,1] ]
      modelling_err[mod][item] = DifferCalculator(raw_pair)
  return modelling_err

def ModellingCalculator_y(nominal,models):#hybrid
  modelling_err = {}
  for mod in models:
    modelling_err[mod] = {}
    if mod == 'tt':
      modelling_err[mod] = ModellingHybrid(nominal,models[mod])
    else:
      for item in models[mod]:
        raw_pair = [ update(nominal,{mod:models[mod][item][key]}) for key in [0,1] ]
        modelling_err[mod][item] = DifferCalculator(raw_pair)
  return modelling_err
  
def ModellingHybrid(nominal,models):
  raws = {}
  modelling_hybrid = {}
  for item in models:
    key_do = C.tt_cfg[item][0]
    key_up = C.tt_cfg[item][1]
    if not key_do in raws:
      raws[key_do] = update(nominal,{'tt':models[item][0]})
    if not key_up in raws:
      raws[key_up] = update(nominal,{'tt':models[item][1]})
    modelling_hybrid[item] = DifferCalculator( [ raws[key_do], raws[key_up] ] )
  AppendPackErr(modelling_hybrid,raws)
  return modelling_hybrid

def AppendPackErr(modelling_hybrid,raws):
  holder = {}
  items = modelling_hybrid.keys()
  for item in items + ['pack']:
    holder[item] = {}
    for var in modelling_hybrid[items[0]]:
      holder[item][var] = {}
  r = R.TRandom3()
  walker = lambda x:Drunkwalker_x(raws[x],r)
  for n in xrange(C.nLoop):
    R_raws = {key:walker(key) for key in raws}
    pack = GetPack(R_raws)
    for key,value in pack.iteritems():
      for _key,_value in value.iteritems():
        if not 'm1' in  holder[key][_key]:
          holder[key][_key]['m1'] = _value/C.nLoop
        else:
          holder[key][_key]['m1'] += _value/C.nLoop
        if not 'm2' in  holder[key][_key]:
          holder[key][_key]['m2'] = _value**2/C.nLoop
        else:
          holder[key][_key]['m2'] += _value**2/C.nLoop
  for key,value in holder.iteritems():
    if key not in modelling_hybrid:
      modelling_hybrid[key] = {}
    for _key,_value in value.iteritems():
      assert( (key=='pack') or (_key in modelling_hybrid[key]) )
      var = (_value['m2']-_value['m1']**2).bincontent
      var = map(lambda x:0.0 if x>-1e-12 and x<1e-12 else x,var)
      if key=='pack':
        modelling_hybrid[key][_key] = Hist(bincontent=map(math.sqrt,var))
      else:
        modelling_hybrid[key][_key+'_stat'] = Hist(bincontent=map(math.sqrt,var))
  #T.Look(modelling_hybrid)    
def GetPack(raws):
  pack = {}
  psum = {}
  for key,value in C.tt_cfg.iteritems():
    pack[key] = DifferCalculator([raws[value[0]],raws[value[1]]])
    for _key,_value in pack[key].iteritems():
      if not _key in psum:
        psum[_key] = _value
      else:
        psum[_key] = (psum[_key]**2 + _value**2).sqrt()
  pack['pack'] = psum
  return pack

def ModellingCalculator_x(nominal,models):
  modelling_err = {}
  for mod in models:
    modelling_err[mod]={}
    for item in models[mod]:
      raw_pair = [ update(nominal,{mod:models[mod][item][key]}) for key in [0,1] ]
      modelling_err[mod][item] = DifferCalculator_x(raw_pair)
  return modelling_err

def DifferCalculator_x(raw_pair):
     model = DifferCalculator(raw_pair)
     stat_up = StatCalculator_x(raw_pair[1],Drunkwalker_x)
     stat_do = StatCalculator_x(raw_pair[0],Drunkwalker_x)
     for key in stat_up:
       model[key] = ((stat_up[key]**2+stat_do[key]**2)/4.+model[key]**2).sqrt()
     return model

def DifferCalculator(raw_pair,is_fake=False):
  up = Cook(raw_pair[0],is_fake)
  do = Cook(raw_pair[1],is_fake)
  differ = {}
  for key in up:
    differ[key] = Hist(bincontent=map(abs,(up[key]/2-do[key]/2).bincontent))
  return differ


def Dump(data,mu,eta,mva,wp,name):
  pname_pre = '{path:}/{jet:}_{tag:}'.format(path=C.outPickles,jet=C.runmode,tag=C.runtag)
  pname_post = '{mu:}{eta:}_{tt:}_{mva:}MVA_{wp:}.{name:}.pickle'.format(mu=mu,eta=eta,tt=C.tail,mva=mva,wp=wp,name=name)
  pname = pname_pre + pname_post
  with open(pname,'wb') as f:
    pickle.dump(data,f)
    print '\n\n\npicke file generated:\n',pname,'\n\n'
  return pname

#input: args = [mva_wp,mv2c10_wp]
#output: (results, mva_wp,mv2c10_wp)
#results = {
#  'nominal':[ref_dish],
#  'stat':[ref_stat],
#  'syst':[ref_syst],
#  'model':[ref_model],
#}
def GetResults(mva_wp,wp,mu_bin,eta_bin,systs):
  C.currentWP = wp
  C.currentMVA = mva_wp
  print ('{2:} mva {0:} wp, mv2c10 {1:} wp started'.format(mva_wp,wp,C.runmode)).center(40)
  fmt_dt = r'SysNominal/data_TP_1ptag2jet_MVA'+mva_wp+mu_bin+'_em'+eta_bin+'_{}'+wp+C.runmode+'JetPt'
  fmt_mc = r'SysNominal/{}_TP_1ptag2jet_MVA'+mva_wp+mu_bin+'_em'+eta_bin+'_{{}}'+wp+C.runmode+'JetPt'
  fmt_sys = r'{0}/{{}}_TP_1ptag2jet_MVA'+mva_wp+mu_bin+'_em'+eta_bin+'_{{{{}}}}'+wp+C.runmode+'JetPt_{0}'
  raw_nominal = {}
  raw_nominal['dt'] = RetrieveH([fmt_dt],['PxT','PxP'],C.data)
  raw_nominal.update(RetrieveMC(fmt_mc,C.MCSamples))
  raw_modelling = {} #tt/stop->[up(->PxP,PxT),do]
  #tag
  for sam in C.SysModelling:
    reglis = ['PxT','PxP','PjT','PjP','PbT','PbP']
    raw_modelling[sam] = {}
    for sysitem in C.SysModelling[sam]:
      raw_up = Retrieve(fmt_mc,sysitem[1],reglis,C.mc)
      raw_do = Retrieve(fmt_mc,sysitem[2],reglis,C.mc)
      raw_modelling[sam][sysitem[0]] = [raw_up,raw_do]
  raw_sys = {}
  if not C.onlyNominal:
    keys = systs.keys()
    for sys in keys[2:]:
      
      if sys!='SysJET_BJES_Response':
        pass
        #continue
      raw_sys[sys]=[]
      for item in systs[sys]:
        if item.find('Nominal')!=-1:
          tmp=fmt_mc
        else:
          tmp=fmt_sys.format(item)
        sys_updo = RetrieveMC(tmp,C.MCSamples)
        raw_sys[sys].append(sys_updo)
  dish_nominal = Cook(raw_nominal)
  stat = StatCalculator(raw_nominal,Drunkwalker)
  if not C.onlyNominal: 
    syst = SystCalculator(raw_nominal['dt'],raw_sys);
  if C.run_hybrid:
    modelling = ModellingCalculator_y(raw_nominal,raw_modelling)
  elif not C.run_hybrid:
    modelling = ModellingCalculator_x(raw_nominal,raw_modelling)
  if not C.onlyNominal: results = {'nominal':dish_nominal,'stat':stat,'syst':syst,'model':modelling,'raw':raw_nominal};
  else: results = {'nominal':dish_nominal,'stat':stat,'model':modelling,'raw':raw_nominal};
  #Wt scale and nonettbarB scale
  for key_norm in C.scales:
    raw_scale = [ update(raw_nominal,RetrieveMC(fmt_mc,C.MCSamples,C.scales[key_norm][key])) for key in ['up','do'] ]
    is_fake = True if 'fake' in  key_norm.lower() else False
    scaled = DifferCalculator(raw_scale,is_fake) 
    results.update({key_norm:scaled})
  return results 

def star_GetResults(arg):
  return GetResults(*arg)

def Fun(mu_bin,eta_bin,mva_wp,wp,systs):
  results = GetResults(mva_wp,wp,mu_bin,eta_bin,systs)
  pickles = MakePickle(mva_wp,wp,mu_bin,eta_bin,results)
  return pickles


def MakePickle(mva_wp,wp,mu_bin,eta_bin,results):
  
  #doesn't interesting
  out = lambda x:map('{:.6f}'.format,x)[1:]
  out_l = lambda x:map('{:.6f}'.format,x)[1:]
  getsum2 = lambda x: reduce(lambda _x,_y:(_x**2+_y**2).sqrt(),x)
  sum2 = lambda x: reduce(lambda a,b:math.sqrt(a**2+b**2),x)
  
  #interface functions to read info from totResults[mva_wp][mv2c10_wp]
  #all these functions return python list
  #x = 'sf','e_nonb','f_tb'.... for all these functions 
  nominal = lambda x:results['nominal'][x].bincontent 
  stat = lambda x,y:results['stat'][y][x].bincontent #y = 'mc','dt'
  model = lambda x,y:{key:results['model'][y][key][x] for key in results['model'][y]} #y = 'tt','stop
  detecsum = lambda x:getsum2([results['syst'][key][x] for key in results['syst']]).bincontent
  
  def modelsum_x(x,y):
    modelsum = []
    for key in results['model'][y]:
      if key == 'pack':
        continue
      modelsum.append(results['model'][y][key][x])
    return getsum2(modelsum).bincontent

  def modelsum_y(x,y):
    h = Hist(bincontent=modelsum_x(x,y)) + results['model'][y]['pack'][x]
    return h.bincontent
    
  pack_tt = lambda x:results['model']['tt']['pack'][x].bincontent 
  
  keys = C.SysModelling.keys()

  print 'keys',keys
  modelsum_X = lambda x:map(sum2,zip(*tuple(modelsum_x(x,k) for k in keys)))
#  modelsum_X = lambda x:map(sum2,zip(modelsum_x(x,'tt'),modelsum_x(x,'stop'),modelsum_x(x,'z+jets'))) 

  #get dict
  detec_dict = lambda x:{key:results['syst'][key][x].bincontent for key in results['syst']}
  def mod_dict(x,y):
    mod_out = {}
    for key,value in results['model'][y].iteritems():
      if not x in results['model'][y][key]:
        continue
      mod_out['mod_%s_%s'%(y,key)] = copy.deepcopy(results['model'][y][key][x].bincontent)
    return mod_out

  def modstat_dict(x,y):
    mod_out = {}
    for key,value in results['model'][y].iteritems():
      if not x in results['model'][y][key]:
        continue
      mod_out['modstat_%s_%s'%(y,key)] = copy.deepcopy(results['model'][y][key][x].bincontent)
    return mod_out

  def wrap_norm(name):
    def fun(x):
      res = results[name][x].bincontent
      return res
    return fun

  stat_mc = lambda x:stat(x,'mc')
  stat_dt = lambda x:stat(x,'dt')

  norm_fun = {}
  tuple_tot = (stat_mc,stat_dt)
  #tuple_tot = (modelsum_X,stat_mc,stat_dt)
  for key_norm in C.scales:
    norm_fun[key_norm] = wrap_norm(key_norm)
    tuple_tot += (norm_fun[key_norm],)
  if not C.onlyNominal: 
    tuple_tot += (detecsum,)
    systsum = lambda x:map(sum2,zip(detecsum(x),stat(x,'mc')))
    #systsum = lambda x:map(sum2,zip(modelsum_X(x),detecsum(x),stat(x,'mc')))
  else: 
    systsum = lambda x:map(sum2,zip(stat(x,'mc')))
    #systsum = lambda x:map(sum2,zip(modelsum_X(x),stat(x,'mc')))
     
  fun_tot = lambda args:lambda x:map(sum2,zip(*(key(x) for key in args)))
  toterr = fun_tot(tuple_tot)

  #validation printing
  print 'mva ',mva_wp,' mv2c10 ',wp,' sf      ',out(nominal('sf'))

  pickles = {}
  stag = '{0:}MVA_{1:}'.format(mva_wp, wp)

  if C.is_fill_datapool:
    DataPool = {}
    print out_l(toterr('sf'))
    print 'syst',out_l(systsum('sf'))
    print 'modsys',out_l(modelsum_X('sf'))
    print 'stat',out_l(stat('sf','dt'))
    print 'detect',out_l(detecsum('sf'))
    DataPool['{}MVA'.format(mva_wp)]={}
    DataPool['{}MVA'.format(mva_wp)][wp]={
        'sys':out_l(systsum('sf')),
      'modsys':out_l(modelsum_X('sf')),
        'stat':out_l(stat('sf','dt')),
      'mcstat':out_l(stat('sf','mc')),
        'total':out_l(toterr('sf')),
        'sf':out_l(nominal('sf')),
        'bf':out_l(nominal('f_tb')),
        'bf stat':out_l(stat('f_tb','mc')),
        'e_dtsys':out_l(systsum('e_dt')),
      'e_dtmodsys':out_l(modelsum_X('e_dt')),
        'e_dtstat':out_l(stat('e_dt','dt')),
      'e_dtmcstat':out_l(stat('e_dt','mc')),
        'e_dttotal':out_l(toterr('e_dt')),
        'e_dte_dt':out_l(nominal('e_dt')),
        'e_mcsys':out_l(systsum('e_mc')),
      'e_mcmodsys':out_l(modelsum_X('e_mc')),
        'e_mcstat':out_l(stat('e_mc','dt')),
      'e_mcmcstat':out_l(stat('e_mc','mc')),
        'e_mctotal':out_l(toterr('e_mc')),
        'e_mc':out_l(nominal('e_mc')),
      }

    for key_norm in C.scales:
      DataPool['{}MVA'.format(mva_wp)][wp].update({key_norm:out_l(norm_fun[key_norm]('sf'))}) 
    if not C.onlyNominal: 
      DataPool['{}MVA'.format(mva_wp)][wp].update({'detsys':out_l(detecsum('sf'))})
    pickles['DP'] = {}
    pickles['DP'][stag] = Dump(DataPool,mu_bin,eta_bin,mva_wp,wp,'DP')
  if C.is_fill_cdipool  and ((C.runmode == 'Cal' and mva_wp=='80') or (C.runmode == 'Trk' and mva_wp=='70')):
    mod_tt = mod_dict('sf','tt')
    mod_st = mod_dict('sf','stop')
    mod_zj = mod_dict('sf','z+jets')
    njets = results['raw']['dt']['PxT'].bincontent
    ntagged = results['raw']['dt']['PxP'].bincontent

    if not C.onlyNominal:
      dec = detec_dict('sf')
      sys_cdi = update({'mc_stat':stat('sf','mc')},update(dec,update(mod_tt,mod_st)))
    else:
      sys_cdi = update({'mc_stat':stat('sf','mc')},update(mod_tt,mod_st)) 
      dec = {}
    
    CDIPool = {}
    CDIPool[wp] = {
        'sf':nominal('sf'),
        'stat':stat('sf','dt'),
      'sys':systsum('sf'),
      'total':toterr('sf'),
      'systs':sys_cdi,
      'detecsys':dec,
      'mod':update(mod_tt,mod_st),
      'n_jets':njets,
      'n_tagged':ntagged,
      #'norm wt':norm_wt('sf'),
      #'norm ntB':norm_ntB('sf'),
    }
    pickles['CP'] = {}
    pickles['CP'][stag] = Dump(CDIPool,mu_bin,eta_bin,mva_wp,wp,'CP')
    
  if C.is_fill_sea and not C.onlyNominal:
    Pasific = {} 
    Pasific['%sMVA'%mva_wp] = {}
    Pasific['%sMVA'%mva_wp][wp] = {}
    Pasific['%sMVA'%mva_wp][wp]['raw'] = results['raw'],
    for key in ['sf','f_tb','e_nb','e_mc','e_dt','e_tt']:
      keys = C.SysModelling.keys()
      
      models = [mod_dict(key,k) for k in keys]
      if 'tt' in keys:
        models += [modstat_dict(key+'_stat','tt')]
        
      dict_model = reduce(update,models,{})
      Pasific['%sMVA'%mva_wp][wp][key] = {
        'nominal'    : nominal(key),
        'dt_stat'       : stat(key,'dt'),
        'mc_stat'     : stat(key,'mc'),
        'syst'       : systsum(key),
        'total'      : toterr(key),
        'model'      : modelsum_X(key),

        '''
        'tt_model'   : modelsum_x(key,'tt'),
        'stop_model' : modelsum_x(key,'stop'),
        'z+jets_model':modelsum_x(key,'z+jets'),
        '''
        'dict_model' : dict_model,
        'dict_systs' : detec_dict(key),
      }
      for k in C.SysModelling.keys():
        update(Pasific['%sMVA'%mva_wp][wp][key] ,{'%s_model'%(k):modelsum_x(key,k)})
      for key_norm in C.scales:
        Pasific['%sMVA'%mva_wp][wp][key].update({key_norm:norm_fun[key_norm](key)})
    pickles['OS'] = {}
    pickles['OS'][stag] = Dump(Pasific,mu_bin,eta_bin,mva_wp,wp,'OS')
  return pickles




def main(info):

  if not info['usingOptimisedWP']:
    C.mva_wps = info['mva']
  else:
    C.mva_wps = [info['mvaOpts'][C.runmode]]

  C.is_mu_cali = info['isMuCali']
  C.is_eta_cali = info['isEtaCali']

  C.wps = info['mv2c10']
  C.varPickles = os.environ['PWD'] + '/' + info['input_tag']
  C.outPickles = info['pickle_dir']
  C.FixParameters()
  C.SysModelling = {}

  varpickle = '{0:}/var.pickle'.format(C.varPickles)
  with open(varpickle,'rb') as f:
    systs = pickle.load(f)

  if C.is_mu_cali and C.is_eta_cali:
    raise ValueError('can\'t do is_mu_cali and is_eta_cali simultaneouly')  

  pickles = {}
  for mu_bin in C.mu_bins:
    for eta_bin in C.eta_bins :
      mu_eta = '{0:}{1:}'.format(mu_bin,eta_bin)
      pickles[mu_eta] = {}
      for wp in C.wps:
        for mva in C.mva_wps:
          pks = Fun(mu_bin,eta_bin,mva,wp,systs)
          print pks
          MergeDict(pickles[mu_eta],pks)
  print pickles

  return pickles

sys.path.append("/sps/atlas/c/ccheng/BtaggingInputsProcessor/Jan.18.2018.Test/pickles/p4All")#TVAR1
from Cfg_generate import *
C = Config()

if __name__ == '__main__':
  print 'in __main__'
  path = './Jan.18.2018.Test/pickles/'
#  path = './Dec.01.AddStopNlo/pickles/'
  for p in ['p4All']:#'p2Com','p2.mu','p2.eta']:
    pathin = path + p 
    pathout = pathin + '/sum'
    MergePickles(pathin,pathout)
#  main(info)

