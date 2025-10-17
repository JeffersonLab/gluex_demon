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
  
  fdc_tdc = fdc_tdc_diff(False)
  sc_chans = sc_rf_channels(False)
  tagh_chans = tagh_rf_channels(False)
  tagm_chans = tagm_rf_channels(False)
  sc_adctdc = sc_adctdc_channels(False)
  tof_adctdc = tof_adctdc_channels(False)
  tagh_adctdc = tagh_adctdc_channels(False)
  tagm_adctdc = tagm_adctdc_channels(False)
  
  things = [ sc, tof, bcal, fcal, cdc, fdc, ps, tagh, tagm ] 
  things += [ fdc_tdc, sc_chans, tagh_chans, tagm_chans, sc_adctdc, tof_adctdc, tagh_adctdc, tagm_adctdc ]

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


  fdc_tdcmin = -10
  fdc_tdcmax = 10

  fdc_tdc = fdc_tdc_diff(rootfile, fdc_tdcmin, fdc_tdcmax)
  sc_chans = sc_rf_channels(rootfile)
  tagh_chans = tagh_rf_channels(rootfile)
  tagm_chans = tagm_rf_channels(rootfile)
  sc_adctdc = sc_adctdc_channels(rootfile)
  tof_adctdc = tof_adctdc_channels(rootfile)
  tagh_adctdc = tagh_adctdc_channels(rootfile)
  tagm_adctdc = tagm_adctdc_channels(rootfile)

  things += [ fdc_tdc, sc_chans, tagh_chans, tagm_chans, sc_adctdc, tof_adctdc, tagh_adctdc, tagm_adctdc ]

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

  #print("in sc_rf_time() ...")
  names = ['sc_rf_status', 'pim_SCRF_mg', 'pim_SCRF_mg_err', 'pip_SCRF_mg', 'pip_SCRF_mg_err', 'p_SCRF_mg', 'p_SCRF_mg_err']   
  titles = ['SC-RF time status', 'PiMinus #DeltaT(SC-RF) (ns)',  'PiMinus #DeltaT(SC-RF) width (ns)', 'PiPlus #DeltaT(SC-RF) (ns)',  'PiPlus #DeltaT(SC-RF) width (ns)', 'Proton #DeltaT(SC-RF) (ns)',  'Proton #DeltaT(SC-RF) width (ns)']   # Graph titles 
  values = [-1, None, None, None, None, None, None ]   
    
  if not rootfile :  # called by init function
    return [names, titles, values]

  pi_low_limit = -0.3     # fit ranges
  pi_high_limit = 0.3
  pi_pmin = 0.0
  pi_pmax = 0.0   # no limit if 0.0

  p_low_limit = -0.5
  p_high_limit = 0.5
  p_pmin = 0.0
  p_pmax = 0.0    # no limit if 0.0

  # check the min and max time diff for pi- only  
  pim_max_dt = 0.01

  dirname = '/Independent/Hist_DetectorPID/SC'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)

    if pim[0] == 1: # successful fit
      if abs(pim[1]) > pim_max_dt :
        pim[0] = 0
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)

  values = [pimstatus]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)

  return values

#############
  
def tof_rf_time(rootfile) :

  #print("in tof_rf_time() ...")
  names = ['tof_rf_status', 'pim_TOFRF_mg', 'pim_TOFRF_mg_err', 'pip_TOFRF_mg', 'pip_TOFRF_mg_err', 'p_TOFRF_mg', 'p_TOFRF_mg_err']   
  titles = ['TOF-RF time status', 'PiMinus #DeltaT(TOF-RF) (ns)',  'PiMinus #DeltaT(TOF-RF) width (ns)', 'PiPlus #DeltaT(TOF-RF) (ns)',  'PiPlus #DeltaT(TOF-RF) width (ns)', 'Proton #DeltaT(TOF-RF) (ns)',  'Proton #DeltaT(TOF-RF) width (ns)']   # Graph titles 

  values = [-1, None, None, None, None, None, None ]   
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  pi_low_limit = -0.3     # fit ranges
  pi_high_limit = 0.3
  pi_pmin = 0.0
  pi_pmax = 0.0   # no limit if 0.0

  p_low_limit = -0.5
  p_high_limit = 0.5
  p_pmin = 0.0
  p_pmax = 0.0    # no limit if 0.0

  # check the min and max time diff for pi- only    
  pim_max_dt = 0.005 
  
  dirname = '/Independent/Hist_DetectorPID/TOF'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)

    if pim[0] == 1: # successful fit
      if abs(pim[1]) > pim_max_dt :
        pim[0] = 0    
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)
  
  values = [pimstatus]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)

  return values


##############

