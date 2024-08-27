import csv

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'Timing'
  names = ['timing_status']    # This will be the overall status graph name for this module, must start with modulename_
  titles = ['Timing status']   # This will be the status graph title
  values = [-1]                 # Default status, keep it at -1


  # list of functions to check, here they should be called with one argument: False, to return names, titles & defaults

  sc_piminus_time = sc_piminus_rf_time(False)  # return names, titles, values
  tof_piminus_time = tof_piminus_rf_time(False)  # return names, titles, values

  bcal_photon_time = bcal_photon_rf_time(False)  # return names, titles, values
  bcal_photon_nominE_time = bcal_photon_nominE_rf_time(False)  # return names, titles, values
  bcal_photon_alt_time = bcal_photon_alt_rf_time(False)  # return names, titles, values
  bcal_piminus_time = bcal_piminus_rf_time(False)  # return names, titles, values

  fcal_photon_time = fcal_photon_rf_time(False)  # return names, titles, values
  fcal_photon_alt_time = fcal_photon_alt_rf_time(False)  # return names, titles, values
  fcal_piminus_time = fcal_piminus_rf_time(False)  # return names, titles, values

  cdc_time = cdc_rf_time(False)  # return names, titles, values
  fdc_time = fdc_rf_time(False)  # return names, titles, values
  ps_time = ps_rf_time(False)  # return names, titles, values
  tagh_time = tagh_rf_time(False)  # return names, titles, values
  tagm_time = tagm_rf_time(False)  # return names, titles, values


  for thing in [ sc_piminus_time, tof_piminus_time, bcal_photon_time, bcal_photon_nominE_time, bcal_photon_alt_time, bcal_piminus_time, fcal_photon_time, fcal_photon_alt_time, fcal_piminus_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # acceptable value limits, defined here for accessibility


  sc_error_max = 0.01
  sc_time_min = -0.04
  sc_time_max =  0.04
  sc_fitmin_piminus = -0.3
  sc_fitmax_piminus = 0.3
  sc_pmin_piminus = 0.0
  sc_pmax_piminus = 0.0 # pmax = 0 means no maximum

  tof_error_max = 0.01
  tof_time_min = -0.015
  tof_time_max =  0.015
  tof_fitmin_piminus = -0.3
  tof_fitmax_piminus = 0.3
  tof_pmin_piminus = 0.0
  tof_pmax_piminus = 0.0

  bcal_error_max = 0.01
  bcal_neut_time_min = -0.02
  bcal_neut_time_max =  0.02
  bcal_fitmin_photon = -0.3 # -0.5 for when it's wide due to empty target
  bcal_fitmax_photon = 0.25 # 0.5
  bcal_fitmin_photon_nominE = -0.3 # -0.5
  bcal_fitmax_photon_nominE = 0.25 # 0.5
  bcal_fitmin_photon_alt = -0.3 # -0.6
  bcal_fitmax_photon_alt = 0.4 # 0.6
  bcal_pmin_photon = 1.0
  bcal_pmax_photon = 0.0
  bcal_pmin_photon_nominE = 0.0
  bcal_pmax_photon_nominE = 0.0
  bcal_pmin_photon_alt = 0.8 # dobbs
  bcal_pmax_photon_alt = 0.0

  bcal_chg_time_min = -0.02
  bcal_chg_time_max =  0.02
  bcal_fitmin_piminus = -0.5
  bcal_fitmax_piminus = 0.5
  bcal_pmin_piminus = 0.0
  bcal_pmax_piminus = 0.0

  fcal_error_max = 0.02
  fcal_neut_time_min = -0.1
  fcal_neut_time_max =  0.1
  fcal_fitmin_photon = -0.4
  fcal_fitmax_photon = 0.3
  fcal_fitmin_photon_alt = -0.6
  fcal_fitmax_photon_alt = 0.6
  fcal_pmin_photon = 1.0
  fcal_pmax_photon = 0.0
  fcal_pmin_photon_alt = 3.0
  fcal_pmax_photon_alt = 0.0

  fcal_chg_time_min = -0.1
  fcal_chg_time_max =  0.1
  fcal_fitmin_piminus = -0.7
  fcal_fitmax_piminus = 0.7
  fcal_pmin_piminus = 0.6
  fcal_pmax_piminus = 0.0
  
  cdc_time_min = -1.
  cdc_time_max =  1.
  
  fdc_time_min = -0.5
  fdc_time_max =  0.5

  ps_time_min = -0.1
  ps_time_max =  0.1

  tagh_time_min = -0.03
  tagh_time_max =  0.03

  tagm_time_min = -0.03
  tagm_time_max =  0.03


  # list of functions to check, here they should be called with rootfile followed by the limits, and return an array of values

  sc_piminus_time = sc_piminus_rf_time(rootfile, sc_time_min, sc_time_max, sc_fitmin_piminus, sc_fitmax_piminus, sc_pmin_piminus, sc_pmax_piminus, sc_error_max)
  tof_piminus_time = tof_piminus_rf_time(rootfile, tof_time_min, tof_time_max, tof_fitmin_piminus, tof_fitmax_piminus, tof_pmin_piminus, tof_pmax_piminus, tof_error_max)
  bcal_photon_time = bcal_photon_rf_time(rootfile, bcal_neut_time_min, bcal_neut_time_max, bcal_fitmin_photon, bcal_fitmax_photon, bcal_pmin_photon, bcal_pmax_photon, bcal_error_max)
  bcal_photon_nominE_time = bcal_photon_nominE_rf_time(rootfile, bcal_neut_time_min, bcal_neut_time_max, bcal_fitmin_photon_nominE, bcal_fitmax_photon_nominE, bcal_pmin_photon_nominE, bcal_pmax_photon_nominE, bcal_error_max)
  bcal_photon_alt_time = bcal_photon_alt_rf_time(rootfile, bcal_neut_time_min, bcal_neut_time_max, bcal_fitmin_photon_alt, bcal_fitmax_photon_alt, bcal_pmin_photon_alt, bcal_pmax_photon_alt, bcal_error_max)
  bcal_piminus_time = bcal_piminus_rf_time(rootfile, bcal_chg_time_min, bcal_chg_time_max, bcal_fitmin_piminus, bcal_fitmax_piminus, bcal_pmin_piminus, bcal_pmax_piminus, bcal_error_max)
  fcal_photon_time = fcal_photon_rf_time(rootfile, fcal_neut_time_min, fcal_neut_time_max, fcal_fitmin_photon, fcal_fitmax_photon, fcal_pmin_photon, fcal_pmax_photon, fcal_error_max)
  fcal_photon_alt_time = fcal_photon_alt_rf_time(rootfile, fcal_neut_time_min, fcal_neut_time_max, fcal_fitmin_photon_alt, fcal_fitmax_photon_alt, fcal_pmin_photon_alt, fcal_pmax_photon_alt, fcal_error_max)
  fcal_piminus_time = fcal_piminus_rf_time(rootfile, fcal_chg_time_min, fcal_chg_time_max, fcal_fitmin_piminus, fcal_fitmax_piminus, fcal_pmin_piminus, fcal_pmax_piminus, fcal_error_max)

  cdc_time = cdc_rf_time(rootfile, cdc_time_min, cdc_time_max)
  fdc_time = fdc_rf_time(rootfile, fdc_time_min, fdc_time_max)
  ps_time = ps_rf_time(rootfile, ps_time_min, ps_time_max)
  tagh_time = tagh_rf_time(rootfile, tagh_time_min, tagh_time_max)
  tagm_time = tagm_rf_time(rootfile, tagm_time_min, tagm_time_max)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [ sc_piminus_time, tof_piminus_time, bcal_photon_time, bcal_photon_nominE_time, bcal_photon_alt_time, bcal_piminus_time, fcal_photon_time, fcal_photon_alt_time, fcal_piminus_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] : 
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]
  for thing in [ sc_piminus_time, tof_piminus_time, bcal_photon_time, bcal_photon_nominE_time, bcal_photon_alt_time, bcal_piminus_time, fcal_photon_time, fcal_photon_alt_time, fcal_piminus_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] : 
    allvals.extend(thing) 

  return allvals



