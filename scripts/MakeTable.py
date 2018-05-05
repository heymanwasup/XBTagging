import BreakDown
def test_tab(project_name,input_json,output_path,title,label,name,intervals):

    
    table_maker = BreakDown.BreakDown(project_name,output_path)
    table_maker.GetTex(name,input_json,intervals,title,label) 

if __name__ == '__main__':
    output_path = '.'
    input_json  = './output/test/output_mu_XMu_mva_80_eta_xEta_wp_85.json'
    
    title = 'table for test'
    label = '1'
    name = 'tab_for_test_2'

    intervals = [20,30,40,60,85,110,140,175,250,600]
    test_tab(project_name,input_json,output_path,title,label,name,intervals)
