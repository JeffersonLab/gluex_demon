
from utils import get_histo
from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1
  pagename = 'FDC'
  titles = ['FDC status']   # add column at the start for overall FDC status
  names = ['fdc_status']
  values = [-1]

  eff = fdc_efficiency(False)
  dedxpos = fdc_dedxpos(False)
  dedxneg = fdc_dedxneg(False)

  things = [ eff, dedxpos, dedxneg ]

  #things = [ eff ]
  
  for thing in things :

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)
  # metrics can be None for unknown (no histo, bad fit)
  
  # acceptable value limits, defined here for accessibility

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5

  tdcmin = -10
  tdcmax = 10

  e0min=0.97
  e2min=0.96
  e4min=0.89
  e5min = 0.85  

  # these return an array [names, values] 

  eff = fdc_efficiency(rootfile, e0min, e2min, e4min)
  
  dedxpos = fdc_dedxpos(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)

  dedxneg = fdc_dedxneg(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)

  # set the overall status to the min value of each histogram status

  statuslist = []

  things = [ eff, dedxpos, dedxneg ]
  
  for thing in things :

    statuslist.append(thing[0])   # status is the first value in the array

  fdc_status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [fdc_status]
  for thing in things :

    allvals.extend(thing) 

  return allvals



def fdc_dedxpos(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['q+ dE/dx status','FDC q+ dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q+ dE/dx resolution at 1.5 GeV/c']
  names = ['dedxpos_status','dedxposmean','dedxposres']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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


def fdc_dedxneg(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['q- dE/dx status','FDC q- dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q- dE/dx resolution at 1.5 GeV/c']
  names = ['dedxneg_status','dedxnegmean','dedxnegres']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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


def fdc_efficiency(rootfile, e0min=0.97, e2min=0.96, e4min=0.89, e5min=0.85) :

  titles = ['FDC efficiency status', 'FDC wire efficiency at 0.04mm', 'FDC wire efficiency at 0.04mm error', 'FDC wire efficiency at 2mm', 'FDC wire efficiency at 2mm error', 'FDC wire efficiency at 4mm', 'FDC wire efficiency at 4mm error', 'FDC wire efficiency at 5mm', 'FDC wire efficiency at 5mm error']
  names = ['eff_status', 'eff0_efficiency_mg', 'eff0_efficiency_mg_err', 'eff2_efficiency_mg', 'eff2_efficiency_mg_err', 'eff4_efficiency_mg', 'eff4_efficiency_mg_err', 'eff5_efficiency_mg', 'eff5_efficiency_mg_err']
  values = [-1, None, None, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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




