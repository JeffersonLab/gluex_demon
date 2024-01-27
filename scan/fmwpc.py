import csv

from ROOT import gROOT

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

  pagename = 'FMWPC'          # Title for the page of graphs

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['fmwpc_status']    # Graph name, fmwpc_status 
  titles = ['FMWPC status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  e = fmwpc_e(False)


  for thing in [ e ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # Acceptable value limits, defined here for accessibility


  emin = 500
  emax = 600

  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  e = fmwpc_e(rootfile, emin, emax)

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [ e ] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [ e ] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 



def fmwpc_e(rootfile, emin=500, emax=600) :

  # Example custom function to check the occupancy histogram

  # Provide unique graph names, starting with 'fmwpc_'. The first must be the status code from this function.

  names = ['fmwpc_e_status','fmwpc_e_1','fmwpc_e_2', 'fmwpc_e_3', 'fmwpc_e_4', 'fmwpc_e_5', 'fmwpc_e_6']  
  titles = ['E status','E chamber 1 (GeV)','E chamber 2 (GeV)', 'E chamber 3 (GeV)', 'E chamber 4 (GeV)', 'E chamber 5 (GeV)', 'E chamber 6 (GeV)']         # These will be the graph titles
  values = [-1,-1,-1, -1, -1, -1, -1]   # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'h2_fmwpc_pi_chamber'   # monitoring histogram to check
  dirname = '/FMWPC'      # directory containing the histogram


  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values


  # code to check the histogram and find the status values

  myvals = []
  status = 1   # combined status for all 4, assume good to start with

  for bin in range(1,7):

    p = h.ProjectionY("p1",bin,bin)

    # find the bin with max content, histo looks like spike on gauss bg
    # just plot the bin value for now

    maxbin = p.GetMaximumBin()
    epeak = p.GetXaxis().GetBinCenter(maxbin)

    myvals.append(float('%.1f'%(epeak)))

    if epeak < emin  or epeak > emax : 
        status = 0

  values = [status]

  values.extend(myvals)

  
  return values       # return array of values, status first

