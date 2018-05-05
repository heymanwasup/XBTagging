import toolkit
import math
from copy import copy
import commands

class BreakDown(object):
    def __init__(self,project_name,output_path,uncertainties=None):
        if uncertainties==None:
            self.uncertainties = GroupSystmatics.uncertainties
        else:
            sel.uncertainties = uncertainties
        self.output_path = '{0:}/{1:}/table'.format(output_path,project_name)
        toolkit.mkdir(self.output_path)


    @staticmethod
    def AddEntry(tab_list,entries,isPercentage=False):
        nbins = len(entries.values()[0])
        fmt = lambda x : x if isinstance(x,str) else '{0:.3f}'.format(x)
        fmtP = lambda x:'{0:.1f}'.format(x)
        
        def addEntry(name):
            tot = entries[r'SF']
            if not name in entries:
                print '\n'+'----------\n'*2+'FBIWARNING: {0:} not even registered !\n----------'.format(name)
                content = ['-']*nbins                
            elif  isinstance(entries[name][0],str) or (not isPercentage):
                content = map(fmt,entries[name])
            else:
                content = map(lambda x,y:fmtP(100.*(x/y)) if y!=0 else 0, entries[name], tot)
            content = [name] + content
            content_str = ' & '.join(map(str,content))
            content_str = content_str + r'\\'
            tab_list.append(content_str)
        return addEntry

    def GetEnrties(self,data,uncertainties):
        entries = {}

        sf = data.pop('nominal')[1:]
        stat = data.pop('data stats')[1:]

        nbins = len(sf)
        syst = [0.]*nbins
        for name,uncertainty in data.iteritems():
            unc = uncertainty[1:]
            for n in range(nbins):
                syst[n] = math.sqrt(syst[n]**2+unc[n]**2)

        total = list(map(lambda x,y:math.sqrt(x**2+y**2), syst,stat))

        entries['SF'] = sf
        entries[r'Stat. unc.'] = stat
        entries[r'Syst. unc.'] = syst        
        entries[r'Total unc.'] = total

        for name, uncertainty_group in uncertainties.iteritems():
            group_tot = [0.]*nbins
            empty = True
            for item in uncertainty_group:
                if not item in data:
                    print '\n\n--------\nWARNNING: skip {0:}\n--------'.format(item)
                    continue
                empty = False
                unc = data[item][1:]
                for n in range(nbins):
                    group_tot[n] = math.sqrt(group_tot[n]**2+unc[n]**2)
            if empty:
                group_tot = ['-']*nbins
            entries[name] = group_tot

        return entries


    def MaketabularList(self,input_json,intervals):
        data = toolkit.json_load(input_json)['sf']

        entries = self.GetEnrties(data,self.uncertainties)
        nBins = len(entries.values()[0])+1

        tabular_list = []
        
        addEntry = self.AddEntry(tabular_list,entries,isPercentage=False)
        addEntryP = self.AddEntry(tabular_list,entries,isPercentage=True)
        tabular_list.append( r'\begin{tabular}{l'+r'|r'*(nBins-1)+r'}' )
        tabular_list.append(r'\toprule')
        tabular_list.append(intervals)
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        addEntry('SF')
        addEntry(r'Total unc.')
        addEntry(r'Stat. unc.')
        addEntry(r'Syst. unc.')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\multicolumn{'+str(nBins)+r'}{c}{Systematic Uncertainties [\%]} \\')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\hline')
        addEntryP(r'Parton shower / Hadronisation ($t\bar{t}$)')
        addEntryP(r'Matrix element modelling ($t\bar{t}$)')
        addEntryP(r'NNLO Top $p_{T}$, $t\bar{t}$ $p_{T}$ reweighting ($t\bar{t}$)')
        addEntryP(r'PDF reweighting ($t\bar{t}$)')
        addEntryP(r'More / less radiation ($t\bar{t}$)')
        addEntryP(r'Modelling (single top)')
        addEntryP(r'Parton shower / Hadronisation (single top)')
        addEntryP(r'More / less radiation (single top)')
        addEntryP(r'$t\bar{t}$ diagram overlap (single top)')
        addEntryP(r'Modelling (Z+jets)')
        addEntryP(r'Z $p_{T}$ reweighting')
        tabular_list.append(r'\hline')
        addEntryP(r'MC stat. unc.')
        tabular_list.append(r'\hline')
        addEntryP(r'Norm. single top')
        addEntryP(r'Norm. Z+jets')
        addEntryP(r'Norm. Z+b/c')
        addEntryP(r'Norm. diboson')
        addEntryP(r'Norm. lepton fakes')
        tabular_list.append(r'\hline')
        addEntryP(r'Pile-up reweighting')
        addEntryP(r'Electron eff./res./scale')
        addEntryP(r'Muon eff./res./scale')
        addEntryP(r'$E_{T}^{miss}$')
        addEntryP(r'Jet energy scale')
        addEntryP(r'Jet energy resolution')
        addEntryP(r'JVT')
        addEntryP(r'Light jet mis-tag rate')
        addEntryP(r'C jet mis-tag rate')
        addEntryP(r'Luminosity (3.2\%)')
        tabular_list.append(r'\hline')
        tabular_list.append(r'\bottomrule')
        tabular_list.append(r'\end{tabular}')
        return tabular_list

    def WrapTable(self,tabular_list,title,table_number):
        tabular_list = copy(tabular_list)
        tabular_list.insert(0,r'\scalebox{0.75}[0.85]{')
        tabular_list.append(r'}')
        
        tabular_list.insert(0,r'\centering')
        tabular_list.insert(0,r'\renewcommand\thetable{'+str(table_number)+'}')
        tabular_list.insert(0,r'\begin{table}[htbp]') 
        tabular_list.append(r'\caption{'+title+'}')
        tabular_list.append(r'\end{table}')

        return tabular_list
    def WrapDocument(self,table):
        table = copy(table)
        table.insert(0, r'\begin{document}')
        table.append(r'\end{document}')

        table.insert(0,r'\usepackage{graphics}')
        table.insert(0,r'\usepackage{booktabs}')
        table.insert(0,r'\documentclass{article}')
        return table

    def DumpTex(self,name,tabular_list):
        tex_path = '{0:}/{1:}.tex'.format(self.output_path,name)
        with open(tex_path,'w') as f:
            for line in tabular_list:
                f.write(line+'\n')
        return tex_path

    def MakePDF(self,input_tex):
        commands.getstatusoutput('pdflatex -output-directory={0:} {1:}'.format(self.output_path,input_tex))

    def GetInterval(self,interval_list):
        nbins = len(interval_list)-1
        interval_str_list = [r'$p_{T}$ Interval [GeV]']
        for n in range(nbins):
            interval_str_list.append('{0:}-{1:}'.format(interval_list[n],interval_list[n+1]))
        interval_str = ' & '.join(interval_str_list)
        interval_str += r'\\'
        return interval_str
        
        
    def GetTex(self,name,input_json,intervals,title,tab_number):
        intervals = self.GetInterval(intervals)
        tabular_list = self.MaketabularList(input_json,intervals)
        table = self.WrapTable(tabular_list,title,tab_number)
        document = self.WrapDocument(table)
        tex_path = self.DumpTex(name,document)
        self.MakePDF(tex_path)

