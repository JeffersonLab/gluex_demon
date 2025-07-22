# Sean used min of 0.8 GeV for second BCAL photon graph.  Mark's plots use 1 GeV
# Sean checked 2 different histos for neutrals
#

# regular
#  histoname = 'BCALNeutralShowerDeltaTVsE'      # monitoring histogram to check
#  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram

#alt
#  histoname = 'DeltaTVsShowerE_Photon'      # monitoring histogram to check
#  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram


from utils import get_histo     # demon's helper functions
from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'Timing'
  names = ['timing_status']    # This will be the overall status graph name for this module, must start with modulename_
  titles = ['Timing status']   # This will be the status graph title
  values = [-1]                 # Default status, keep it at -1


  # list of functions to check, here they should be called with one argument: False, to return names, titles & defaults

  sc = sc_rf_time(False)  # return names, titles, values
  tof = tof_rf_time(False)  # return names, titles, values
  bcal = bcal_rf_time(False)
  fcal = fcal_rf_time(False)

  cdc = cdc_rf_time(False)
  fdc = fdc_rf_time(False)
  ps = ps_rf_time(False)
  tagh = tagh_rf_time(False)
  tagm = tagm_rf_time(False)
  
  things = [ sc, tof, bcal, fcal, cdc, fdc, ps, tagh, tagm ] 

  for thing in things :   # loop through the arrays returned from each function    

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)


  # list of functions to check, here they should be called with rootfile, followed by the status limits, then the fit and momentum limits, then the error limit, and return an array of values

  sc = sc_rf_time(rootfile)  
  tof = tof_rf_time(rootfile)
  bcal = bcal_rf_time(rootfile)
  fcal = fcal_rf_time(rootfile)
  cdc = cdc_rf_time(rootfile)
  fdc = fdc_rf_time(rootfile)  
  ps = ps_rf_time(rootfile)
  tagh = tagh_rf_time(rootfile)
  tagm = tagm_rf_time(rootfile)
  
  things = [ sc, tof, bcal, fcal, cdc, fdc, ps, tagh, tagm ] 

  # set the overall status to the min value of each histogram status

  statuslist = []
  
  for thing in things : # loop through the arrays returned from each function
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]
  for thing in things :
    allvals.extend(thing) 
    
  return allvals


#############
  
def sc_rf_time(rootfile) :

  #print("in sc_piplus_rf_time() ...")
  names = ['sc_rf_status', 'pim_SCRFdt_mg', 'pim_SCRFdt_mg_err', 'pip_SCRFdt_mg', 'pip_SCRFdt_mg_err', 'proton_SCRFdt_mg', 'proton_SCRFdt_mg_err']   
  titles = ['SC-RF time status', 'PiMinus SC-RF time (ns)',  'PiMinus SC-RF time width (ns)', 'PiPlus SC-RF time (ns)',  'PiPlus SC-RF time width (ns)', 'Proton SC-RF time (ns)',  'Proton SC-RF time width (ns)']   # Graph titles 
  values = [-1, None, None, None, None, None, None ]   
    
  if not rootfile :  # called by init function
    return [names, titles, values]

  error_max = 0.01       # criteria for good/bad
  pi_time_min = -0.1
  pi_time_max = 0.1
  p_time_min = -0.15
  p_time_max = 0.15

  pi_low_limit = -0.3     # fit ranges
  pi_high_limit = 0.3
  pi_pmin = 0.0
  pi_pmax = 0.0   # no limit if 0.0

  p_low_limit = -0.5
  p_high_limit = 0.5
  p_pmin = 0.0
  p_pmax = 0.0    # no limit if 0.0

  dirname = '/Independent/Hist_DetectorPID/SC'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_time_min, p_time_max, error_max, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)

  status = min(pimstatus, pipstatus, pstatus) 

  values = [status]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)

  return values



#############
  