def sc_piminus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in sc_piminus_rf_time() ...")
  names = ['timing_sc_rf_piminus_status','timing_sc_rf_piminus_peak','timing_sc_rf_piminus_mean','timing_sc_rf_piminus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiMinus SC-RF time status','PiMinus SC-RF time peak (ns)','PiMinus SC-RF time mean (ns)', 'PiMinus SC-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/SC'          # directory containing that histogram


  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first


def tof_piminus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in tof_piminus_rf_time() ...")
  names = ['timing_tof_rf_piminus_status','timing_tof_rf_piminus_peak','timing_tof_rf_piminus_mean','timing_tof_rf_piminus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiMinus TOF-RF time status','PiMinus TOF-RF time peak (ns)','PiMinus TOF-RF time mean (ns)', 'PiMinus TOF-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/TOF'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first

def bcal_photon_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_photon_rf_time() ...")
  names = ['timing_bcal_photon_rf_status','timing_bcal_photon_rf_peak','timing_bcal_photon_rf_mean','timing_bcal_photon_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Photon BCAL-RF time status','Photon BCAL-RF time peak (ns)','Photon BCAL-RF time mean (ns)', 'Photon BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'BCALNeutralShowerDeltaTVsE'      # monitoring histogram to check
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  minbin = h.GetXaxis().FindBin(pmin)
  if pmax == 0.0 :
    maxbin = h.GetNbinsX()
  else :
    maxbin = h.GetXaxis().FindBin(pmax)
  h1d = h.ProjectionY("DeltaTVsP_1D", minbin, maxbin)
  if h1d.GetEntries() > 20 :
    peak = h1d.GetBinCenter(h1d.GetMaximumBin())
  else :
    peak = 0.0

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first



def bcal_photon_nominE_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_photon_nominE_rf_time() ...")
  names = ['timing_bcal_photon_nominE_rf_status','timing_bcal_photon_nominE_rf_peak','timing_bcal_photon_nominE_rf_mean','timing_bcal_photon_nominE_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Photon (nominE) BCAL-RF time status','Photon (nominE) BCAL-RF time peak (ns)','Photon (nominE) BCAL-RF time mean (ns)', 'Photon (nominE) BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'BCALNeutralShowerDeltaTVsE'      # monitoring histogram to check
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first




def bcal_photon_alt_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_photon_alt_rf_time() ...")
  names = ['timing_bcal_photon_alt_rf_status','timing_bcal_photon_alt_rf_peak','timing_bcal_photon_alt_rf_mean','timing_bcal_photon_alt_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Photon (alt) BCAL-RF time status','Photon (alt) BCAL-RF time peak (ns)','Photon (alt) BCAL-RF time mean (ns)', 'Photon (alt) BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsShowerE_Photon'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)
#  quad_vertix = TF1("quad_vertix","[0]*(x-[1])*(x-[1])+[2]")
#  quad_vertix.SetParameters(-3000,peak,h1d.GetMaximum())
#  r = h1d.Fit("quad_vertix", "0SQI", "", peak + low_limit, peak + high_limit) # when using this quadratic fit, we don't get a sigma... maybe just set sigma to zero

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)
#  sigma = 0.0 # quad_vertix fit

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first



def bcal_piminus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_piminus_rf_time() ...")
  names = ['timing_bcal_piminus_rf_status','timing_bcal_piminus_rf_peak','timing_bcal_piminus_rf_mean','timing_bcal_piminus_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiMinus BCAL-RF time status','PiMinus BCAL-RF time peak (ns)','PiMinus BCAL-RF time mean (ns)','PiMinus BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first


def fcal_photon_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in fcal_photon_rf_time() ...")
  names = ['timing_fcal_photon_rf_status','timing_fcal_photon_rf_peak','timing_fcal_photon_rf_mean','timing_fcal_photon_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Photon FCAL-RF time status','Photon FCAL-RF time peak (ns)','Photon FCAL-RF time mean (ns)', 'Photon FCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'FCALNeutralShowerDeltaTVsE'      # monitoring histogram to check
  dirname = '/Independent/Hist_Neutrals'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first



def fcal_photon_alt_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in fcal_photon_alt_rf_time() ...")
  names = ['timing_fcal_photon_alt_rf_status','timing_fcal_photon_alt_rf_peak','timing_fcal_photon_alt_rf_mean','timing_fcal_photon_alt_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Photon (alt) FCAL-RF time status','Photon (alt) FCAL-RF time peak (ns)','Photon (alt) FCAL-RF time mean (ns)', 'Photon (alt) FCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsShowerE_Photon'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first




def fcal_piminus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in fcal_piminus_rf_time() ...")
  names = ['timing_fcal_piminus_rf_status','timing_fcal_piminus_rf_peak','timing_fcal_piminus_rf_mean','timing_fcal_piminus_rf_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiMinus FCAL-RF time status','PiMinus FCAL-RF time peak (ns)','PiMinus FCAL-RF time mean (ns)','PiMinus FCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
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

  r = h1d.Fit("gaus", "0SQI", "", peak + low_limit, peak + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  mean = r.Parameter(1)
  mean_error = r.ParError(1)
  sigma = r.Parameter(2)

  status = 1
  if mean < timemin or mean > timemax or mean_error > error_max:
      status=0

  values = [status, float('%.5f'%(peak)), float('%.5f'%(mean)), float('%.5f'%(sigma)) ]
  #print(values)
  return values       # return array of values, status first





# TODO: check size of resolution or error as well?
def cdc_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit = 15., high_limit = 10.) :
  #print("in cdc_rf_time() ...")
  names = ['timing_cdc_sc_status','timing_cdc_sc_mean','timing_cdc_sc_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['CDC-SC time status','Earliest CDC - matched SC time mean (ns)', 'Earliest CDC - matched SC time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'Earliest CDC Time Minus Matched SC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  max = h.GetBinCenter(h.GetMaximumBin())

  r = h.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  cdc_time_mean = r.Parameter(1)
  cdc_time_mean_err = r.Parameter(2)

  status = 1
  if cdc_time_mean < timemin or cdc_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(cdc_time_mean)), float('%.5f'%(cdc_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def fdc_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit = 15., high_limit = 10.) :
  #print("in fdc_rf_time() ...")
  names = ['timing_fdc_time_status','timing_fdc_time_mean','timing_fdc_time_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['FDC time status','FDC earliest flight-corrected time mean (ns)', 'FDC earliest flight-corrected time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'Earliest Flight-time Corrected FDC Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values


  # code to check the histogram and find the status values

  max = h.GetBinCenter(h.GetMaximumBin())

  r = h.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  fdc_time_mean = r.Parameter(1)
  fdc_time_mean_err = r.Parameter(2)

  status = 1
  if fdc_time_mean < timemin or fdc_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(fdc_time_mean)), float('%.5f'%(fdc_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def ps_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit = 0.3, high_limit = 0.3) :
  #print("in ps_rf_time() ...")
  names = ['timing_ps_rf_status','timing_ps_rf_mean','timing_ps_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['PS-TAGH time status','PS-TAGH time mean (ns)', 'PS-TAGH time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

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
  if ps_time_mean < timemin or ps_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(ps_time_mean)), float('%.5f'%(ps_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def tagh_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit = 0.3, high_limit = 0.3) :
  #print("in tagh_rf_time() ...")
  names = ['timing_tagh_rf_status','timing_tagh_rf_mean','timing_tagh_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGH-RF time status','TAGH-RF time mean (ns)', 'TAGH-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'Tagger - RFBunch 1D Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values


  # code to check the histogram and find the status values

  max = h.GetBinCenter(h.GetMaximumBin())

  r = h.Fit("gaus", "0SQ", "", max + low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  tagh_time_mean = r.Parameter(1)
  tagh_time_mean_err = r.Parameter(2)

  status = 1
  if tagh_time_mean < timemin or tagh_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(tagh_time_mean)), float('%.5f'%(tagh_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


# TODO: check size of resolution or error as well?
def tagm_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit = 0.3, high_limit = 0.3) :
  #print("in tagm_rf_time() ...")
  names = ['timing_tagm_rf_status','timing_tagm_rf_mean','timing_tagm_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['TAGM-RF time status','TAGM-RF time mean (ns)', 'TAGM-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'TAGM - RFBunch 1D Time'      # monitoring histogram to check
  dirname = '/HLDetectorTiming/Physics Triggers/TRACKING'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values


  # code to check the histogram and find the status values

  max = h.GetBinCenter(h.GetMaximumBin())

  r = h.Fit("gaus", "0SQ", "", max + low_limit, max + high_limit)
 
  if int(r) != 0 :  # bad fit
    return values 

  tagm_time_mean = r.Parameter(1)
  tagm_time_mean_err = r.Parameter(2)

  status = 1
  if tagm_time_mean < timemin or tagm_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(tagm_time_mean)), float('%.5f'%(tagm_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def get_histo(rootfile, dirname, histoname, min_counts) :

  test = rootfile.GetDirectory(dirname) 

  if (not test):
    #print('Could not find ' + dirname)
    return False

  rootfile.cd(dirname)

  h = gROOT.FindObject(histoname)

  if (not h) :
    #print('Could not find ' + histoname)
    return False

  if h.GetEntries() < min_counts:
    return False

  return h
