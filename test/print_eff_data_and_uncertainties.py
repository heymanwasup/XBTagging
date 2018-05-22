"""
Andy said the errors of eff_data are too low, should be double checked
"""
import math
import toolkit

def fun(json_file_path,key):
    data = toolkit.json_load(json_file_path)[key]
    nominal = data.pop('nominal')
    data_stat = data.pop('data stats')

    
    

    fmter = lambda x:'  '.join(list(map(lambda _x:'{0:.3f}'.format(_x),x)))
    syst = [0.]*len(nominal)
    syst_2 = reduce(lambda x,y:list(map(lambda _x,_y:_x + _y**2,x,y)),data.values(),syst)
    syst_tot = list(map(lambda x:math.sqrt(x),syst_2))

    tot = list(map(lambda x,y:math.sqrt(x**2+y**2),syst_tot,data_stat))
    p = lambda k,v:'{0:<8} {1:}'.format(k,fmter(v))
    print p(key,nominal)
    print p('stat',data_stat)
    print p('total',tot)
    print '\n\n'

def main():
    json_file_path = 'output/CalJetDec.01.AddStopNlo/jsons_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
    fun(json_file_path,'e_dt')
    fun(json_file_path,'e_mc')
    fun(json_file_path,'sf')
if __name__ == '__main__':
    main()



