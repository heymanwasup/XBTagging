import RetrieveEfficiency
import DrawPlots
import BreakDown
import os
import time
import toolkit

default_project_name = 'CalJetMar.04.2018.21.2.16.data1516.Full'
default_input_file = './input/CalJetMar.04.2018.21.2.16.data1516.Full.root'
default_output_path = './output'
#For ttbar modelling, only hardscatter included
default_config_path = './data/Run_CalJet_mc16a_partialModelling_fullVariation.json'

parser = toolkit.MyParser(description='Run btagging')
parser.add_argument('-e','--efficiency',   action='store_true', help='retrieve tagging efficinecy')
parser.add_argument('-c','--control_plots', action='store_true', help='print control plots')
parser.add_argument('-b','--btagging_plots', action='store_true', help='print btagging plots')
parser.add_argument('-t','--table', action='store_true', help='get the full results')
parser.add_argument('-a','--all', action='store_true', help='get the full results')

parser.add_argument('--project_name', action='store', default=default_project_name, help='name of project')
parser.add_argument('--input_file', action='store', default=default_input_file, help='/path/to/root_file')
parser.add_argument('--output_path', action='store', default=default_output_path, help='/path/to/output')
parser.add_argument('--config_path', action='store', default=default_config_path, help='/path/to/run_cfg')
args = parser.parse_args()

def main():

    output_path = '{0:}/{1:}'.format(args.output_path,args.project_name)

    if args.all or args.control_plots:
        DrawPlots.MakeControlPlots(args.input_file,output_path, args.config_path)

    if args.all or args.efficiency:
        isLoadRawFromCache = False
        worker = RetrieveEfficiency.RetrieveEfficiency(args.input_file, output_path, args.config_path,isLoadRawFromCache)
        worker.Work()
        #TODO: worker.WorkParallel()

    json_path = '{0:}/jsons_TagProbe/'.format(output_path)
    jsons = CollectJsonFiles(json_path)

    if args.all or args.btagging_plots or args.table:
        print '{0:} json files founded in \n\t{1:}\t:'.format(len(jsons),json_path)
        for name,f in jsons.iteritems():
            print '\t',os.path.basename(f)
        print 'going to work on those json files.'
        for n in range(3):
            print '.',
            time.sleep(1)
        print 

    if args.all or args.btagging_plots:
        DrawPlots.MakeBtaggingPlots(output_path, jsons)

    if args.all or args.table:
        table_maker = BreakDown.BreakDown(output_path)
        for name,json_path in jsons.iteritems():
            #TODO: title translater
            table_maker.GetTex(tex_name=name, input_json=json_path, intervals=intervals, title=name, label='breakdown')

def CollectJsonFiles(json_path):
    json_name_ptn = 'output_(.*).json'
    files = os.listdir(json_path)
    jsons = {}
    for f in files:
        if json_name_ptn.match(f):
            name = json_name_ptn.findall(f)
            jsons[name] = os.path.join(json_path,f)
    return jsons

if __name__ == '__main__':
    main()
