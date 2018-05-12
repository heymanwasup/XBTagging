import toolkit
import ROOT as R

class CDIInputs(object):
    def __init__(self,outputPath,cdiFilePath):
        self.outputDir = '{0:}/CDIInputs'.format(outputPath)
        self.f = R.TFile(cdiFilePath,'READ')
        toolkit.mkdir(self.outputDir)
        self.meta_data_overall = []

    def AddMetaData(self,meta_data_list):
        self.meta_data_overall.append(meta_data_list)
    
    def SetInfo(self,method=None,quark=None,jetAuthor=None,tagger=None,ptIntervals=None,operating_point=None):
        if method != None:
            self.method = method
        if quark != None:
            self.quark = quark            
        if jetAuthor != None:
            self.jetAuthor = jetAuthor
        if tagger != None:
            self.tagger = tagger
        if ptIntervals != None:
            self.ptIntervals =ptIntervals
        if operating_point != None:
            self.operating_point = operating_point
        
    def MakeInput(self,name,json_output,json_raw):
        self.NJet_total = toolkit.json_load(json_raw)['data']['PxT']
        self.NJet_pass = toolkit.json_load(json_raw)['data']['PxP']
        self.SF_Syst = toolkit.json_load(json_output)['sf']
        
        res = []
        self.__fillMetaDataOverall(res)

        for n in range(len(self.ptIntervals)-1):
            self.__fillPtBin(n,res)
        self.__enclose(res)
        self.__dumpResult(res,name)
        
    def __fillMetaDataOverall(self,result):
        for meta_data in self.meta_data_overall:
            args = ', '.join(meta_data)
            meta_data_line = 'meta_data_s({0:})'.format(args)
            result.append('\t'+meta_data_line)

        cut_value = self.f.Get('{0:}/{1:}/{2:}/cutvalue'.format(self.tagger,self.jetAuthor,self.operating_point))
        result.append('\tmeta_data_s(OperatingPoint,{0:})'.format(cut_value[0]))
        
    
    def __fillPtBin(self,nbin,result):
        ptL,ptR = self.ptIntervals[nbin], self.ptIntervals[nbin+1]
        result.append('\tbin({0:}<pt<{1:}, 0<abseta<2.5)'.format(ptL,ptR))
        result.append('\t{')

        nominal_val = self.SF_Syst['nominal'][nbin+1]
        stat_err = self.SF_Syst['data stats'][nbin+1]
        nJetTotal_val = self.NJet_total['vals'][nbin+1]
        nJetTotal_err = self.NJet_total['errs'][nbin+1]
        nJetPass_val = self.NJet_pass['vals'][nbin+1]
        nJetPass_err = self.NJet_pass['errs'][nbin+1]

        result.append('\t\tcentral_value({0:},{1:})'.format(nominal_val,stat_err))
        result.append('\t\tmeta_data(N_jets total,{0:},{1:})'.format(nJetTotal_val,nJetTotal_err))
        result.append('\t\tmeta_data(N_jets tagged,{0:},{1:})'.format(nJetPass_val,nJetPass_err))

        for name,syst in self.SF_Syst.iteritems():
            if name == 'nominal' or name == 'data stats':
                continue
            error = syst[nbin+1]*100./self.SF_Syst['nominal'][nbin+1]
            result.append('\t\tusys(FT_EFF_{0:},{1:}%)'.format(name,error))            

        result.append('\t}')

    def __enclose(self,result):
        head = 'Analysis({0:},{1:},{2:},{3:},{4:}){{'.format(self.method,self.quark,self.tagger,self.operating_point,self.jetAuthor)            
        result.insert(0,head)
        result.append('}')

    def __dumpResult(self,result,name):
        fname = '{0:}/cdi_{1:}.txt'.format(self.outputDir,name)
        with open(fname,'w') as f:
            for line in result:
                f.write(line+'\n')
        print 'CDI inputs generated:\t',fname