def tof_rf_time(rootfile) :

  #print("in tof_rf_time() ...")
  names = ['tof_rf_status', 'pim_TOFRFdt_mg', 'pim_TOFRFdt_mg_err', 'pip_TOFRFdt_mg', 'pip_TOFRFdt_mg_err', 'proton_TOFRFdt_mg', 'proton_TOFRFdt_mg_err']   
  titles = ['TOF-RF time status', 'PiMinus TOF-RF time (ns)',  'PiMinus TOF-RF time width (ns)', 'PiPlus TOF-RF time (ns)',  'PiPlus TOF-RF time width (ns)', 'Proton TOF-RF time (ns)',  'Proton TOF-RF time width (ns)']   # Graph titles 

  values = [-1, None, None, None, None, None, None ]   
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  error_max = 0.01       # criteria for good/bad
  pi_time_min = -0.04
  pi_time_max = 0.04
  p_time_min = -0.5
  p_time_max = 0.5

  pi_low_limit = -0.3     # fit ranges
  pi_high_limit = 0.3
  pi_pmin = 0.0
  pi_pmax = 0.0   # no limit if 0.0

  p_low_limit = -0.5
  p_high_limit = 0.5
  p_pmin = 0.0
  p_pmax = 0.0    # no limit if 0.0
  
  dirname = '/Independent/Hist_DetectorPID/TOF'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  
  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_time_min, p_time_max, error_max, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)
  
  status = min(pimstatus, pipstatus, pstatus) 

  values = [status]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)

  return values


##############

def bcal_rf_time(rootfile) :
  
  #print("in bcal_rf_time() ...")
  names = ['bcal_rf_piplus_status', 'pim_BCALRFdt_mg', 'pim_BCALRFdt_mg_err', 'pip_BCALRFdt_mg', 'pip_BCALRFdt_mg_err', 'proton_BCALRFdt_mg', 'proton_BCALRFdt_mg_err', 'gamma_BCALRFdt_mg', 'gamma_BCALRFdt_mg_err', 'gamma_1GeV_BCALRFdt_mg', 'gamma_1GeV_BCALRFdt_mg_err']   
  titles = ['BCAL-RF time status', 'PiMinus BCAL-RF time (ns)',  'PiMinus BCAL-RF time width (ns)', 'PiPlus BCAL-RF time (ns)',  'PiPlus BCAL-RF time width (ns)', 'Proton BCAL-RF time (ns)',  'Proton BCAL-RF time width (ns)', 'Photon BCAL-RF time (ns)',  'Photon BCAL-RF time width (ns)', 'Photon > 1GeV BCAL-RF time (ns)',  'Photon > 1GeV BCAL-RF time width (ns)']   # Graph titles ]   # Graph titles ]   # Graph titles ]   # Graph titles 

  values = [-1, None, None, None, None, None, None, None, None, None, None ]   

  
  if not rootfile :  # called by init function
    return [names, titles, values]

  error_max = 0.01       # criteria for good/bad
  pi_time_min = -0.3
  pi_time_max = 0.3
  p_time_min = -0.5
  p_time_max = 0.5
  g_time_min = -0.1
  g_time_max = 0.1

  pi_low_limit = -0.5     # fit ranges
  pi_high_limit = 0.5
  pi_pmin = 0.0
  pi_pmax = 0.0   # no limit if 0.0

  p_low_limit = -0.5
  p_high_limit = 0.5
  p_pmin = 0.0
  p_pmax = 0.0    # no limit if 0.0

  g_low_limit = -0.5
  g_high_limit = 0.5
  g_pmin = 0.0
  g_pmax = 0.0    # no limit if 0.0

  
  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_time_min, p_time_max, error_max, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

    
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram  
  histoname = 'BCALNeutralShowerDeltaTVsE'      # monitoring histogram to check

  hg = get_histo(rootfile, dirname, histoname, min_counts)

  if hg:
    g = check_deltatvsp(hg, fitoptions, g_time_min, g_time_max, error_max, g_pmin, g_pmax, g_low_limit, g_high_limit)
    gamma1min = 1.0
    g1 = check_deltatvsp(hg, fitoptions, g_time_min, g_time_max, error_max, gamma1min, g_pmax, g_low_limit, g_high_limit)
  else:
    g = [-1, None, None]
    g1 = [-1, None, None]        


  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)
  gstatus = g.pop(0)
  g1status = g1.pop(0)     

  status = min(pimstatus, pipstatus, pstatus, gstatus, g1status) 

  values = [status]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)
  values.extend(g)
  values.extend(g1)    

  return values

  

