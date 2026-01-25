from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'FDC'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [fdc_efficiency, fdc_dedxpos, fdc_dedxneg]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def fdc_dedxpos(rootfile) :

  titles = ['q+ dE/dx status','FDC q+ dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q+ dE/dx resolution at 1.5 GeV/c']
  names = ['dedxpos_status','dedxposmean','dedxposres']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5
  
  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q+'

  min_counts = 5e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  pcut = 1.5 #;    // draw cut through histo at p=1.5 GeV/c
  pbin = h.GetXaxis().FindBin(pcut)
  p = h.ProjectionY("p1",pbin,pbin)

  if p.GetEntries() < 1000 :
    return values 

  p.GetXaxis().SetRangeUser(0,5)

  g = TF1('g','gaus',0,12)

  fitstat = p.Fit('g','0qwes')
  
  #print 'fit status ',fitstat.IsValid(), fitstat.Status()

  if int(fitstat) == 0:
    mean = g.GetParameter(1)
    res = 2.0*g.GetParameter(2)/mean

    status = 1
    if mean < dedxmin or mean > dedxmax:
      status=0
    if res < dedxresmin or res > dedxresmax:
      status=0

    values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
  
  return values


def fdc_dedxneg(rootfile) :

  titles = ['q- dE/dx status','FDC q- dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q- dE/dx resolution at 1.5 GeV/c']
  names = ['dedxneg_status','dedxnegmean','dedxnegres']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5
  
  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q-'

  min_counts = 5e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  pcut = 1.5 #;    // draw cut through histo at p=1.5 GeV/c
  pbin = h.GetXaxis().FindBin(pcut)
  p = h.ProjectionY("p1",pbin,pbin)

  if p.GetEntries() < 1000 :
    return values 

  g = TF1('g','gaus',0,12)

  fitstat = p.Fit('g','0qwes')
  
  #print 'fit status ',fitstat.IsValid(), fitstat.Status()

  if fitstat == 0:
    mean = g.GetParameter(1)
    res = 2.0*g.GetParameter(2)/mean

    status = 1
    if mean < dedxmin or mean > dedxmax:
      status=0
    if res < dedxresmin or res > dedxresmax:
      status=0

    values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
  
  return values


def fdc_efficiency(rootfile) :

  titles = ['FDC efficiency status', 'FDC wire efficiency at 0.04mm', 'FDC wire efficiency at 0.04mm error', 'FDC wire efficiency at 2mm', 'FDC wire efficiency at 2mm error', 'FDC wire efficiency at 4mm', 'FDC wire efficiency at 4mm error', 'FDC wire efficiency at 5mm', 'FDC wire efficiency at 5mm error']
  names = ['eff_status', 'eff0_efficiency_mg', 'eff0_efficiency_mg_err', 'eff2_efficiency_mg', 'eff2_efficiency_mg_err', 'eff4_efficiency_mg', 'eff4_efficiency_mg_err', 'eff5_efficiency_mg', 'eff5_efficiency_mg_err']
  values = [-1, None, None, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  e0min=0.97
  e2min=0.96
  e4min=0.89
  e5min = 0.85  

  dirname = '/FDC_Efficiency/Offline'
  histoname1 = 'Expected Hits Vs DOCA'
  histoname2 = 'Measured Hits Vs DOCA'

  min_counts = 100

  h1 = get_histo(rootfile, dirname, histoname1, min_counts)
  h2 = get_histo(rootfile, dirname, histoname2, min_counts)

  if (not h1 or not h2) :
    return values

  else :

    h2.Divide(h1)

    e0 = h2.GetBinContent(1) # // 0.04 mm 
    e2 = h2.GetBinContent(40) # // 2 mm 
    e4 = h2.GetBinContent(80) # // 4 mm
    e5 = h2.GetBinContent(90) # // 5 mm    
    
    e0err = h2.GetBinError(1)
    e2err = h2.GetBinError(40)
    e4err = h2.GetBinError(80)
    e5err = h2.GetBinError(90)
    
    status = 1

    if e0 < e0min or e2 < e2min or e4 < e4min or e5 < e5min:
      status = 0

    values = [status, float('%.2f'%(e0)), float('%.3f'%(e0err)),float('%.2f'%(e2)), float('%.3f'%(e2err)), float('%.2f'%(e4)), float('%.3f'%(e4err)), float('%.2f'%(e5)), float('%.3f'%(e5err))]

    return values




