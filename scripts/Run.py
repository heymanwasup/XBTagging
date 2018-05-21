
import toolkit
default_project_name = '16a'
default_input_file = './input/CalJetMar.04.2018.21.2.16.data1516.Full.root'
default_output_path = './output'
default_config_file = './data/Run_CalJet_mc16a_partialModelling_fullVariation.json'
default_cdi_file = './data/2016-20_7-13TeV-MC15-CDI-2017-01-31_v1.root'


parser = toolkit.MyParser(description='Run btagging')
parser.add_argument('-e','--efficiency',   action='store_true', help='retrieve tagging efficinecy')
parser.add_argument('-c','--control_plots', action='store_true', help='print control plots')
parser.add_argument('-b','--btagging_plots', action='store_true', help='print btagging plots')
parser.add_argument('-t','--table', action='store_true', help='get the table tex/pdf results')
parser.add_argument('-cdi','--cdi_inputs', action='store_true', help='get the cdi inputs file')
parser.add_argument('-a','--all', action='store_true', help='get the full results')


parser.add_argument('--project_name', action='store', default=default_project_name, help='name of project')
parser.add_argument('--input_file', action='store', default=default_input_file, help='/path/to/root_file')
parser.add_argument('--output_path', action='store', default=default_output_path, help='/path/to/output')
parser.add_argument('--config_file', action='store', default=default_config_file, help='/path/to/run_cfg')
parser.add_argument('--cdi_file', action='store', default=default_cdi_file, help='/path/to/cdi_file (or basename_of_cdi_file )')
args = parser.parse_args()

import RetrieveEfficiency
import DrawPlots
import BreakDown
import CDIInputs
import os
import time
import sys
import re

def main():

    output_path = '{0:}/{1:}'.format(args.output_path,args.project_name)

    if args.all or args.control_plots:
        DrawPlots.MakeControlPlots(args.input_file,output_path, args.config_file)

    if args.all or args.efficiency:
        isLoadRawFromCache = False
        worker = RetrieveEfficiency.RetrieveEfficiency(args.input_file, output_path, args.config_file,isLoadRawFromCache)
        worker.Work()
        #TODO: worker.WorkParallel()
    
    json_path = '{0:}/jsons_TagProbe/'.format(output_path)
    jsons,jsons_raw = CollectJsonFiles(json_path)
    config_overall = toolkit.json_load('./data/Overall_Info.json')
    config_user = toolkit.json_load(args.config_file)
    intervals = config_overall['binnings'][config_user['binnings']][1:]


    print '{0:}({1:}) efficiency (raw) files founded in "{2:}" :'.format(len(jsons),len(jsons_raw),json_path)
    for name,f in jsons.iteritems():
        print '\t',os.path.basename(f)
    for name,f in jsons_raw.iteritems():
        print '\t',os.path.basename(f)
    print 'Going to work on those json files.'
    time.sleep(1)

    if args.all or args.btagging_plots:
        DrawPlots.MakeBtaggingPlots(output_path, jsons)



    if args.all or args.table:
        title_fmt = 'MC16a and Data1516, {0:}\% OP of MV2c10 tagger'        
        table_maker = BreakDown.BreakDown(output_path)
        for name,json_path in jsons.iteritems():
            print name
            title = TableTitle(name, title_fmt)
            table_maker.GetTex(tex_name=name, input_json=json_path, intervals=intervals, title=title, label='unc.')

    if args.all or args.cdi_inputs:
        if args.cdi_file[0] == '.' or args.cdi_file[0] == '/':
            cdi_file = args.cdi_file
        else:
            cdi_file = os.path.join('/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/xAODBTaggingEfficiency/13TeV/',args.cdi_file)

        cdiInputMaker = CDIInputs.CDIInputs(output_path,cdi_file)
        cdiInputMaker.SetInfo(method='TP',quark='bottom',jetAuthor='AntiKt4EMTopoJets',tagger='MV2c10',ptIntervals=intervals)

        cdiInputMaker.AddMetaData(['Hadronization','Pythia8EvtGen'])
        print 'haha'
        print 
        for name in jsons.keys():
            print name
            wp = re.findall('.*wp_([0-9]+).*',name)[0]
            OP = 'FixedCutBEff_{0:}'.format(wp)
            cdiInputMaker.SetInfo(operating_point=OP)
            cdiInputMaker.MakeInput(name,jsons[name],jsons_raw[name])

def CollectJsonFiles(json_path):
    json_name_ptn = re.compile('output_(.*).json')
    json_raw_name_ptn = re.compile('raw_(?!scales|variations)(.*).json')

    files = os.listdir(json_path)
    jsons = {}
    jsons_raw = {}
    for f in files:
        if json_name_ptn.match(f):
            name = json_name_ptn.findall(f)[0]            
            jsons[name] = os.path.join(json_path,f)
        if json_raw_name_ptn.match(f):
            name = json_raw_name_ptn.findall(f)[0]            
            jsons_raw[name] = os.path.join(json_path,f)    
    return jsons,jsons_raw

def TableTitle(name,fmt):
    wp = re.findall('.*wp_([0-9]+).*',name)[0]
    title = fmt.format(wp)
    return title

if __name__ == '__main__':
    main()
