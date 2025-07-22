import csv
from utils import get_histo     # demon's helper functions

from ROOT import gROOT

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#
# Copy and rename new_module.py and test_new_module.py, and change all instances of new_module to your module's name  
#
# Adapt the example custom functions (new_module_occupancy and new_module_e) to retrieve the metrics needed from their histogram.
# Add more custom functions, or remove one if it is not required.
#
# Add the custom functions to the list of functions in 'init' and 'check'.
#
# To show a pair of quantities together in a TGraphErr, give them names like x and x_err, eg rho_mass and rho_mass_err
# At present, test_new_module makes these into separate graphs, but scan makes them into TGraphErr


def init() : 

  pagename = 'New_Module'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['new_module_status']    # Graph name, new_module_status 
  titles = ['new_module status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  occ = new_module_occupancy(False)  # return names, titles, values
  e = new_module_e(False)


  for thing in [ occ, e ] :   # loop through the arrays returned from each function

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

  occ = new_module_occupancy(rootfile)

  e = new_module_e(rootfile)

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [occ, e] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [occ, e] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 


def new_module_occupancy(rootfile, occmin=0.99) :

  # Example custom function to check the occupancy histogram

  print('in new_module_occupancy()...')

  # Provide unique graph names, starting with 'new_module_'. The first must be the status code from this function. Do not call it new_module_status - call it something else ending with _status, eg new_module_functionname_status.

  names = ['occ_status','occ_percent']            
  titles = ['Occupancy status','Occupancy (%)']   # Graph titles
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'an30_100ns'      # monitoring histogram to check
  dirname = '/CDC_amp'          # directory containing that histogram

  occmax = 0.98                 # acceptability limit
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # this is a copy of the CDC's occupancy code

  from array import array
  Nstraws = array("I", [42, 42, 54, 54, 66, 66, 80, 80, 93, 93, 106, 106, 123, 123, 135, 135, 146, 146, 158, 158, 170, 170, 182, 182, 197, 197, 209, 209])

  Ndead = 0
  Nfirst = 0

  #deadstraws = []

  for ring in range(0,28) :
    
    ahisto = h.ProjectionY("ring", Nfirst+2, Nfirst+Nstraws[ring]+1 );  #straw 1 is in bin 2

    hits_ring = ahisto.GetEntries()
   
    floatnstraws = float(Nstraws[ring])

    mean_hits_per_straw = int(hits_ring/floatnstraws)

    for straw in range(Nfirst+1, Nfirst+Nstraws[ring]+1) :

      ahisto = h.ProjectionY("straw_"+str(straw), straw+1, straw+1 )  #straw 1 is in bin 2

      hits_straw = ahisto.GetEntries()

      eff = 1

      if (hits_straw < 0.25 * mean_hits_per_straw) :
        eff = 0

      if eff == 0:
        Ndead = Ndead + 1


    Nfirst = Nfirst + Nstraws[ring]



  occupancy = 100*(3522-Ndead)/3522.0

  status=1

  if occupancy < occmin:
    status=0

  values = [status, float('%.3f'%(occupancy)) ]

  return values       # return array of values, status first
  


def new_module_e(rootfile) :

  # Example custom function to check another histogram

  print('in new_module_e()...')

# Provide unique graph names. The first must be the status code from this function. Do not call it new_module_status - call it something else ending with _status, eg new_module_functionname_status.

  names = ['e_status','e_mean','e_width']  
  titles = ['E status','E mean (GeV)','E width (GeV)']      # These will be the graph titles
  values = [-1, None, None]                                 # Default values, -1 for status, None for others

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics.
  # Metrics can be None if unknown (histo is missing or fit fails).
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/fit problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'dedx_p_pos'   # monitoring histogram to check
  dirname = '/CDC_dedx'      # directory containing the histogram

  emin=1.8    # acceptability limit
  emax=2.3    # acceptability limit
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  pbin = h.GetXaxis().FindBin(3.0)
  p = h.ProjectionY("p1",1,pbin)

  if p.GetEntries() < 50 :   # not enough entries
    return values 

  e_mean = p.GetMean()
  e_width = p.GetRMS()

  status = 1
  if e_mean < emin or e_mean > emax:
      status=0


  values = [status, float('%.5f'%(e_mean)), float('%.5f'%(e_width)) ]
  
  return values       # return array of values, status first


