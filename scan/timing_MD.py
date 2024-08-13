import csv

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'Timing_MD'
  names = ['timing_MD_status']    # This will be the overall status graph name for this module, must start with modulename_
  titles = ['Timing status']   # This will be the status graph title
  values = [-1]                 # Default status, keep it at -1


  # list of functions to check, here they should be called with one argument: False, to return names, titles & defaults

  sc_piplus_time = sc_piplus_rf_time(False)  # return names, titles, values
  sc_proton_time = sc_proton_rf_time(False)  # return names, titles, values
  tof_piplus_time = tof_piplus_rf_time(False)  # return names, titles, values
  tof_proton_time = tof_proton_rf_time(False)  # return names, titles, values
  bcal_piplus_time = bcal_piplus_rf_time(False)  # return names, titles, values
  bcal_proton_time = bcal_proton_rf_time(False)  # return names, titles, values
  fcal_piplus_time = fcal_piplus_rf_time(False)  # return names, titles, values
  fcal_proton_time = fcal_proton_rf_time(False)  # return names, titles, values


  for thing in [ sc_piplus_time, sc_proton_time, tof_piplus_time, tof_proton_time, bcal_piplus_time, bcal_proton_time, fcal_piplus_time, fcal_proton_time ] :   # loop through the arrays returned from each function

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
  sc_fitmin_piplus = -0.3
  sc_fitmax_piplus = 0.3
  sc_fitmin_proton = -0.3
  sc_fitmax_proton = 0.3
  sc_pmin_piminus = 0.0
  sc_pmax_piminus = 0.0 # pmax = 0 means no maximum
  sc_pmin_piplus = 0.0
  sc_pmax_piplus = 0.0
  sc_pmin_proton = 0.6
  sc_pmax_proton = 10.0

  tof_error_max = 0.01
  tof_time_min = -0.015
  tof_time_max =  0.015
  tof_fitmin_piminus = -0.3
  tof_fitmax_piminus = 0.3
  tof_fitmin_piplus = -0.3
  tof_fitmax_piplus = 0.3
  tof_fitmin_proton = -0.15
  tof_fitmax_proton = 0.3
  tof_pmin_piminus = 0.0
  tof_pmax_piminus = 0.0
  tof_pmin_piplus = 0.0
  tof_pmax_piplus = 0.0
  tof_pmin_proton = 0.0
  tof_pmax_proton = 2.0

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
  bcal_fitmin_piplus = -0.5
  bcal_fitmax_piplus = 0.4
  bcal_fitmin_proton = -0.3
  bcal_fitmax_proton = 0.5
  bcal_pmin_piminus = 0.0
  bcal_pmax_piminus = 0.0
  bcal_pmin_piplus = 0.0
  bcal_pmax_piplus = 0.0
  bcal_pmin_proton = 0.0
  bcal_pmax_proton = 0.0

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
  fcal_fitmin_piplus = -0.7
  fcal_fitmax_piplus = 0.5
  fcal_fitmin_proton = -0.9
  fcal_fitmax_proton = 0.9
  fcal_pmin_piminus = 0.6
  fcal_pmax_piminus = 0.0
  fcal_pmin_piplus = 0.6
  fcal_pmax_piplus = 0.0
  fcal_pmin_proton = 0.0
  fcal_pmax_proton = 0.0

  # list of functions to check, here they should be called with rootfile, followed by the status limits, then the fit and momentum limits, then the error limit, and return an array of values

  sc_piplus_time = sc_piplus_rf_time(rootfile, sc_time_min, sc_time_max, sc_fitmin_piplus, sc_fitmax_piplus, sc_pmin_piplus, sc_pmax_piplus, sc_error_max)
  sc_proton_time = sc_proton_rf_time(rootfile, sc_time_min, sc_time_max, sc_fitmin_proton, sc_fitmax_proton, sc_pmin_proton, sc_pmax_proton, sc_error_max)
  tof_piplus_time = tof_piplus_rf_time(rootfile, tof_time_min, tof_time_max, tof_fitmin_piplus, tof_fitmax_piplus, tof_pmin_piplus, tof_pmax_piplus, tof_error_max)
  tof_proton_time = tof_proton_rf_time(rootfile, tof_time_min, tof_time_max, tof_fitmin_proton, tof_fitmax_proton, tof_pmin_proton, tof_pmax_proton, tof_error_max)
  bcal_piplus_time = bcal_piplus_rf_time(rootfile, bcal_chg_time_min, bcal_chg_time_max, bcal_fitmin_piplus, bcal_fitmax_piplus, bcal_pmin_piplus, bcal_pmax_piplus, bcal_error_max)
  bcal_proton_time = bcal_proton_rf_time(rootfile, bcal_chg_time_min, bcal_chg_time_max, bcal_fitmin_proton, bcal_fitmax_proton, bcal_pmin_proton, bcal_pmax_proton, bcal_error_max)
  fcal_piplus_time = fcal_piplus_rf_time(rootfile, fcal_chg_time_min, fcal_chg_time_max, fcal_fitmin_piplus, fcal_fitmax_piplus, fcal_pmin_piplus, fcal_pmax_piplus, fcal_error_max)
  fcal_proton_time = fcal_proton_rf_time(rootfile, fcal_chg_time_min, fcal_chg_time_max, fcal_fitmin_proton, fcal_fitmax_proton, fcal_pmin_proton, fcal_pmax_proton, fcal_error_max)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [ sc_piplus_time, sc_proton_time, tof_piplus_time, tof_proton_time, bcal_piplus_time, bcal_proton_time, fcal_piplus_time, fcal_proton_time ] : 
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]
  for thing in [ sc_piplus_time, sc_proton_time, tof_piplus_time, tof_proton_time, bcal_piplus_time, bcal_proton_time, fcal_piplus_time, fcal_proton_time ] : 
    allvals.extend(thing) 

  return allvals




