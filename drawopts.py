import toolkit
import copy
class OPts(object):
  def __init__(self):
    uppad = self.GetUpPadOpts()
    downpad = self.GetDownPadOpts()
    errBandnew = self.GetErrBandNew()
    drawopts = self.GetGeneralOpts()
    drawopts['upPad'] = uppad 
    drawopts['downPad'] = downpad
    drawopts['errBandnew'] = errBandnew
    drawopts['dataHist_new'] = self.GetDataOpts_New() 
    drawopts['mcHStack_new'] = self.GetErrMCHStack_New()   
    drawopts['ratioHist_new'] = self.GetHistOpts_New()  
    drawopts['upLeg'] = self.GetUpLeg()
    drawopts['downLeg'] = self.GetDownLeg()


    self.drawopts = drawopts

  def GetGeneralOpts(self):
    drawopts = {
      'xRange':[0,250],
      'yRange':None,
      'name':'test',
      #'xBins':None,      
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],

      'fmt':['png'],
      'canvasSize':[800,800],
      #'funit':None,
      'funit':10.,
      'isLogy':True,
      'errBandName':'MC stat.',
      'dataName':'Data',
      'columns':1,
    }
    return drawopts

  def GetUpLeg(self):
    upleg = {
      'constructor':(0.60,0.55,0.9,0.9),  
      'settings':{
        'NColumns':1,
        'FillStyle':0,
        'BorderSize':0,
        'TextFont':62,
      },
    }
    return upleg

  def GetDownLeg(self):
    downleg = {
      'constructor':(0.35,0.8,0.7,0.95),  
      'settings':{
        'TextFont':62,
      },
    } 
    return downleg

  def GetUpPadOpts(self):
    upPad = {
      'constructor':('upPad','upPad',0,0.355,1,1),
      'settings'   :{
        'TopMargin':0.05,
        'BottomMargin':0.023,
        'LeftMargin':0.15,
        'RightMargin':0.045,
        'Logy':True,
      },
    }
    return upPad

  def GetDownPadOpts(self):
    downpad = {
      'constructor':('downPad','downPad',0,0,1,0.348),
      'settings'   :{
        'TopMargin':0.03,
        'BottomMargin':0.40,
        'LeftMargin':0.15,
        'RightMargin':0.045,
        'Logy':False,
      },
    }
    return downpad


  def GetErrBandNew(self):
    opts = {
      'MarkerSize':0,
      'MarkerColor':3,
      'LineWidth':1,
      'FillStyle':3002,
      'FillColor':3,
    }
    return opts
    
  def GetErrMCHStack_New(self):
    opts = {
        'Xaxis':{
        'Title':'p_{T}(jet) [GeV]',
        'TitleSize':0.13,
        'TitleOffset':1.2,
        'TitleFont':42,
        'LabelSize':0.04,
        'LabelFont':42,
        'LabelOffset':999,
        'Ndivisions':510,
      },

      'Yaxis':{
        'Title':'Jets / 10 GeV',
        'TitleSize':0.06,
        'TitleOffset':1.35,
        'TitleFont':42,
        'LabelSize':0.06,
        'LabelFont':42,
        'LabelOffset':0.005,
        'Ndivisions':505,
      },



    }
    return opts

  def GetHistOpts_New(self):
    opts = {
        'Xaxis':{
        'Title':'p_{T}(jet) [GeV]',
        'TitleSize':0.13,
        'TitleOffset':1.2,
        'TitleFont':42,
        'LabelSize':0.11,
        'LabelFont':42,
        'LabelOffset':0.005,
        'Ndivisions':510,
      },

      'Yaxis':{
        'Title':'Data/Pred.',
        'TitleSize':0.11,
        'TitleOffset':0.74,
        'TitleFont':42,
        'LabelSize':0.08,
        'LabelFont':42,
        'LabelOffset':0.005,
        'Ndivisions':50104,
      },

    }
    return opts

  def GetDataOpts_New(self):
    opts = {
      'Xaxis':{
        'Title':'',
        'TitleSize':0.13,
        'TitleOffset':1.2,
        'TitleFont':42,
        'LabelSize':0.11,
        'LabelFont':42,
        'LabelOffset':0.005,
        'Ndivisions':510,
      },

      'Yaxis':{
        'Title':'Jets / 10 GeV',
        'TitleSize':0.06,
        'TitleOffset':1.35,
        'TitleFont':42,
        'LabelSize':0.06,
        'LabelFont':42,
        'LabelOffset':0.005,
        'Ndivisions':510,
      },

      'MarkerSize':0.8,
    }
    return opts

    

    
