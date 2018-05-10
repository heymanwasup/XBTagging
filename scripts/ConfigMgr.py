import toolkit
import OverAllConfig_register
import PlottingConfig_register

default_overall_config = './data/Overall_Info.json'
default_plotting_config = './data/PlottingConfig_default.json'

parser = toolkit.MyParser(description='Manage config files')
parser.add_argument('-o', '--option',choices=['overall','plotting'],action='store',required=True, help='update overall/plotting configuration file')
parser.add_argument('-p','--path', action='store', help='path to configure file')

args = parser.parse_args()

def main():
    overall_config = OverAllConfig_register.Config_overall()
    plotting_config = PlottingConfig_register.Config_draw()

    if args.option == 'overall':
        overall_config.UpdateConfig(default_overall_config)

    if args.option == 'plotting':
        plotting_config.UpdateConfig(default_plotting_config)


if __name__ == '__main__':
    main()