def sc_piplus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in sc_piplus_rf_time() ...")
  names = ['timing_MD_sc_rf_piplus_status','timing_MD_sc_rf_piplus_peak','timing_MD_sc_rf_piplus_mean','timing_MD_sc_rf_piplus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiPlus SC-RF time status','PiPlus SC-RF time peak (ns)','PiPlus SC-RF time mean (ns)', 'PiPlus SC-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
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



def sc_proton_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in sc_proton_rf_time() ...")
  names = ['timing_MD_sc_rf_proton_status','timing_MD_sc_rf_proton_peak','timing_MD_sc_rf_proton_mean','timing_MD_sc_rf_proton_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Proton SC-RF time status','Proton SC-RF time peak (ns)','Proton SC-RF time mean (ns)', 'Proton SC-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
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




def tof_piplus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in tof_piplus_rf_time() ...")
  names = ['timing_MD_tof_rf_piplus_status','timing_MD_tof_rf_piplus_peak','timing_MD_tof_rf_piplus_mean','timing_MD_tof_rf_piplus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiPlus TOF-RF time status','PiPlus TOF-RF time peak (ns)','PiPlus TOF-RF time mean (ns)', 'PiPlus TOF-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
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



def tof_proton_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in tof_proton_rf_time() ...")
  names = ['timing_MD_tof_rf_proton_status','timing_MD_tof_rf_proton_peak','timing_MD_tof_rf_proton_mean','timing_MD_tof_rf_proton_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Proton TOF-RF time status','Proton TOF-RF time peak (ns)','Proton TOF-RF time mean (ns)', 'Proton TOF-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
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





def bcal_piplus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_piplus_rf_time() ...")
  names = ['timing_MD_bcal_rf_piplus_status','timing_MD_bcal_rf_piplus_peak','timing_MD_bcal_rf_piplus_mean','timing_MD_bcal_rf_piplus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiPlus BCAL-RF time status','PiPlus BCAL-RF time peak (ns)','PiPlus BCAL-RF time mean (ns)', 'PiPlus BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
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



def bcal_proton_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in bcal_proton_rf_time() ...")
  names = ['timing_MD_bcal_rf_proton_status','timing_MD_bcal_rf_proton_peak','timing_MD_bcal_rf_proton_mean','timing_MD_bcal_rf_proton_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Proton BCAL-RF time status','Proton BCAL-RF time peak (ns)','Proton BCAL-RF time mean (ns)', 'Proton BCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
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





def fcal_piplus_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in fcal_piplus_rf_time() ...")
  names = ['timing_MD_fcal_rf_piplus_status','timing_MD_fcal_rf_piplus_peak','timing_MD_fcal_rf_piplus_mean','timing_MD_fcal_rf_piplus_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['PiPlus FCAL-RF time status','PiPlus FCAL-RF time peak (ns)','PiPlus FCAL-RF time mean (ns)', 'PiPlus FCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi+'      # monitoring histogram to check
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



def fcal_proton_rf_time(rootfile, timemin=-0.1, timemax=0.1, low_limit=-0.5, high_limit=0.5, pmin=0.0, pmax=0.0, error_max=0.1) :
  #print("in fcal_proton_rf_time() ...")
  names = ['timing_MD_fcal_rf_proton_status','timing_MD_fcal_rf_proton_peak','timing_MD_fcal_rf_proton_mean','timing_MD_fcal_rf_proton_sigma']     # These will be unique graph names, start with modulename_status
  titles = ['Proton FCAL-RF time status','Proton FCAL-RF time peak (ns)','Proton FCAL-RF time mean (ns)', 'Proton FCAL-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Proton'      # monitoring histogram to check
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


def get_histo(rootfile, dirname, histoname, min_counts) :

  test = rootfile.GetDirectory(dirname) 

  # file pointer contains tobj if dir exists, set false if not

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
