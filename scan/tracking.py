from utils import get_histo     # demon's helper functions
from ROOT import gROOT

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.

def init() : 

  pagename = 'Tracking'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['tracking_status']    # Graph name, new_module_status 
  titles = ['tracking status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  f = fom(False)  # return names, titles, values
  nc = ncandidates(False)
  nw = nwirebasedtracks(False)
  nt = ntimebasedtracks(False)    
  bcal = bcal_matchrate(False)
  ecal = ecal_matchrate(False)
  fcal = fcal_matchrate(False)
  sc = sc_matchrate(False)
  tof = tof_matchrate(False)
  
  

  for thing in [ f, nc, nw, nt, bcal, ecal, fcal, sc, tof ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # List of custom functions, called with argument rootfile
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  f = fom(rootfile)

  nc = ncandidates(rootfile)
  nw = nwirebasedtracks(rootfile)
  nt = ntimebasedtracks(rootfile)    

  bcal = bcal_matchrate(rootfile)
  ecal = ecal_matchrate(rootfile)
  fcal = fcal_matchrate(rootfile)
  sc = sc_matchrate(rootfile)
  tof = tof_matchrate(rootfile)
  
  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [f, nc, nw, nt, bcal, ecal, fcal, sc, tof] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [f, nc, nw, nt, bcal, ecal, fcal, sc, tof] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 


def fom(rootfile, llim=0.3, ulim=0.9 ) :

  names = ['fom_min_status','fom_min']            
  titles = ['Tracking FOM status','Tracking FOM histo minimum']   # Graph titles
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'TrackingFOM'      # monitoring histogram to check
  dirname = '/Independent/Hist_Reconstruction/Tracking/'          # directory containing that histogram


  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  tracking_fom_min = h.GetXaxis().GetBinCenter(h.GetMinimumBin())

  status=1

  if tracking_fom_min < llim:
    status=0

  if tracking_fom_min > ulim:
    status=0

  values = [status, float('%.2f'%(tracking_fom_min)) ]

  return values       # return array of values, status first
  


def ncandidates(rootfile) :

  # Example custom function to check another histogram

  #print('in tracking_candidates()...')

# Provide unique graph names, starting with 'tracking_'. The first must be the status code from this function. Do not call it tracking_status - call it something else ending with _status, eg tracking_functionname_status.

  names = ['ncandidates_status','candidates']  
  titles = ['Track candidates status','Mean number of track candidates'] # graph titles
  values = [-1, None]                                       # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'NumTrackCandidates'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit

  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0


  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def nwirebasedtracks(rootfile) :

  # Example custom function to check another histogram

  #print('in nwirebasedtracks()...')

# Provide unique graph names, starting with 'tracking_'. The first must be the status code from this function. Do not call it tracking_status - call it something else ending with _status, eg tracking_functionname_status.

  names = ['nwirebasedtracks_status','wire_based']  
  titles = ['Wire-based tracks status','Mean number of wire-based tracks'] # graph titles
  values = [-1, None]                                       # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'NumWireBasedTracks'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit

  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0


  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def ntimebasedtracks(rootfile) :

  # Example custom function to check another histogram

  #print('in ntimebasedtracks()...')

# Provide unique graph names, starting with 'tracking_'. The first must be the status code from this function. Do not call it tracking_status - call it something else ending with _status, eg tracking_functionname_status.

  names = ['ntimebasedtracks_status','time_based']  
  titles = ['Time-based tracks status','Mean number of time-based tracks'] # graph titles
  values = [-1, None]                                       # Default values, keep as -1
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'NumTimeBasedTracks'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit

  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0


  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def bcal_matchrate(rootfile) :

  # Example custom function to check another histogram

  #print('in ntimebasedtracks()...')

# Provide unique graph names, starting with 'tracking_'. The first must be the status code from this function. Do not call it tracking_status - call it something else ending with _status, eg tracking_functionname_status.

  names = ['bcalmatch_status','bcal_match']  
  titles = ['BCAL track match rate status','BCAL match rate'] # graph titles
  values = [-1, None]                                       # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'TrackBCALModuleVsZ_HasHit'
  dirname = '/Independent/Hist_DetectorMatching/TimeBased/BCAL'
  
  llim = 0.77    # acceptability limit

  min_counts=100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  hits = h.GetEntries()

  histoname = 'TrackBCALModuleVsZ_NoHit'
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  nohits = h.GetEntries()

  chances = hits + nohits

  if chances == 0:
    return values
  
  match_rate = hits/chances

  status = 1
  if match_rate < llim : 
      status=0


  values = [status, float('%.3f'%(match_rate)) ]
  
  return values       # return array of values, status first



def ecal_matchrate(rootfile) :

  names = ['ecal_match_status','ecal_match','ecal_match_1g']  
  titles = ['ECAL track match rate status','ECAL match rate','ECAL match rate > 1GeV'] 
  values = [-1, None, None]                                      

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/ECAL'
  
  llim = 0.3    # acceptability limit
  llim2 = 0.55

  min_counts=100

  histoname = 'TrackECALP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackECALP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackECALR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackECALR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2
  
  return values       # return array of values, status first


def fcal_matchrate(rootfile) :

  names = ['fcal_match_status','fcal_match','fcal_match_1g']  
  titles = ['FCAL track match rate status','FCAL match rate','FCAL match rate > 1GeV'] # graph titles
  values = [-1, None, None]                                       # Defult values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/FCAL'
  
  llim = 0.33    # acceptability limit
  llim2 = 0.42

  min_counts=100

  histoname = 'TrackFCALP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackFCALP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackFCALR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackFCALR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2

  
  return values       # return array of values, status first



def sc_matchrate(rootfile) :

  names = ['sc_match_status','sc_match']  
  titles = ['SC track match rate status','SC match rate']
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/SC'
  
  llim = 0.86    # acceptability limit

  min_counts=100

  histoname = 'SCPaddleVsZ_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'SCPaddleVsZ_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        values[0] = 1
  
  return values       # return array of values, status first



def tof_matchrate(rootfile) :

  names = ['tof_match_status','tof_match','tof_match_1g']  
  titles = ['TOF track match rate status','TOF match rate','TOF match rate > 1GeV'] # graph titles
  values = [-1, None, None]                                       # Defult values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/TOFPoint'
  
  llim = 0.25    # acceptability limit
  llim2 = 0.36

  min_counts=100

  histoname = 'TrackTOFP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackTOFR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2

  
  return values       # return array of values, status first

