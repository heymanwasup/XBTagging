
import toolkit
#default_project_name = 'CalJetMar.04.2018.21.2.16.data1516.Full'
default_project_name = 'test'
default_input_file = './input/CalJetMar.04.2018.21.2.16.data1516.Full.root'
default_output_path = './output'
default_config_path = './data/Run_CalJet_mc16a_partialModelling_fullVariation.json'


parser = toolkit.MyParser(description='Run btagging')
parser.add_argument('-e','--efficiency',   action='store_true', help='retrieve tagging efficinecy')
parser.add_argument('-c','--control_plots', action='store_true', help='print control plots')
parser.add_argument('-b','--btagging_plots', action='store_true', help='print btagging plots')
parser.add_argument('-t','--table', action='store_true', help='get the table tex/pdf results')
parser.add_argument('-a','--all', action='store_true', help='get the full results')

parser.add_argument('-P','--parallel', action='store_true', help='run retrieve efficiency parallelly')
parser.add_argument('-N','--process', action='store',default=8, help='# of processes when run retrieve efficiency parallelly')

parser.add_argument('--project_name', action='store', default=default_project_name, help='name of project')
parser.add_argument('--input_file', action='store', default=default_input_file, help='/path/to/root_file')
parser.add_argument('--output_path', action='store', default=default_output_path, help='/path/to/output')
parser.add_argument('--config_path', action='store', default=default_config_path, help='/path/to/run_cfg')
args = parser.parse_args()

import os
import time
import sys
import re

import RetrieveEfficiency
import DrawPlots
import BreakDown

def main():




    output_path = '{0:}/{1:}'.format(args.output_path,args.project_name)

    if args.all or args.control_plots:
        DrawPlots.MakeControlPlots(args.input_file,output_path, args.config_path)

    if args.all or args.efficiency:
        isLoadRawFromCache = False
        worker = RetrieveEfficiency.RetrieveEfficiency(args.input_file, output_path, args.config_path,isLoadRawFromCache)
        worker.Work(args.parallel,int(args.process))
        #TODO: worker.WorkParallel()

    json_path = '{0:}/jsons_TagProbe/'.format(output_path)
    jsons = CollectJsonFiles(json_path)

    if args.all or args.btagging_plots or args.table:
        print '{0:} json files founded in "{1:}" :'.format(len(jsons),json_path)
        for name,f in jsons.iteritems():
            print '\t',os.path.basename(f)
        print 'Going to work on those json files.'
        for n in range(5):
            print '.',
            sys.stdout.flush()
            time.sleep(1)
        print 

    if args.all or args.btagging_plots:
        DrawPlots.MakeBtaggingPlots(output_path, jsons)

    if args.all or args.table:
        title_fmt = 'MC16a vs Data1516, {0:}\% OP of MV2c10 tagger'
        config_overall = toolkit.json_load('./data/Overall_Info.json')
        config_user = toolkit.json_load(args.config_path)
        intervals = config_overall['binnings'][config_user['binnings']][1:]
        table_maker = BreakDown.BreakDown(output_path)
        for name,json_path in jsons.iteritems():
            title = TableTitle(name, title_fmt)
            table_maker.GetTex(tex_name=name, input_json=json_path, intervals=intervals, title=title, label='unc.')

def CollectJsonFiles(json_path):
    json_name_ptn = re.compile('output_(.*).json')
    files = os.listdir(json_path)
    jsons = {}
    for f in files:
        if json_name_ptn.match(f):
            name = json_name_ptn.findall(f)[0]            
            jsons[name] = os.path.join(json_path,f)
    return jsons

def TableTitle(name,fmt):
    ptn = re.compile('.*_wp_([0-9]+).*')
    wp = ptn.findall(name)[0]
    title = fmt.format(wp)
    return title
    
if __name__ == '__main__':
    main()
