"""
Andy said the errors of eff_data are too low, should be double checked
"""
import math
import toolkit
import pickle
def funJson(json_file_path):
    for key in ['e_dt','e_mc','sf'  ]:
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

def LoadPickleDumpJson(pickle_file_path):
    with open(pickle_file_path,'rb') as f:
        data = pickle.load(f)
    with open('./test/data/Nov.24.Fixed.json','w') as f:
        toolkit.DumpToJson(data,f)

def funOld(json_path):
    data = toolkit.json_load(json_path)['80MVA']['70']
    for key in ['e_dt','e_mc','sf']:
        _data = data[key]
        nominal = _data['nominal'][1:]
        data_stat = _data['dt_stat'][1:]
        tot = _data['total'][1:]
        syst = list(map(lambda x,y:math.sqrt(x**2-y**2),tot,data_stat))
        fmter = lambda x:'  '.join(list(map(lambda _x:'{0:.3f}'.format(_x),x)))
        p = lambda k,v:'{0:<8} {1:}'.format(k,fmter(v))
        print p(key,nominal)
        print p('total',tot)
        print p('stat',data_stat)
        print p('syst',syst)
        print '\n\n'


    
def main():
    json_file_path = 'output/Dec.01.AddStopNlo/jsons_TagProbe/output_mu_XMu_mva_80_eta_xEta_wp_70.json'
    #funJson(json_file_path)

    pickle_file_path = './test/data/Cal_Nov.24.Fixed_XMu_xEta_py6.OS.pickle'

    json_path_old = './test/data/Nov.24.Fixed.json'
    funOld(json_path_old)






if __name__ == '__main__':
    main()



