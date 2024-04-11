import csv

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'Timing'
  names = ['timing_status']    # This will be the overall status graph name for this module, must start with modulename_
  titles = ['Timing status']   # This will be the status graph title
  values = [-1]                 # Default status, keep it at -1


  # list of functions to check, here they should be called with one argument: False, to return names, titles & defaults

  sc_time = sc_rf_time(False)  # return names, titles, values
  tof_time = tof_rf_time(False)  # return names, titles, values
  bcal_neut_time = bcal_neut_rf_time(False)  # return names, titles, values
  bcal_chg_time = bcal_chg_rf_time(False)  # return names, titles, values
  fcal_neut_time = fcal_neut_rf_time(False)  # return names, titles, values
  fcal_chg_time = fcal_chg_rf_time(False)  # return names, titles, values
  cdc_time = cdc_rf_time(False)  # return names, titles, values
  fdc_time = fdc_rf_time(False)  # return names, titles, values
  ps_time = ps_rf_time(False)  # return names, titles, values
  tagh_time = tagh_rf_time(False)  # return names, titles, values
  tagm_time = tagm_rf_time(False)  # return names, titles, values


  for thing in [ sc_time, tof_time, bcal_neut_time, bcal_chg_time, fcal_neut_time, fcal_chg_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # acceptable value limits, defined here for accessibility

  sc_time_min = -0.04
  sc_time_max =  0.04
  tof_time_min = -0.015
  tof_time_max =  0.015
  bcal_neut_time_min = -0.02
  bcal_neut_time_max =  0.02
  bcal_chg_time_min = -0.02
  bcal_chg_time_max =  0.02
  fcal_neut_time_min = -0.1
  fcal_neut_time_max =  0.1
  fcal_chg_time_min = -0.1
  fcal_chg_time_max =  0.1
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

  sc_time = sc_rf_time(rootfile, sc_time_min, sc_time_max)
  tof_time = tof_rf_time(rootfile, tof_time_min, tof_time_max)
  bcal_neut_time = bcal_neut_rf_time(rootfile, bcal_neut_time_min, bcal_neut_time_max)
  bcal_chg_time = bcal_chg_rf_time(rootfile, bcal_chg_time_min, bcal_chg_time_max)
  fcal_neut_time = fcal_neut_rf_time(rootfile, fcal_neut_time_min, fcal_neut_time_max)
  fcal_chg_time = fcal_chg_rf_time(rootfile, fcal_chg_time_min, fcal_chg_time_max)
  cdc_time = cdc_rf_time(rootfile, cdc_time_min, cdc_time_max)
  fdc_time = fdc_rf_time(rootfile, fdc_time_min, fdc_time_max)
  ps_time = ps_rf_time(rootfile, ps_time_min, ps_time_max)
  tagh_time = tagh_rf_time(rootfile, tagh_time_min, tagh_time_max)
  tagm_time = tagm_rf_time(rootfile, tagm_time_min, tagm_time_max)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [ sc_time, tof_time, bcal_neut_time, bcal_chg_time, fcal_neut_time, fcal_chg_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] : 
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]
  for thing in [ sc_time, tof_time, bcal_neut_time, bcal_chg_time, fcal_neut_time, fcal_chg_time, cdc_time, fdc_time, ps_time, tagh_time, tagm_time ] : 
    allvals.extend(thing) 

  return allvals



