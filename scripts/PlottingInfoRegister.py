import toolkit
import copy
class Config_draw(object):
  def __init__(self):
    pass

  def GetConfig_default(self):
    config = {
      'Config_general': {
      'xRange':[0,600],
      'yRange':None,
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],
      'fmt':['png'],
      'canvasSize':[800,800],
      'unit':10.,
      'LogScale':True,
      'errBandName':'MC stat.',
      'dataName':'Data',
    }
    }
    
    




    self.ProbeJetPt()

    
  def ProbeJetPt(self):
    uppad = self.GetUpPad()
    downpad = self.GetDownPadO()
    ratioErrBand = self.GetErrBand()
    drawopts = {}
    drawopts['Config_general'] = self.GetConfig_general()
    drawopts['TPad_up'] = uppad 
    drawopts['TPad_down'] = downpad
    drawopts['Hist_ratioErrBand'] = ratioErrBand
    drawopts['Hist_data'] = self.GetData() 
    drawopts['Hist_mcStack'] = self.GetMCHStack()   
    drawopts['Hist_ratio'] = self.GetRatio()  
    drawopts['Legend_up'] = self.GetUpLeg()
    drawopts['Legend_down'] = self.GetDownLeg()
    return drawopts

  def GetConfig_general(self):
    drawopts = {
      'xRange':[0,600],
      'yRange':None,
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],
      'fmt':['png'],
      'canvasSize':[800,800],
      'unit':10.,
      'LogScale':True,
      'errBandName':'MC stat.',
      'dataName':'Data',
    }
    return drawopts

  def GetUpLeg(self):
    upleg = {
      'constructor':[0.60,0.55,0.9,0.9],  
      'settings':{
        'NColumns':[1],
        'FillStyle':[0],
        'BorderSize':[0],
        'TextFont':[62],
      },
    }
    return upleg

  def GetDownLeg(self):
    downleg = {
      'constructor':[0.35,0.8,0.7,0.95],  
      'settings':{
        'TextFont':[62],
      },
    } 
    return downleg

  def GetUpPad(self):
    upPad = {
      'constructor':['upPad','upPad',0,0.355,1,1],
      'settings'   :{
        'TopMargin':[0.05],
        'BottomMargin':[0.023],
        'LeftMargin':[0.15],
        'RightMargin':[0.045],
      },
    }
    return upPad

  def GetDownPad(self):
    downpad = {
      'constructor':['downPad','downPad',0,0,1,0.348],
      'settings'   :{
        'TopMargin':[0.03],
        'BottomMargin':[0.40],
        'LeftMargin':[0.15],
        'RightMargin':[0.045],
      },
    }
    return downpad


  def GetErrBand(self):
    opts = {
      'MarkerSize':[0],
      'MarkerColor':[3],
      'LineWidth':[1],
      'FillStyle':[3002],
      'FillColor':[3],
    }
    return opts
    
  def GetMCHStack(self):
    opts = {
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



    }
    return opts

  def GetRatio(self):
    opts = {
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
    }
    return opts

  def GetData(self):
    opts = {
      'MarkerSize':[0.8],
    }
    return opts

def main():
  drawopts = OPts()

  cal_probe_pt = drawopts.ProbeJetPt()
  toolkit.mkdir('./PlottingConfigs')
  with open('./PlottingConfigs/caljet_probe_jet_pt.json','w') as f:
    toolkit.DumpToJson(cal_probe_pt,f)


if  __name__ == '__main__':
  main()