def bcal_rf_time(rootfile) :
  
  #print("in bcal_rf_time() ...")
  names = ['bcal_rf_status', 'pim_BCALRF_mg', 'pim_BCALRF_mg_err', 'pip_BCALRF_mg', 'pip_BCALRF_mg_err', 'p_BCALRF_mg', 'p_BCALRF_mg_err', 'g_BCALRF_mg', 'g_BCALRF_mg_err', 'g_1GeV_BCALRF_mg', 'g_1GeV_BCALRF_mg_err']   
  titles = ['BCAL-RF time status', 'PiMinus #DeltaT(BCAL-RF) (ns)',  'PiMinus #DeltaT(BCAL-RF) width (ns)', 'PiPlus #DeltaT(BCAL-RF) (ns)',  'PiPlus #DeltaT(BCAL-RF) width (ns)', 'Proton #DeltaT(BCAL-RF) (ns)',  'Proton #DeltaT(BCAL-RF) width (ns)', 'Photon #DeltaT(BCAL-RF) (ns)',  'Photon #DeltaT(BCAL-RF) width (ns)', 'Photon > 1GeV #DeltaT(BCAL-RF) (ns)',  'Photon > 1GeV #DeltaT(BCAL-RF) width (ns)']   # Graph titles ]   # Graph titles ]   # Graph titles ]   # Graph titles 

  values = [-1, None, None, None, None, None, None, None, None, None, None ]   

  
  if not rootfile :  # called by init function
    return [names, titles, values]

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

  g_max_dt = 0.02  # good if less than this 

  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
  hp = get_histo(rootfile, dirname, histoname, min_counts)

  if hp:
    p = check_deltatvsp(hp, fitoptions, p_pmin, p_pmax, p_low_limit, p_high_limit)
  else:
    p = [-1, None, None]    

    
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram  
  histoname = 'BCALNeutralShowerDeltaTVsE'      # monitoring histogram to check

  hg = get_histo(rootfile, dirname, histoname, min_counts)

  if hg:
    g = check_deltatvsp(hg, fitoptions, g_pmin, g_pmax, g_low_limit, g_high_limit)
    if g[0] == 1:
      if abs(g[1]) > g_max_dt :
        g[0] = 0
    
    gamma1min = 1.0
    g1 = check_deltatvsp(hg, fitoptions, gamma1min, g_pmax, g_low_limit, g_high_limit)
  else:
    g = [-1, None, None]
    g1 = [-1, None, None]        


  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  pstatus = p.pop(0)
  gstatus = g.pop(0)
  g1status = g1.pop(0)     

  values = [gstatus]
  values.extend(pim)
  values.extend(pip)
  values.extend(p)
  values.extend(g)
  values.extend(g1)    

  return values

  

##############

