import argparse
import DrawPlots
import RetrieveEfficiency


def main():
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--retrieve',   action='store',  default='test', help='the runtag for training')
    parser.add_argument('--control_plots', action='store', choices=['0','1','2','3'],help='the training category')
    parser.add_argument('--all', action='store_true', help='training parallel in 4 categories')
    parser.add_argument('--btagging_plots',   action='store',default='0',choices=['0','1','2'],help='the input variables')
    parser.add_argument('--table',    action='store',default='',help='the input file tag')
    main()