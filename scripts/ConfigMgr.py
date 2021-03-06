import toolkit
import OverAllConfig_register
import PlottingConfig_register

default_overall_config = './data/Overall_Info.json'
default_plotting_config = './data/PlottingConfig_default.json'

parser = toolkit.MyParser(description='Manage config files')
parser.add_argument('-o', '--option',choices=['overall','plotting'],action='store',required=True, help='update overall/plotting configuration file')
parser.add_argument('-p','--path', action='store',default='', help='/path/to/configure_file (it\'s optional) ')

args = parser.parse_args()

def main():
    overall_config = OverAllConfig_register.Config_overall()
    plotting_config = PlottingConfig_register.Config_draw()

    if args.option == 'overall':
        overall_config_path = default_overall_config if len(args.path)==0 else args.path
        overall_config.UpdateConfig(overall_config_path)

    if args.option == 'plotting':
        plotting_config_path = default_plotting_config if len(args.path)==0 else args.path
        plotting_config.UpdateConfig(plotting_config_path)


if __name__ == '__main__':
    main()