def fcal_rf_time(rootfile) :

  #print("in fcal_rf_time() ...")
  names = ['fcal_rf_status', 'pim_FCALRF_mg', 'pim_FCALRF_mg_err', 'pip_FCALRF_mg', 'pip_FCALRF_mg_err', 'g_FCALRF_mg', 'g_FCALRF_mg_err']   
  titles = ['FCAL-RF time status', 'PiMinus #DeltaT(FCAL-RF) (ns)',  'PiMinus #DeltaT(FCAL-RF) width (ns)', 'PiPlus #DeltaT(FCAL-RF) (ns)',  'PiPlus #DeltaT(FCAL-RF) width (ns)', 'Photon #DeltaT(FCAL-RF) (ns)',  'Photon #DeltaT(FCAL-RF) width (ns)']   # Graph titles 

  values = [-1, None, None, None, None, None, None ]   
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  pi_low_limit = -0.7     # fit ranges
  pi_high_limit = 0.7
  pi_pmin = 0.6
  pi_pmax = 0.0   # no limit if 0.0

  g_low_limit = -0.5
  g_high_limit = 0.5
  g_pmin = 0.0
  g_pmax = 0.0    # no limit if 0.0
  
  g_max_dt = 0.1  # good if less than this
  
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram
  min_counts = 1000
  fitoptions = "0SQI"

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  hpim = get_histo(rootfile, dirname, histoname, min_counts)

  if hpim:
    pim = check_deltatvsp(hpim, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pim = [-1, None, None]

  
  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
  hpip = get_histo(rootfile, dirname, histoname, min_counts)

  if hpip:
    pip = check_deltatvsp(hpip, fitoptions, pi_pmin, pi_pmax, pi_low_limit, pi_high_limit)
  else:
    pip = [-1, None, None]

    
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram  
  histoname = 'FCALNeutralShowerDeltaTVsE'      # monitoring histogram to check

  hg = get_histo(rootfile, dirname, histoname, min_counts)

  if hg:
    g = check_deltatvsp(hg, fitoptions, g_pmin, g_pmax, g_low_limit, g_high_limit)
    if g[0] == 1:
      if abs(g[1]) > g_max_dt :
        g[0] = 0

  else:
    g = [-1, None, None]


  pimstatus = pim.pop(0) 
  pipstatus = pip.pop(0) 
  gstatus = g.pop(0)

  values = [gstatus]
  values.extend(pim)
  values.extend(pip)
  values.extend(g)

  return values

# TODO: check size of resolution or error as well?
def cdc_rf_time(rootfile) :

  #print("in cdc_rf_time() ...")

  names = ['cdc_sc_status','cdc_sc','cdc_sc_err']     # These will be unique graph names, start with modulename_status
  titles = ['CDC-SC time status','Earliest CDC - matched SC time, mean (ns)', 'Earliest CDC - matched SC time, width (ns)']  # Graph titles 

  values = [-1, None, None]
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  time_max = 0.5  # acceptability limits

  low_limit = -15.   # fit range
  high_limit = 10.

  histoname = 'Earliest CDC Time Minus Matched SC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values
    
  fitoptions = "0SQ"
  values = check_deltat(h, fitoptions, time_max, low_limit, high_limit)

  return values

  
# TODO: check size of resolution or error as well?
def fdc_rf_time(rootfile) :
  #print("in fdc_rf_time() ...")
  names = ['fdc_time_status','fdc_t0','fdc_t0_err']     # These will be unique graph names, start with modulename_status
  titles = ['FDC time status','FDC earliest flight-corrected time, mean (ns)', 'FDC earliest flight-corrected time, width (ns)']  # Graph titles 
  values = [-1, None, None ]

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_max = 0.5  # acceptability limits

  low_limit = -15.   # fit range
  high_limit = 10.
  
  histoname = 'Earliest Flight-time Corrected FDC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  fitoptions = "0SQ"
  values = check_deltat(h, fitoptions, time_max, low_limit, high_limit)

  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def ps_rf_time(rootfile) :
  #print("in ps_rf_time() ...")
  names = ['ps_tagh_status','ps_tagh','ps_tagh_err']     # These will be unique graph names, start with modulename_status
  titles = ['PS-TAGH time status','#DeltaT(PS-TAGH) (ns)', '#DeltaT(PS-TAGH) width (ns)']  # Graph titles 
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_max = 0.1   # acceptability limits

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
  if abs(ps_time_mean) > time_max:
      status=0

  values = [status, float('%.5f'%(ps_time_mean)), float('%.5f'%(ps_time_mean_err)) ]

  return values       # return array of values, status first



# TODO: check size of resolution or error as well?
def tagh_rf_time(rootfile) :
  #print("in tagh_rf_time() ...")
  names = ['tagh_rf_status','tagh_rf','tagh_rf_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGH-RF time status','#DeltaT(TAGH-RF) (ns)', '#DeltaT(TAGH-RF) width (ns)']  # Graph titles 
  values = [-1, None, None]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  time_max = 0.03   # acceptability limits

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
  values = check_deltat(h, fitoptions, time_max, low_limit, high_limit)

  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def tagm_rf_time(rootfile) :
  #print("in tagm_rf_time() ...")
  names = ['tagm_rf_status','tagm_rf','tagm_rf_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGM-RF time status','#DeltaT(TAGM-RF) (ns)', '#DeltaT(TAGM-RF) width (ns)']  # Graph titles 
  values = [-1, None, None]   

  if not rootfile :  # called by init function
    return [names, titles, values]
  
  time_max = 0.03   # acceptability limits

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
    values = check_deltat(h, fitoptions, time_max, low_limit, high_limit)

  #print(values)
  return values       # return array of values, status first


def fdc_tdc_diff(rootfile, tdcmin=-2, tdcmax=2) :

  titles = ['FDC TDC status','FDC hit wire time peak, max diff from mean (ns)']
  names = ['fdc_tdc_status','tdc_max_diff']
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/FDC'
  histoname = 'FDCHit Wire time vs. module'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()

  nmin = 0.5*(n/48)   # 0.5 x entries/number of modules (one is always missing?) 
  # find the overall peak time, then look at each module to find the tdiff

  p = h.ProjectionY("p",1,48)   # 400 bins !

  maxbin = p.GetMaximumBin()
  overall_epeak = p.GetXaxis().GetBinCenter(maxbin)
  max_tdiff = 0

  for mod in range(1,49):
    p = h.ProjectionY("p",mod,mod)   # 400 bins !
    #p.Rebin(8)
    if p.GetEntries() > nmin:

      # find the bin with max content, histo looks like spike on flat bg
      maxbin = p.GetMaximumBin()
      epeak = p.GetXaxis().GetBinCenter(maxbin)
      tdiff = epeak - overall_epeak
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff  

  status = 1
  if max_tdiff < tdcmin or max_tdiff > tdcmax:
    status=0

  values = [status, float('%.1f'%(max_tdiff)) ]
  
  return values


def sc_rf_channels(rootfile, diffmin=-0.2, diffmax=0.2) :

  #print("in sc_rf_channels() ...")

  titles = ['SC channel status', 'SC RF time number bad channels','SC RF time maximum difference']
  names = ['sc_channel_status','sc_rftime_bad_channels','sc_rftime_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'
  histoname = 'SC - RF Time vs. Sector'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.  
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.3
  high_limit = 0.3

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values


def tagh_rf_channels(rootfile, diffmin=-0.1, diffmax=0.1) :

  #print("in sc_rf_channels() ...")

  titles = ['TAGH channel status', 'TAGH RF time number bad channels','TAGH RF time maximum difference']
  names = ['tagh_channel_status','tagh_rftime_bad_channels','tagh_rftime_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'
  histoname = 'TAGH - RFBunch Time'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.15
  high_limit = 0.15

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values


def tagm_rf_channels(rootfile, diffmin=-0.1, diffmax=0.1) :

  #print("in sc_rf_channels() ...")

  titles = ['TAGM channel status', 'TAGM RF time number bad channels','TAGM RF time maximum difference']
  names = ['tagm_channel_status','tagm_rftime_bad_channels','tagm_rftime_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'
  histoname = 'TAGM - RFBunch Time'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.3
  high_limit = 0.3

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values

def sc_adctdc_channels(rootfile, diffmin=-0.1, diffmax=0.1) :

  #print("in sc_rf_channels() ...")

  titles = ['SC ADC-TDC channel status', 'SC ADC-TDC time number bad channels','SC ADC-TDC time maximum difference']
  names = ['sc_adctdc_channel_status','sc_adctdc_bad_channels','sc_adctdc_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/SC'
  histoname = 'SCHit TDC_ADC Difference'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.3
  high_limit = 0.3

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values


def tof_adctdc_channels(rootfile, diffmin=-0.5, diffmax=0.5) :

  #print("in sc_rf_channels() ...")

  titles = ['TOF ADC-TDC channel status', 'TOF ADC-TDC time number bad channels','TOF ADC-TDC time maximum difference']
  names = ['tof_adctdc_channel_status','tof_adctdc_bad_channels','tof_adctdc_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TOF'
  histoname = 'TOFHit TDC_ADC Difference'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.15
  high_limit = 0.15

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values


def tagh_adctdc_channels(rootfile, diffmin=-0.1, diffmax=0.1) :

  #print("in sc_rf_channels() ...")

  titles = ['TAGH ADC-TDC channel status', 'TAGH ADC-TDC time number bad channels','TAGH ADC-TDC time maximum difference']
  names = ['tagh_adctdc_channel_status','tagh_adctdc_bad_channels','tagh_adctdc_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TAGH'
  histoname = 'TAGHHit TDC_ADC Difference'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.15
  high_limit = 0.15

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values


def tagm_adctdc_channels(rootfile, diffmin=-0.1, diffmax=0.1) :

  #print("in sc_rf_channels() ...")

  titles = ['TAGM ADC-TDC channel status', 'TAGM ADC-TDC time number bad channels','TAGM ADC-TDC time maximum difference']
  names = ['tagm_adctdc_channel_status','tagm_adctdc_bad_channels','tagm_adctdc_max_diff']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/TAGM'
  histoname = 'TAGMHit TDC_ADC Difference'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  n = h.GetEntries()
  bad_channels = 0
  max_tdiff = 0.
  fitoptions = "0SQ"
  time_max = 10.
  low_limit = -0.3
  high_limit = 0.3

  for mod in range(1,h.GetNbinsX()):
    p = h.ProjectionY("p",mod,mod)  
    #p.Rebin(8)
    if p.GetEntries() > min_counts:

      # find the bin with max content, histo looks like spike on flat bg
      tdiff = check_deltat(p, fitoptions, time_max, low_limit, high_limit)[1]
      if tdiff is None:
      	continue
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff 
        bad_channels = bad_channels + 1

  status = 1
  if max_tdiff < diffmin or max_tdiff > diffmax:
    status=0

  values = [status, bad_channels, float('%.1f'%(max_tdiff)) ]
  
  return values




def check_deltatvsp(h, fitoptions, pmin, pmax, low_limit, high_limit) :

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
    
    values = [ status, float('%.5f'%(mean)), float('%.5f'%(sigma)) ]

  return values



def check_deltat(h, fitoptions, tmax, low_limit, high_limit) :

  values = [ -1, None, None ]   # defaults in case fit fails

  peak = h.GetBinCenter(h.GetMaximumBin())

  fitresult = h.Fit("gaus", fitoptions, "", peak + low_limit, peak + high_limit)
    
  if int(fitresult) == 0:
    mean = fitresult.Parameter(1)
    sigma = fitresult.Parameter(2)
    status = 1
  
    if abs(mean) > tmax :
      status=0
      
    values = [ status, float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
    
  return values