def sc_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in sc_rf_time() ...")
  names = ['timing_sc_rf_status','timing_sc_rf_mean','timing_sc_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['SC-RF time status','SC-RF time mean (ns)', 'SC-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/SC'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.3
  high_limit = 0.3

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_PiMinus_1D", 25, 250)
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  sc_time_mean = r.Parameter(1)
  sc_time_mean_err = r.Parameter(2)

  status = 1
  if sc_time_mean < timemin or sc_time_mean > timemax:
      status=0


  values = [status, float('%.5f'%(sc_time_mean)), float('%.5f'%(sc_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def tof_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in tof_rf_time() ...")
  names = ['timing_tof_rf_status','timing_tof_rf_mean','timing_tof_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['TOF-RF time status','TOF-RF time mean (ns)', 'TOF-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/TOF'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.15
  high_limit = 0.15

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_PiMinus_1D", 35, 250)
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  tof_time_mean = r.Parameter(1)
  tof_time_mean_err = r.Parameter(2)

  status = 1
  if tof_time_mean < timemin or tof_time_mean > timemax:
      status=0

  values = [status, float('%.5f'%(tof_time_mean)), float('%.5f'%(tof_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def bcal_neut_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in bcal_neut_rf_time() ...")
  names = ['timing_bcal_neut_rf_status','timing_bcal_neut_rf_mean','timing_bcal_neut_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['BCAL (neutral)-RF time status','BCAL (neutral)-RF time mean (ns)', 'BCAL (neutral)-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsShowerE_Photon'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.3
  high_limit = 0.4

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_Photon_1D", 20, 250)
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  bcal_time_mean = r.Parameter(1)
  bcal_time_mean_err = r.Parameter(2)

  status = 1
  if bcal_time_mean < timemin or bcal_time_mean > timemax:
      status=0

  values = [status, float('%.5f'%(bcal_time_mean)), float('%.5f'%(bcal_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def bcal_chg_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in bcal_chg_rf_time() ...")
  names = ['timing_bcal_chg_rf_status','timing_bcal_chg_rf_mean','timing_bcal_chg_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['BCAL (charged)-RF time status','BCAL (charged)-RF time mean (ns)', 'BCAL (charged)-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/BCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.3
  high_limit = 0.4

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_PiMinus_1D")
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  bcal_time_mean = r.Parameter(1)
  bcal_time_mean_err = r.Parameter(2)

  status = 1
  if bcal_time_mean < timemin or bcal_time_mean > timemax:
      status=0

  values = [status, float('%.5f'%(bcal_time_mean)), float('%.5f'%(bcal_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def fcal_neut_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in fcal_neut_rf_time() ...")
  names = ['timing_fcal_neut_rf_status','timing_fcal_neut_rf_mean','timing_fcal_neut_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['FCAL (neutral)-RF time status','FCAL (neutral)-RF time mean (ns)', 'FCAL (neutral)-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsShowerE_Photon'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.5
  high_limit = 0.5

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_Photon_1D")
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  fcal_time_mean = r.Parameter(1)
  fcal_time_mean_err = r.Parameter(2)

  status = 1
  if fcal_time_mean < timemin or fcal_time_mean > timemax:
      status=0

  values = [status, float('%.5f'%(fcal_time_mean)), float('%.5f'%(fcal_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def fcal_chg_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
  #print("in fcal_chg_rf_time() ...")
  names = ['timing_fcal_chg_rf_status','timing_fcal_chg_rf_mean','timing_fcal_chg_rf_mean_err']     # These will be unique graph names, start with modulename_status
  titles = ['FCAL (charged)-RF time status','FCAL (charged)-RF time mean (ns)', 'FCAL (charged)-RF time width (ns)']  # Graph titles 
  values = [-1, -1, -1]   

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'DeltaTVsP_Pi-'      # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorPID/FCAL'          # directory containing that histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  low_limit = 0.5
  high_limit = 0.5

  # code to check the histogram and find the status values
  h1d = h.ProjectionY("DeltaTVsP_PiMinus_1D")
  max = h1d.GetBinCenter(h1d.GetMaximumBin())

  r = h1d.Fit("gaus", "0SQ", "", max - low_limit, max + high_limit)

  if int(r) != 0 :  # bad fit
    return values 

  fcal_time_mean = r.Parameter(1)
  fcal_time_mean_err = r.Parameter(2)

  status = 1
  if fcal_time_mean < timemin or fcal_time_mean > timemax:
      status=0

  values = [status, float('%.5f'%(fcal_time_mean)), float('%.5f'%(fcal_time_mean_err)) ]
  #print(values)
  return values       # return array of values, status first


def cdc_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
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

  low_limit = 15.
  high_limit = 10.

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


def fdc_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
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

  low_limit = 15.
  high_limit = 10.

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


def ps_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
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

  low_limit = 0.3
  high_limit = 0.3

  # code to check the histogram and find the status values
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


def tagh_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
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

  low_limit = 0.3
  high_limit = 0.3

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


def tagm_rf_time(rootfile, timemin=-0.1, timemax=0.1) :
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

  low_limit = 0.3
  high_limit = 0.3

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