##############

def fcal_rf_time(rootfile) :

  #print("in fcal_rf_time() ...")
  names = ['fcal_rf_piplus_status', 'pim_FCALRFdt_mg', 'pim_FCALRFdt_mg_err', 'pip_FCALRFdt_mg', 'pip_FCALRFdt_mg_err', 'gamma_FCALRFdt_mg', 'gamma_FCALRFdt_mg_err']   
  titles = ['FCAL-RF time status', 'PiMinus FCAL-RF time (ns)',  'PiMinus FCAL-RF time width (ns)', 'PiPlus FCAL-RF time (ns)',  'PiPlus FCAL-RF time width (ns)', 'Photon FCAL-RF time (ns)',  'Photon FCAL-RF time width (ns)']   # Graph titles 

  values = [-1, None, None, None, None, None, None ]   
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  error_max = 0.02       # criteria for good/bad
  pi_time_min = -0.3
  pi_time_max = 0.3
  g_time_min = -0.1
  g_time_max = 0.1

  pi_low_limit = -0.7     # fit ranges
  pi_high_limit = 0.7
  pi_pmin = 0.6
  pi_pmax = 0.0   # no limit if 0.0

  g_low_limit = -0.5
  g_high_limit = 0.5
  g_pmin = 0.0
  g_pmax = 0.0    # no limit if 0.0
  
  
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_time_min, pi_time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram  
  histoname = 'FCALNeutralShowerDeltaTVsE'      # monitoring histogram to check

  hg = get_histo(rootfile, dirname, histoname, min_counts)

  if hg:
    g = check_deltatvsp(hg, fitoptions, g_time_min, g_time_max, error_max, g_pmin, g_pmax, g_low_limit, g_high_limit)
  else:
    g = [-1, None, None]


  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  gstatus = g.pop(0)

  status = min(pimstatus, pipstatus, gstatus) 

  values = [status]
  values.extend(pim)
  values.extend(pip)
  values.extend(g)

  return values

  

