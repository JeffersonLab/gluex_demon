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


  for thing in [ f, nc, nw, nt ] :   # loop through the arrays returned from each function

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

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [f, nc, nw, nt] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [f, nc, nw, nt] :  # Add or remove the list names assigned above.  
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

  names = ['ncandidates_status','ncandidates_mean']  
  titles = ['Track candidates status','Number of track candidates'] # graph titles
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

  names = ['nwirebasedtracks_status','nwirebasedtracks_mean']  
  titles = ['Wire-based tracks status','Number of wire-based tracks'] # graph titles
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

  names = ['ntimebasedtracks_status','ntimebasedtracks_mean']  
  titles = ['Time-based tracks status','Number of time-based tracks'] # graph titles
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


