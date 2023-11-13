import csv

from ROOT import gROOT,TF1

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#
#
# Change all instances of new_module to your module's name 
#
# Adapt the example custom functions (new_module_occupancy and new_module_e) to retrieve the metrics needed from their histogram.
# Add more custom functions, or remove one if it is not required.
#
# Add the custom functions to the list of functions in 'init' and 'check'.
#
# In 'check', provide the set of limits for each metric, and adapt the code to use these. 
#



def init() : 

  # These arrays are the headers for the overall status summary for this module
  # Do not add any more array elements here

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

  return [names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # Acceptable value limits, defined here for accessibility

  occmin = 99.8

  emin = 3.1
  emax = 3.3

  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  occ = new_module_occupancy(rootfile, occmin)

  e = new_module_e(rootfile, emin, emax)

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

  # Provide unique graph names, starting with 'new_module_'. The first must be the status code from this function.

  names = ['new_module_occ_status','new_module_occ_percent']            
  titles = ['New_Module occupancy status','New_Module occupancy (%)']   # Graph titles
  values = [-1, -1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'an30_100ns'      # monitoring histogram to check
  dirname = '/CDC_amp'          # directory containing that histogram


  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
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




  new_module_occupancy = 100*(3522-Ndead)/3522.0

  status=1

  if new_module_occupancy < occmin:
    status=0

  values = [status, float('%.3f'%(new_module_occupancy)) ]

  return values       # return array of values, status first
  


def new_module_e(rootfile, emin=1.8, emax=2.3) :

  # Example custom function to check the occupancy histogram

  # Provide unique graph names, starting with 'new_module_'. The first must be the status code from this function.

  names = ['new_module_e','new_module_e_mean','new_module_e_width']  
  titles = ['E status','E mean (GeV)','E width (GeV)']      # These will be the graph titles
  values = [-1,-1,-1]                                       # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'dedx_p_pos'   # monitoring histogram to check
  dirname = '/CDC_dedx'      # directory containing the histogram


  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values


  # code to check the histogram and find the status values

  pbin = h.GetXaxis().FindBin(3.0)
  p = h.ProjectionY("p1",1,pbin)

  if p.GetEntries() < 50 :   # not enough entries
    return values 

  new_module_e_mean = p.GetMean()
  new_module_e_width = p.GetRMS()

  status = 1
  if new_module_e_mean < emin or new_module_e_mean > emax:
      status=0


  values = [status, float('%.5f'%(new_module_e_mean)), float('%.5f'%(new_module_e_width)) ]
  
  return values       # return array of values, status first

