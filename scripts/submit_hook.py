#!/usr/bin/python
import toolkit
import RetrieveEfficiency

default_input_file = './input/CalJetDec.01.AddStopNlo.root'
default_output_path = './output'
default_config_file = './submit/test.json'


parser = toolkit.MyParser(description='Run btagging')
parser.add_argument('--input_file', action='store', default=default_input_file, help='/path/to/root_file')
parser.add_argument('--output_path', action='store', default=default_output_path, help='/path/to/output')
parser.add_argument('--config_file', action='store', default=default_config_file, help='/path/to/calibration_cfg')
parser.add_argument('--load_raw', action='store_true', help='is load raw from json')

args = parser.parse_args()

def main():
    caliber = RetrieveEfficiency.Caliber(args.input_file,args.output_path,int(args.load_raw))
    config = toolkit.json_load(args.config_file)
    caliber.Run(config)

if __name__ == '__main__':
    main()