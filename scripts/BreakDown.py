import toolkit
import math
import re
from copy import copy,deepcopy
import commands

class BreakDown(toolkit.IOHandler):
    label = 1
    def __init__(self,output_path,version='r21.old',variable=['ScaleFactor','Scale factor','sf']):
        self.uncertainties = GroupSystmatics().GetUncertainties(version)
        self.output_path = '{0:}/table'.format(output_path,)
        self.Name = variable[0]
        self.head = variable[1]
        self.key = variable[2]       
        self.FooSum2 = lambda x:list(reduce(lambda _x,_y:map(lambda __x,__y:math.sqrt(__x**2+__y**2),_x,_y),x))
        self.config_default = {
            'width':270,
            'height':270,
            't_b_l_rMargin':[2,2,2,2],
            'scale':1.5,
        }

        toolkit.mkdir(self.output_path)

    def GetTexAllFix(self,tex_name,input_json,alter_json,intervals,title):        
        entriesA = self._getEntries(input_json,readPickle=True)
        entriesB = self._getEntries(alter_json,readPickle=False)
        entries = self._updateEntries(entriesA, entriesB)

        name = tex_name + '_group_fixed'
        self._getTex({'height':270},name,entries,intervals,title,isGroup=True)
        name = tex_name + '_detail_fixed'
        self._getTex({'height':480},name,entries,intervals,title,isGroup=False)

    def GetTexAll(self,tex_name,input_json,intervals,title,readPickle=False):
        entries = self._getEntries(input_json,readPickle)

        name = tex_name + '_group'
        self._getTex({'height':270},name,entries,intervals,title,isGroup=True)
        name = tex_name + '_detail'
        self._getTex({'height':480},name,entries,intervals,title,isGroup=False)    

    def _addEntry(self,tab_list,entries,isGroup=True,isPercentage=False,entries_alter=None):
        tot = entries[self.head]
        nbins = len(tot)
        if isPercentage:
            fmt = lambda errs:list(map(lambda x,y:'{0:.1f}'.format(100.*(x/y)),errs,tot))
        else:
            fmt = lambda errs:list(map(lambda x:'{0:.3f}'.format(x),errs))

        def AppendSys(name,entry):
            if entry == None:
                content = [name] + ['-']*nbins
            else:
                content = [name] + fmt(entry)
            content_str = ' & '.join(content) + r'\\'
            tab_list.append(content_str)

        def AddEntry(name):
            if not name in entries: #systs not known
                self.FBIWarning('{0:} not even registered !'.format(name))
                AppendSys(name,None)
            elif isinstance(entries[name],list): # nominal/stat/syst/total
                AppendSys(name,entries[name]) 
            elif len(entries[name]) == 0: # empty systs
                if isGroup or len(self.uncertainties[name])==1:
                    AppendSys(name,None)
                else:
                    for itm in self.uncertainties[name]:
                        AppendSys(itm,None)
            elif len(self.uncertainties[name]) == 1: # single systs
                AppendSys(name,entries[name].values()[0])
            else: # multiple systs
                if not isGroup:
                    for itm in self.uncertainties[name]:
                        itm_regular = re.sub('_','\_',itm)
                        entry = entries[name][itm] if itm in entries[name] else None                    
                        AppendSys(itm_regular,entry)
                else:
                    init = [0.] * nbins
                    entry = self.FooSum2(entries[name].values() + [init])    
                    AppendSys(name,entry)
        return AddEntry

    def _getEntries(self,input_json,readPickle=False):
        def WrapGetter(data):
            def getter(key):
                if readPickle:
                    entry = toolkit.Searcher(data,nameMap)(key)
                else:
                    entry = data.get(key)
                return entry
            return getter

        nameMap = GroupSystmatics().MapPickle()
        data = WrapGetter(toolkit.json_load(input_json))(self.key)
        getter = WrapGetter(data)
        nominal = getter('nominal')[1:]
        stat = getter('data stats')[1:]
        systs = []
        entries = {}
        for name, uncertainty_group in self.uncertainties.iteritems():
            group = {}
            for item in uncertainty_group:
                entry = getter(item)
                if not entry:
                    self.Warning('skip {0:}'.format(item))                    
                else:
                    group[item] = entry[1:]
                    systs.append(entry[1:])
            entries[name] = group
        syst_sum = self.FooSum2(systs)
        total = self.FooSum2([syst_sum,stat])
        entries[self.head] = nominal
        entries[r'Statistical uncertainty'] = stat
        entries[r'Systematic uncertainty'] = syst_sum
        entries[r'Total uncertainty'] = total
        return entries

    def _maketabularList(self,entries,tabular_list,addEntry,addEntryP,intervals):
        nBins = len(entries[self.head])+1
        tabular_list.append( r'\begin{tabular}{l'+r'|r'*(nBins-1)+r'}' )
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\multicolumn{'+str(nBins)+r'}{c}{T\&P Method} \\')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        tabular_list.append(intervals)
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        addEntry(self.head)
        addEntry(r'Total uncertainty')
        addEntry(r'Statistical uncertainty')
        addEntry(r'Systematic uncertainty')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\multicolumn{'+str(nBins)+r'}{c}{Systematic Uncertainties [\%]} \\')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        addEntryP(r'Matrix element modelling ($t\bar{t}$)')
        addEntryP(r'Parton shower / Hadronisation ($t\bar{t}$)')
        addEntryP(r'NNLO top $p_{T}$, $t\bar{t}$ $p_{T}$ reweighting ($t\bar{t}$)')
        addEntryP(r'PDF reweighting ($t\bar{t}$)')
        addEntryP(r'More / less radiation ($t\bar{t}$)')
        addEntryP(r'Matrix element modelling (single top)')
        addEntryP(r'Parton shower / Hadronisation (single top)')
        addEntryP(r'More / less radiation (single top)')
        addEntryP(r'DR vs. DS (single top)')
        addEntryP(r'Modelling (Z+jets)')
        #addEntryP(r'Z $p_{T}$ reweighting')
        tabular_list.append(r'\hline')
        addEntryP(r'Limited size of simulated samples')
        tabular_list.append(r'\hline')
        addEntryP(r'Normalisation single top')
        addEntryP(r'Normalisation Z+jets')
        addEntryP(r'Normalisation Z+b/c')
        addEntryP(r'Normalisation diboson')
        addEntryP(r'Normalisation misid. leptons')
        tabular_list.append(r'\hline')
        addEntryP(r'Pile-up reweighting')
        addEntryP(r'Electron efficiency/resolution/scale/trigger')
        addEntryP(r'Muon efficiency/resolution/scale/trigger')
        addEntryP(r'$E_{T}^{miss}$')
        addEntryP(r'JVT')
        addEntryP(r'Jet energy scale (JES)')
        addEntryP(r'Jet energy resolution (JER)')
        addEntryP(r'Light-flavour jet mis-tag rate')
        addEntryP(r'c-jet mis-tag rate')
        addEntryP(r'Luminosity (3.2\%)')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\bottomrule')
        tabular_list.append(r'\end{tabular}')
        return tabular_list
        
    def _wrapTable(self,config,tabular_list,title,table_number):
        tabular_list = copy(tabular_list)
        tabular_list.insert(0,r'\scalebox{{{0:}}}[{0:}]{{'.format(config['scale']))
        tabular_list.append(r'}')
        
        
        tabular_list.insert(0,r'\begin{table}[htbp]') 
        tabular_list.insert(1,r'\renewcommand\thetable{'+str(table_number)+'}')
        tabular_list.insert(2,r'\centering')
        
        tabular_list.append(r'\captionsetup{font=large}')
        tabular_list.append(r'\caption{'+title+'}')
        tabular_list.append(r'\end{table}')

        return tabular_list
    def _wrapDocument(self,table,config):
        table = copy(table)
        table.insert(0, r'\begin{document}')
        table.append(r'\end{document}')

        table.insert(0,r'\documentclass{article}')
        table.insert(1,r'\usepackage{booktabs}')
        table.insert(2,r'\usepackage{graphics}')
        table.insert(3,r'\usepackage{caption}')
        table.insert(4,r'\usepackage[paperwidth={0:}mm,paperheight={1:}mm]{{geometry}}'.format(config['width'],config['height']))
        table.insert(5,r'\geometry{{tmargin={0:}mm,bmargin={1:}mm,lmargin={2:}mm,rmargin={3:}mm}}'.format(*config['t_b_l_rMargin']))
        return table

    def _dumpTex(self,name,tabular_list):
        tex_path = '{0:}/{1:}_{2:}.tex'.format(self.output_path,self.Name,name)
        with open(tex_path,'w') as f:
            for line in tabular_list:
                f.write(line+'\n')
        return tex_path

    def _makePDF(self,input_tex):
        res = commands.getstatusoutput('pdflatex -halt-on-error -output-directory={0:} {1:}'.format(self.output_path,input_tex))
        if res[0]:
            raise  RuntimeError(res[1])
        else:
            commands.getstatusoutput('rm {0:}'.format(re.sub('.tex$','.log',input_tex)))
            commands.getstatusoutput('rm {0:}'.format(re.sub('.tex$','.aux',input_tex)))
            pdf_status = commands.getstatusoutput('ls {0:}'.format(re.sub('.tex$','.pdf',input_tex)))
            if not pdf_status[0]:
                self.Stdout('PDF file generated',pdf_status[1])
            else:
                raise RuntimeError('PDF not founed: {0:}'.format(pdf_status[1]))

    def _getInterval(self,interval_list):
       nbins = len(interval_list)-1
        interval_str_list = [r'$p_{T}$ Interval [GeV]']
        for n in range(nbins):
            interval_str_list.append('{0:}-{1:}'.format(interval_list[n],interval_list[n+1]))
        interval_str = ' & '.join(interval_str_list)
        interval_str += r'\\'
        return interval_str

    def _updateEntries(self,entriesA,entriesB):
        entries = deepcopy(entriesA)
        for name,items in self.uncertainties.iteritems():
            for itm in items:
                if not itm in entriesA[name]:
                    if itm in entriesB[name]:
                        entries[name][itm] = entriesB[name][itm]
        return entries

    def _getTex(self,config,tex_name,entries,intervals,title,isGroup):
        config = deepcopy(config)
        config.update(self.config_default)
        tabular_list = []
        addEntry = self._addEntry(tabular_list,entries,isGroup,isPercentage=False)
        addEntryP = self._addEntry(tabular_list,entries,isGroup,isPercentage=True)
        intervals = self._getInterval(intervals)
        tabular_list = self._maketabularList(entries,tabular_list,addEntry,addEntryP,intervals)

        table = self._wrapTable(config,tabular_list,title,type(self).label)
        document = self._wrapDocument(table,config)
        tex_path = self._dumpTex(tex_name,document)
        self._makePDF(tex_path)
        type(self).label += 1

