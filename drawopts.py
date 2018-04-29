import toolkit
import copy
class OPts(object):
  def __init__(self):
    self.Init()
    drawopts = self.GetGeneralOpts()

    ratio_opts = self.GetRatioOpts()
#    data_opts = self.GetDataOpts()
    data_opts = self.GetMCHOpts()
    mch_opts = self.GetMCHOpts()
    errb_opts = self.GetErrbandOpts()
    uppad = self.GetUpPadOpts()
    downpad = self.GetDownPadOpts()
    errBandnew = self.GetErrBandNew()
  
    drawopts['ratioHist'] = ratio_opts
    drawopts['dataHist'] = data_opts 
    drawopts['mcHStack'] = mch_opts
    drawopts['errBand'] = errb_opts
    drawopts['upPadSettings'] = uppad 
    drawopts['downPadSettings'] = downpad
    drawopts['errBandnew'] = errBandnew
    drawopts['dataHist_new'] = self.GetDataOpts_New() 

    drawopts['mcHStack_new'] = self.GetErrMCHStack_New()   
    drawopts['ratioHist_new'] = self.GetHistOpts_New()  
    self.drawopts = drawopts

  def GetGeneralOpts(self):
    drawopts = {
      'name':'test',
      'xBins':[0,20,30,40,60,85,110,140,175,250,600],
      'xRange':None,
      'yRange':None,
      'fmt':['png'],
      'dataHist':None,
      'mcHStack':None,
      'ratioHist':None,
      'errBand':None,
      'canvasSize':[800,800],
      'funit':10.,
      'isLogy':True,
      'errBandName':'MC stat.',
      'downLegPostion':[0.35,0.8,0.7,0.95],
      'dataName':'Data',
      'columns':1,
      'upLegPosition':[0.60,0.55,0.9,0.9],
      'errbMarkerColor':3,
      'errbFillColor':3,
      'errbFillStyle':3002,
      'upPadPosition':[0,0.355,1,1],
      'upPadSettings':None,
      'downPadPosition':[0,0,1,0.348],
      'downPadSettings':None,
    }
    return drawopts

  def GetUpPadOpts(self):
    settings = {
      'SetTopMargin':0.05,
      'SetBottomMargin':0.023,
      'SetLeftMargin':0.15,
      'SetRightMargin':0.045,
      'SetLogy':True,
    }
    return settings

  def GetDownPadOpts(self):
    settings = {
      'SetTopMargin':0.03,
      'SetBottomMargin':0.40,
      'SetLeftMargin':0.15,
      'SetRightMargin':0.045,
      'SetLogy':False,
    }
    return settings

  def GetErrbandOpts(self):
    opts = {
      'MarkerSize':0,
      'MarkerColor':3,
      'LineWidth':1,
      'FillStyle':3002,
      'FillColor':3,
    }
    errband_opts = copy.copy(self.hist_opts)
    errband_opts.update(opts)
    return errband_opts
    opts = copy.copy(self.hist_opts)
    return opts

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



  def GetMCHOpts(self):
    mc_opts = {
      'xTitle':'',
      'xLabelSize':0.04,
      'xLabelOffset':999,
      'xNdiv' : 510,

      'yTitle':'Jets / 10 GeV',
      'yTitleSize':0.06,
      'yTitleOffset':1.35,
      'yLabelSize':0.06,
      'yLabelOffset':0.005,
      'yNdiv':510,

    }
    opts = copy.copy(self.hist_opts)
    opts.update(mc_opts)
    return opts


  def GetDataOpts(self):
    data_opts = {
      'xTitle':'',
      'yTitle':'Jets / 10 GeV',
      'yTitleSize':0.06,
      'yTitleOffset':1.35,
      'yLabelSize':0.06,
      'yNdiv':510,

      'MarkerSize':0.8,
    }
    opts = copy.copy(self.hist_opts)
    opts.update(data_opts)
    return opts

  def GetRatioOpts(self):
    opts = {
    }
    ratio_opts = copy.copy(self.hist_opts)
    ratio_opts.update()
    return ratio_opts

  def GetHistOpts(self):
    hists_opts = {
      'xTitle':'p_{T}(jet) [GeV]',
      'xTitleSize':0.13,
      'xTitleOffset':1.2,
      'xTitleFont':42,
      'xLabelSize':0.11,
      'xLabelFont':42,
      'xLabelOffset':0.005,
      'xNdiv':510,

      'yTitle':'Data/Pred.',
      'yTitleSize':0.11,
      'yTitleOffset':0.74,
      'yTitleFont':42,
      'yLabelSize':0.08,
      'yLabelFont':42,
      'yLabelOffset':0.005,
      'yNdiv':50104,
    }
    return hists_opts

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

  def Init(self):
    self.hist_opts  = self.GetHistOpts()
    self.GeneralOpts = self.GetGeneralOpts()
    

    