# TODO: check size of resolution or error as well?
def cdc_rf_time(rootfile) :

  #print("in cdc_rf_time() ...")

  names = ['cdc_sc_status','cdc_sc_mean','cdc_sc_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['CDC-SC time status','Earliest CDC - matched SC time mean (ns)', 'Earliest CDC - matched SC time width (ns)']  # Graph titles 

  values = [-1, None, None]
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  time_min = -1.5   # acceptability limits
  time_max = 1.5

  low_limit = -15.   # fit range
  high_limit = 10.

  histoname = 'Earliest CDC Time Minus Matched SC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values
    
  fitoptions = "0SQ"
  values = check_deltat(h, fitoptions, time_min, time_max, low_limit, high_limit)

  return values

  
# TODO: check size of resolution or error as well?
def fdc_rf_time(rootfile) :
  #print("in fdc_rf_time() ...")
  names = ['fdc_time_status','fdc_time_mean','fdc_time_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['FDC time status','FDC earliest flight-corrected time mean (ns)', 'FDC earliest flight-corrected time width (ns)']  # Graph titles 
  values = [-1, None, None ]

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_min = -1   # acceptability limits
  time_max = 1

  low_limit = -15.   # fit range
  high_limit = 10.
  
  histoname = 'Earliest Flight-time Corrected FDC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  fitoptions = "0SQ"
  values = check_deltat(h, fitoptions, time_min, time_max, low_limit, high_limit)
  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def ps_rf_time(rootfile) :
  #print("in ps_rf_time() ...")
  names = ['ps_rf_status','ps_rf_mean','ps_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['PS-TAGH time status','PS-TAGH time mean (ns)', 'PS-TAGH time width (ns)']  # Graph titles 
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_min = -0.1   # acceptability limits
  time_max = 0.1

  low_limit = 0.3    # fit range
  high_limit = 0.3

  histoname = 'PSTAGH_tdiffVsEdiff'      # monitoring histogram to check
  dirname = '/PSPair/PSC_PS_TAGH/'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the resolution or error and find the status values
  h1d = h.ProjectionY("tdiffVsEdiff_1D")
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  ps_time_mean = r.Parameter(1)
  ps_time_mean_err = r.Parameter(2)

  status = 1
  if ps_time_mean < time_min or ps_time_mean > time_max:
      status=0


  values = [status, float('%.5f'%(ps_time_mean)), float('%.5f'%(ps_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first



# TODO: check size of resolution or error as well?
def tagh_rf_time(rootfile) :
  #print("in tagh_rf_time() ...")
  names = ['tagh_rf_status','tagh_rf_mean','tagh_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGH-RF time status','TAGH-RF time mean (ns)', 'TAGH-RF time width (ns)']  # Graph titles 
  values = [-1, None, None]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_min = -5   # acceptability limits
  time_max = 5

  low_limit = -0.3    # fit range
  high_limit = 0.3

  histoname = 'Tagger - RFBunch 1D Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  fitoptions = "0SQ"
  values = check_deltat(h, fitoptions, time_min, time_max, low_limit, high_limit)

  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def tagm_rf_time(rootfile) :
  #print("in tagm_rf_time() ...")
  names = ['tagm_rf_status','tagm_rf_mean','tagm_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGM-RF time status','TAGM-RF time mean (ns)', 'TAGM-RF time width (ns)']  # Graph titles 
  values = [-1, None, None]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_min = -5   # acceptability limits
  time_max = 5

  low_limit = -0.3    # fit range
  high_limit = 0.3

  histoname = 'TAGM - RFBunch 1D Time'      # monitoring histogram to check  
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  if h:
    fitoptions = "0SQ"
    values = check_deltat(h, fitoptions, time_min, time_max, low_limit, high_limit)

  #print(values)
  return values       # return array of values, status first



#    pim = check_deltatvsp(hpim, fitoptions, time_min, time_max, error_max, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)

def check_deltatvsp(h, fitoptions, tmin, tmax, emax, pmin, pmax, low_limit, high_limit) :

  values = [ -1, None, None ]   # defaults in case fit fails

  minbin = h.GetXaxis().FindBin(pmin)
  if pmax == 0.0 :
    maxbin = h.GetNbinsX()
  else :
    maxbin = h.GetXaxis().FindBin(pmax)
    
  h1d = h.ProjectionY("DeltaTVsP_1D", minbin, maxbin)
  
  if h1d.GetEntries() > 100 :
    peak = h1d.GetBinCenter(h1d.GetMaximumBin())
  else :
    peak = 0.0

  fitresult = h1d.Fit("gaus", fitoptions, "", peak + low_limit, peak + high_limit)
  
  if int(fitresult) == 0:
    mean = fitresult.Parameter(1)
    mean_error = fitresult.ParError(1)    
    sigma = fitresult.Parameter(2)
    status = 1
    
    if mean < tmin or mean > tmax or abs(mean_error) > emax:
      status=0

    values = [ status, float('%.5f'%(mean)), float('%.5f'%(sigma)) ]

  return values



def check_deltat(h, fitoptions, tmin, tmax, low_limit, high_limit) :

  values = [ -1, None, None ]   # defaults in case fit fails

  peak = h.GetBinCenter(h.GetMaximumBin())

  fitresult = h.Fit("gaus", fitoptions, "", peak + low_limit, peak + high_limit)
    
  if int(fitresult) == 0:
    mean = fitresult.Parameter(1)
    sigma = fitresult.Parameter(2)
    status = 1
  
    if mean < tmin or mean > tmax :
      status=0
      
    values = [ status, float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
    
  return values