class GroupSystmatics(object):
    def __init__(self):
        self.uncertainties = {
            #mcstat
            r'Limited size of simulated samples':[
                'mc stats',
            ],

            #variations
            r'PDF reweighting ($t\bar{t}$)':[
                'tt PDFRW',
            ],

            r'Electron efficiency/resolution/scale/trigger':[
                'SysEL_EFF_Reco_TotalCorrUncertainty',
                'SysEL_EFF_Iso_TotalCorrUncertainty',
                'SysEL_EFF_Trigger_TotalCorrUncertainty',
                'SysEL_EFF_ID_TotalCorrUncertainty',
                'SysEG_RESOLUTION_ALL',
                'SysEG_SCALE_ALL',
            ],
            r'Jet energy resolution (JER)':[
                'SysJET_JER_SINGLE_NP',
            ],
            r'Jet energy scale (JES)':[
                'SysJET_BJES_Response',
                'SysJET_PunchThrough_MC15',
                'SysJET_Flavor_Composition',
                'SysJET_EtaIntercalibration_Modelling',
                'SysJET_EtaIntercalibration_NonClosure',
                'SysJET_EtaIntercalibration_TotalStat',#TODO added
                'SysJET_RelativeNonClosure_MC15',
                'SysJET_Flavor_Response',
                'SysJET_SingleParticle_HighPt',
                'SysJET_EffectiveNP_1',
                'SysJET_EffectiveNP_2',
                'SysJET_EffectiveNP_3',
                'SysJET_EffectiveNP_4',
                'SysJET_EffectiveNP_5',
                'SysJET_EffectiveNP_6restTerm',
            ],
            r'Muon efficiency/resolution/scale/trigger':[
                'SysMUONS_SCALE',
                'SysMUONS_ID',
                'SysMUONS_MS',
                'SysMUON_EFF_STAT',
                'SysMUON_EFF_SYS',
                'SysMUON_EFF_TrigSystUncertainty',
                'SysMUON_EFF_TrigStatUncertainty',
                'SysMUON_TTVA_SYS',
                'SysMUON_TTVA_STAT',
                'SysMUON_ISO_STAT',
                'SysMUON_ISO_SYS',
            ],
            r'NNLO top $p_{T}$, $t\bar{t}$ $p_{T}$ reweighting ($t\bar{t}$)':[
                'SysTOP_PT_RW',
                'SysTTBAR_PT_RW',
            ],
            r'Pile-up reweighting':[
                'SysPRW_DATASF',#TODO maybe wrong position
                'SysJET_Pileup_PtTerm',
                'SysJET_Pileup_OffsetMu',
                'SysJET_Pileup_OffsetNPV',
                'SysJET_Pileup_RhoTopology',
            ],
            r'$E_{T}^{miss}$':[
                'SysMET_SoftTrk_Scale',
                'SysMET_SoftTrk_ResoPara',#TODO added
                'SysMET_SoftTrk_ResoPerp',#TODO added
            ],
            r'c-jet mis-tag rate':[
                'SysFT_EFF_C_systematics',
            ],
            r'Light-flavour jet mis-tag rate':[
                'SysFT_EFF_Light_systematics',
            ],
            r'JVT':[
                'SysJET_JvtEfficiency'
            ],

            #modellings

            r'Parton shower / Hadronisation ($t\bar{t}$)':[
                'tt Fragmentation',
            ],
            r'More / less radiation ($t\bar{t}$)':[
                'tt Radiation',
            ],
            r'Matrix element modelling ($t\bar{t}$)':[
                'tt HardScatter',
            ],
            r'Matrix element modelling (single top)':[
                'stop HardScatter',
            ],
            r'Parton shower / Hadronisation (single top)':[
                'stop Fragmentation',
            ],
            r'More / less radiation (single top)':[
                'stop Radiation',
            ],
            r'DR vs. DS (single top)':[
                'stop DRDS',
            ],

            r'Modelling (Z+jets)':[
                'zjets Modelling',
            ],

            #normalization samples

            r'Normalisation Z+b/c':[
                'SysZHF',
            ],
            r'Normalisation single top':[
                'WtScale',
            ],
            r'Normalisation diboson':[
                'dibosonScale'
            ],
            r'Normalisation Z+jets':[
                'zjetsScale',
            ],
            r'Normalisation misid. leptons':[
                'fakeScale',
            ],

            #others

            r'Luminosity (3.2\%)':[
                'lumiScale',
            ],
        }
    def GetUncertainties(self,release):
        if release == 'r21.old':
            return self.uncertainties
        elif release == 'r20.7':
            self.uncertainties[r'JVT'] = ['SysJvtEfficiency']
            return self.uncertainties
        else:
            raise ValueError

    def MapPickle(self):
        NameMap = { 
            'mc_stat' : 'mc stats',
            'dt_stat' : 'data stats', 
            'FakeScale' : 'fakeScale',
            'Luminosity' : 'lumiScale',
            'norm diboson' : 'dibosonScale',
            'norm wt' : 'WtScale',
            'norm zjets': 'zjetsScale',            
            'mod_stop_StopDRDS' : 'stop DRDS',
            'mod_stop_StopFragmentation' : 'stop Fragmentation',
            'mod_stop_StopRadiation' : 'stop Radiation',
            'mod_tt_ttbarFragmentation' : 'tt Fragmentation',
            'mod_tt_ttbarHardScatter' : 'tt HardScatter',
            'mod_tt_ttbarPDFRW' : 'tt PDFRW',
            'mod_tt_ttbarRadiation' : 'tt Radiation',
            'mod_z+jets_zjetsModelling' : 'zjets Modelling',
        }
        return NameMap

if __name__ == '__main__':
    data = {'1':{2:{'20':{10:100}}}}
    FooSearch = toolkit.Searcher(data)
