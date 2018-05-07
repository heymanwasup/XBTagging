import toolkit
class Config_draw(object):
    def __init__(self):
        pass

    def UpdateConfig(self,fname='./data/PlotInfo_default.json'):
        config = self.GetConfig_default()
        with open(fname,'w') as f:
            toolkit.DumpToJson(config,f)

    def GetConfig_default(self):
        config = {
            'Hist_data':{
                'MarkerSize':[0.8],
            },
            
            'Hist_mcStack':{
                'Xaxis':{
                    'LabelOffset':[999],
                },
                'Yaxis':{
                    'Title':['Jets / 10 GeV'],
                    'TitleSize':[0.06],
                    'TitleOffset':[1.35],
                    'TitleFont':[42],
                    'LabelSize':[0.06],
                    'LabelFont':[42],
                    'LabelOffset':[0.005],
                    'Ndivisions':[505],
                },
            },

            'Hist_ratio':{
                'Xaxis':{
                    'Title':['p_{T}(jet) [GeV]'],
                    'TitleSize':[0.13],
                    'TitleOffset':[1.2],
                    'TitleFont':[42],
                    'LabelSize':[0.11],
                    'LabelFont':[42],
                    'LabelOffset':[0.005],
                    'Ndivisions':[510],
                },
                'Yaxis':{
                    'Title':['Data/Pred.'],
                    'TitleSize':[0.11],
                    'TitleOffset':[0.74],
                    'TitleFont':[42],
                    'LabelSize':[0.08],
                    'LabelFont':[42],
                    'LabelOffset':[0.005],
                    'Ndivisions':[50104],
                    'RangeUser':[0.5,1.5],
                },
            },

            'Hist_ratioErrBand':{
                    'MarkerSize':[0],
                    'MarkerColor':[3],
                    'LineWidth':[1],
                    'FillStyle':[3002],
                    'FillColor':[3],     
            },

            'TPad_up':{
                'constructor':['upPad','upPad',0,0.355,1,1],
                'settings'   :{
                    'TopMargin':[0.06],
                    'BottomMargin':[0.023],
                    'LeftMargin':[0.15],
                    'RightMargin':[0.045],
                },
            },

            'TPad_down':{
                'constructor':['downPad','downPad',0,0,1,0.348],
                'settings'   :{
                    'TopMargin':[0.03],
                    'BottomMargin':[0.40],
                    'LeftMargin':[0.15],
                    'RightMargin':[0.045],
                },
            },

            'Legend_up':{
                'constructor':[0.65,0.6,0.9,0.9],  
                'settings':{
                    'NColumns':[1],
                    'FillStyle':[0],
                    'BorderSize':[0],
                    'TextFont':[62],
                },
            },

            'Legend_down':{
                'constructor':[0.35,0.8,0.7,0.95],  
                'settings':{
                    'TextFont':[62],
                },
                    },
        }
        return config

def main():
    Config_draw().UpdateConfig()

if __name__ == '__main__':
    main()