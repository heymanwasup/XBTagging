import DrawControlPlots
import DrawEffSF
import MakeTable
import RetrieveEfficiency
import os
import sys
import time
sys.path.append('./scripts')

project_name = 'Demo' 
output_path = './output'

input_file = '/sps/atlas/c/cli/BTagCalibration/BtaggingInputsProcessor.Apr.23/input/CalJetApr.23.2018.MV2c10.FullSys.FxiedWP.root'
#input_file = './input/test.root'

run_config = './data/Run_CalJet_test.json'



def Sleep():
    for n in range(3):
        print 3-n,' !'
        time.sleep(1)



print '\n\n\n\n','--------Start draw control plots------------\n'*3
Sleep()
is_modelling = False #if modelling unc. included in ratio error band
is_variation = True #if variations unc. included in ratio error band
#DrawControlPlots.DrawProbeJetPt(project_name,input_file,output_path,run_config,is_modelling,is_variation)





print '\n\n\n\n','--------Start retrieve efficiency------------\n'*3
Sleep()
isLoadRawFromCache = True # could always be True, but if user want to debug the script, it's better set it to False
RetrieveEfficiency.test(project_name,input_file,output_path,run_config,isLoadRawFromCache)





output_json = './{0:}/{1:}/json_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_85.json'.format(output_path,project_name)
if os.path.isfile(output_json):#make the output json file have been generated 
  

    print '\n\n\n\n','--------Start draw SF, Eff plots------------\n'*3
    Sleep()
    DrawEffSF.test_sf(project_name, output_json, output_path)
    DrawEffSF.test_eff(project_name, output_json, output_path)
    DrawEffSF.test_comparison(project_name, output_json, output_path)




    print '\n\n\n\n','--------Start make table------------\n'*3
    Sleep()
    title = 'table for test'
    table_number = '1'
    name = 'table_mu_XMu_mva_80_eta_xEta_wp_85'
    intervals = [20,30,40,60,85,110,140,175,250,600]
    MakeTable.test_tab(project_name,output_json,output_path,title,table_number,name,intervals)