class GroupSystmatics(object):
    uncertainties = {

        #mcstat

        r'MC stat. unc.':[
            'mc stats',
        ],

        #variations
        r'PDF reweighting ($t\bar{t}$)':[
            'tt PDFRW',
        ],

        r'Electron eff./res./scale':[
            'SysEL_EFF_Reco_TotalCorrUncertainty',
            'SysEL_EFF_Iso_TotalCorrUncertainty',
            'SysEL_EFF_Trigger_TotalCorrUncertainty',
            'SysEL_EFF_ID_TotalCorrUncertainty'
            'SysEG_RESOLUTION_ALL',
            'SysEG_SCALE_ALL',
        ],
        r'Jet energy resolution':[
            'SysJET_JER_SINGLE_NP',
        ],
        r'Jet energy scale':[
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
        r'Muon eff./res./scale':[
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
        r'NNLO Top $p_{T}$, $t\bar{t}$ $p_{T}$ reweighting ($t\bar{t}$)':[
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
        r'C jet mis-tag rate':[
            'SysFT_EFF_C_systematics',
        ],
        r'Light jet mis-tag rate':[
            'SysFT_EFF_Light_systematics',
        ],
        r'JVT':[
            'SysJvtEfficiency'
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
        r'Modelling (single top)':[
            'stop HardScatter',
        ],
        r'Parton shower / Hadronisation (single top)':[
            'stop Fragmentation',
        ],
        r'More / less radiation (single top)':[
            'stop Radiation',
        ],
        r'$t\bar{t}$ diagram overlap (single top)':[
            'stop DRDS',
        ],

        r'Modelling (Z+jets)':[
            'zjets Modelling',
        ],

        #normalization samples

        r'Norm. Z+b/c':[
            'SysZHF',
        ],
        r'Norm. single top':[
            'WtScale',
        ],
        r'Norm. diboson':[
            'dibosonScale'
        ],
        r'Norm. Z+jets':[
            'zjetsScale',
        ],
        r'Norm. lepton fakes':[
            'fakeScale',
        ],

        #others

        r'Luminosity (3.2\%)':[
            'lumiScale',
        ],
    }
