
from utils import get_histo
from ROOT import gROOT, TF1
#ROOT.gErrorIgnoreLevel = ROOT.kError

def init() : 

  pagename = 'RF'          # Title for the page of graphs

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['rf_status']    # Graph name
  titles = ['RF status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  tagh_tof = rf_tagh_tof(False)
  psc_tof = rf_psc_tof(False)
  fdc_tof = rf_fdc_tof(False)
  fdc_tagh = rf_fdc_tagh(False)
  fdc_psc = rf_fdc_psc(False)
  psc_tagh = rf_psc_tagh(False)
  
  thinglist = [ tagh_tof , psc_tof, fdc_tof, fdc_tagh, fdc_psc, psc_tagh ]

  for thing in thinglist: 

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # Acceptable value limits, defined here for accessibility


  tagh_tof_tmax = 0.1;
  psc_tof_tmax = 0.1;
  fdc_tof_tmax = 0.1;
  fdc_tagh_tmax = 0.1;
  fdc_psc_tmax = 0.1;
  psc_tagh_tmax = 0.1;

 
  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  tagh_tof = rf_tagh_tof(rootfile, tagh_tof_tmax)
  psc_tof = rf_psc_tof(rootfile, psc_tof_tmax)
  fdc_tof = rf_fdc_tof(rootfile, fdc_tof_tmax)
  fdc_tagh = rf_fdc_tagh(rootfile, fdc_tagh_tmax)
  fdc_psc = rf_fdc_psc(rootfile, fdc_psc_tmax)
  psc_tagh = rf_psc_tagh(rootfile, psc_tagh_tmax)


  # This finds the overall status, setting it to the min value of each histogram status

  thinglist = [ tagh_tof , psc_tof, fdc_tof, fdc_tagh, fdc_psc, psc_tagh ]

  statuslist = []
  for thing in thinglist :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in thinglist :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 



def rf_tagh_tof(rootfile, tmax=0.1) :

  names = ['rf_tagh_tof_status','tagh_tof','tagh_tof_err']
  titles = ['DeltaT (RF_TAGH - RF_TOF) status', 'DeltaT (RF_TAGH - RF_TOF)', '#sigma DeltaT (RF_TAGH - RF_TOF)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_TAGH_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  if h.GetEntries() < 100 :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first



def rf_psc_tof(rootfile, tmax=0.1) : 

  names = ['rf_psc_tof_status','psc_tof','psc_tof_err']
  titles = ['DeltaT(RF_PSC - RF_TOF) status', 'DeltaT (RF_PSC - RF_TOF)', '#sigma DeltaT (RF_PSC - RF_TOF)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_PSC_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  if h.GetEntries() < 100 :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first




def rf_fdc_tof(rootfile, tmax=0.1) :

  names = ['rf_fdc_tof_status','fdc_tof','fdc_tof_err']
  titles = ['DeltaT (RF_FDC - RF_TOF) status', 'DeltaT (RF_FDC - RF_TOF)', '#sigma DeltaT (RF_FDC - RF_TOF)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_FDC_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first





def rf_fdc_tagh(rootfile, tmax=0.1) :

  names = ['rf_fdc_tagh_status','fdc_tagh','fdc_tagh_err']
  titles = ['DeltaT (RF_FDC - RF_TAGH) status', 'DeltaT (RF_FDC - RF_TAGH)', '#sigma DeltaT (RF_FDC - RF_TAGH)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_FDC_TAGH'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first




def rf_fdc_psc(rootfile, tmax=0.1) :

  names = ['rf_fdc_psc_status','fdc_psc','fdc_psc_err']
  titles = ['DeltaT (RF_FDC - RF_PSC) status', 'DeltaT (RF_FDC - RF_PSC)', '#sigma DeltaT (RF_FDC - RF_PSC)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_FDC_PSC'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if (not h) :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first



def rf_psc_tagh(rootfile, tmax=0.1) :

  names = ['rf_psc_tagh_status','psc_tagh','psc_tagh_err']
  titles = ['DeltaT (RF_PSC - RF_TAGH) status', 'DeltaT (RF_PSC - RF_TAGH)', '#sigma DeltaT (RF_PSC - RF_TAGH)' ]
  values = [-1, None, None]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'RFDeltaT_PSC_TAGH'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if (not h) :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first



def fit_histo(h, tmax) :

  values = [ -1, None, None ]
  status = -1

  g = TF1('g','gaus',-2, 2)
  fitstat = h.Fit('g','0qlrs')
  
  if int(fitstat) == 0:
    tmean = g.GetParameter(1)
    tsig = g.GetParameter(2)

    if abs(tmean) < tmax : 
      status = 1
    else :
      status = 0

    values = [status, float('%.5f'%(tmean)), float('%.5f'%(tsig)) ] 


  return values  
