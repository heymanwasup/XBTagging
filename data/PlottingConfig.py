
self.Options = {
  'ratioXTitle'       : 'MV2c10',
  'ratioYTitle'       : 'Data/Pred.',
  'yTitle'            : 'Jets / 0.10',
  'errband'           : 'Syst. + MC Stat. Uncertainty',
  'leg_up'            : [0.65,0.75,0.9,0.95],
  'leg_do'            : [0.35,0.8,0.8,0.95],
  'logScale'          : True,
  'xRange'            : None,
  'xBins'             : None,
  'yRange'            : None,
 
  'ratioMarkerSize'   : 0.6,
  'ratioXTitleSize'   : 0.13,
  'ratioXTitleOffset' : 1.2, 
  'ratioXLabelOffset' : 1.2, 
  'ratioYTitleSize'   : 0.13,
  'ratioYTitleOffset' : 1.2, 
  'ratioYLabelOffset' : 1.2, 
  'xTitleSize'        : 0.13,
  'xTitleOffset'      : 1.2, 
  'xLabelOffset'      : 1.2, 
  'yTitleSize'        : 0.13,
  'yTitleOffset'      : 1.2, 
}

#['text',[x,y],size=1,color=1]
self.Texts = { 
  'ATLAS'  : ['#font[72]{ATLAS}',[0.2,0.9]],
  'status' : ['#font[42]{Internal}',[0.37,0.9]], 
  'Lumi'   : ['#font[42]{#sqrt{s}=13 TeV, 36.1 fb^{-1}}',[0.2,0.85],0.0375],
  'region' : ['#font[42]{e #mu 2 jets , #geq 1 tagged}',[0.2,0.8],0.03],
}
