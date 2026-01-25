from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'RF'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [rf_tagh_tof, rf_psc_tof, rf_fdc_tof, rf_fdc_tagh, rf_fdc_psc, rf_psc_tagh]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def rf_tagh_tof(rootfile) :

  names = ['rf_tagh_tof_status','tagh_tof','tagh_tof_err']
  titles = ['DeltaT (RF_TAGH - RF_TOF) status', 'DeltaT (RF_TAGH - RF_TOF)', '#sigma DeltaT (RF_TAGH - RF_TOF)' ]
  values = [-1, None, None] 

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1
  
  histoname = 'RFDeltaT_TAGH_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  if h.GetEntries() < 100 :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first



def rf_psc_tof(rootfile) : 

  names = ['rf_psc_tof_status','psc_tof','psc_tof_err']
  titles = ['DeltaT(RF_PSC - RF_TOF) status', 'DeltaT (RF_PSC - RF_TOF)', '#sigma DeltaT (RF_PSC - RF_TOF)' ]
  values = [-1, None, None] 

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1

  histoname = 'RFDeltaT_PSC_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  if h.GetEntries() < 100 :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first




def rf_fdc_tof(rootfile) :

  names = ['rf_fdc_tof_status','fdc_tof','fdc_tof_err']
  titles = ['DeltaT (RF_FDC - RF_TOF) status', 'DeltaT (RF_FDC - RF_TOF)', '#sigma DeltaT (RF_FDC - RF_TOF)' ]
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1
  
  histoname = 'RFDeltaT_FDC_TOF'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first





def rf_fdc_tagh(rootfile) :

  names = ['rf_fdc_tagh_status','fdc_tagh','fdc_tagh_err']
  titles = ['DeltaT (RF_FDC - RF_TAGH) status', 'DeltaT (RF_FDC - RF_TAGH)', '#sigma DeltaT (RF_FDC - RF_TAGH)' ]
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1

  histoname = 'RFDeltaT_FDC_TAGH'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if not h:
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first




def rf_fdc_psc(rootfile) :

  names = ['rf_fdc_psc_status','fdc_psc','fdc_psc_err']
  titles = ['DeltaT (RF_FDC - RF_PSC) status', 'DeltaT (RF_FDC - RF_PSC)', '#sigma DeltaT (RF_FDC - RF_PSC)' ]
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1
  
  histoname = 'RFDeltaT_FDC_PSC'   # monitoring histogram to check
  dirname = '/RF/DeltaT_RF_OtherRFs'      # directory containing the histogram

  h = get_histo(rootfile, dirname, histoname, min_counts=100)

  if (not h) :
    return values

  values = fit_histo(h, tmax)
  
  return values       # return array of values, status first



def rf_psc_tagh(rootfile) :

  names = ['rf_psc_tagh_status','psc_tagh','psc_tagh_err']
  titles = ['DeltaT (RF_PSC - RF_TAGH) status', 'DeltaT (RF_PSC - RF_TAGH)', '#sigma DeltaT (RF_PSC - RF_TAGH)' ]
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  tmax = 0.1

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
