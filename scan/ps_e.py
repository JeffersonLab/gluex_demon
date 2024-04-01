import csv

from ROOT import gROOT

# ps pair e


def init() : 

  pagename = 'PS_E'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['ps_pair_status']    # Graph name, ps_pair_status 
  titles = ['ps_pair status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  e = ps_e(False)

  for thing in [ e ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # Acceptable value limits, defined here for accessibility


  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  e = ps_e(rootfile)

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [e] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [e] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 



def ps_e(rootfile) :

  # Example custom function to check another histogram

  #print('in ps_e()...')

  # Provide unique graph names, starting with 'ps_pair_'. The first must be the status code from this function.

  names = ['ps_e_status','ps_e_peak','ps_e_q1','ps_e_q2','ps_e_q3']   
  titles = ['PS pair E status','PS pair Epeak(GeV)','E quartile 1 (GeV)','E quartile 2 (GeV)','E quartile 3 (GeV)']      # These will be the graph titles
  values = [-1,-1,-1,-1,-1]                    # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'PS_E'   # monitoring histogram to check
  dirname = '/PS_flux/PSC_PS'      # directory containing the histogram

  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  
  from array import array

  probsum = array('d',[0.25, 0.5, 0.75])

  q = array('d',[0,0,0])

  y=h.GetQuantiles(3,q,probsum)

  

  max = h.GetBinCenter(h.GetMaximumBin())


  status=1

  values = [status, float('%.3f'%(max)), float('%.2f'%(q[0])), float('%.2f'%(q[1])), float('%.2f'%(q[2])) ]
  
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

  if h.GetEntries() < min_counts :
    return False

  return h
