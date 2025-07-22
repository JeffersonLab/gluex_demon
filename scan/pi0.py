from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#
# To show a pair of quantities together in a TGraphErr, give them names like x and x_err, eg rho_mass and rho_mass_err
# At present, test_pi0 makes these into separate graphs, but scan makes them into TGraphErr


def init() : 

  pagename = 'Pi0'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['pi0_status']    # Graph name, new_module_status 
  titles = ['pi0 status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  b = bcal_inv_mass(False) # return names, titles, values
  f = bcal_fcal_inv_mass(False) # return names, titles, values  

  for thing in [ b, f ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # Values can be None if the fit failed or histo was not present

  # List of custom functions, called with argument rootfile
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  b = bcal_inv_mass(rootfile)
  f = bcal_fcal_inv_mass(rootfile)   

  # This finds the overall status, setting it to the min value of each histogram status

  statuslist = []
  for thing in [ b, f ] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [ b, f ] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 


def bcal_inv_mass(rootfile, llim=130, ulim=140) :

  # Provide unique graph names. The first must be the status code from this function. 
  
  names = ['bcal_2g_mass_status', '300_bcal_mg', '500_bcal_mg', '700_bcal_mg', '900_bcal_mg']
  titles = ['BCAL diphoton mass status', 'BCAL diphoton mass (cluster E > 300 MeV)', 'BCAL diphoton mass (cluster E > 500 MeV)', 'BCAL diphoton mass (cluster E > 700 MeV)', 'BCAL diphoton mass (cluster E > 900 MeV)']   # Graph titles
  values = [-1, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics.
  # Unknown metrics (no histo/no fit) are set to None.
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.


  dirname = '/bcal_inv_mass/'          # directory containing that histogram

  min_counts = 1000
  
  histoname = 'bcal_diphoton_mass_300'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[1] = fitmasshisto(h)
  else :
    values[1] = None


  histoname = 'bcal_diphoton_mass_500'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[2] = fitmasshisto(h)
  else :
    values[2] = None

    
  histoname = 'bcal_diphoton_mass_700'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[3] = fitmasshisto(h)
  else :
    values[3] = None

    
  histoname = 'bcal_diphoton_mass_900'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[4] = fitmasshisto(h)
  else :
    values[4] = None
    

  status=1
  for i in range(1,5) :
    if values[i] == None :
      status = -1
      
  for i in range(1,5) :
    if values[i] != None :
      if values[i] < llim or values[i] > ulim :
        status = 0

  values[0] = status

  return values       # return array of values, status first



def bcal_fcal_inv_mass(rootfile, llim=110, ulim=135) :

  #print('in bcal_fcal_inv_mass()...')

  # Provide unique graph names, starting with 'pi0_'. The first must be the status code from this function. Do not call it pi0_status - call it something else ending with _status, eg pi0_functionname_status.

  names = ['bcal_fcal_2g_mass_status', '300_bcalfcal_mg', '500_bcalfcal_mg', '700_bcalfcal_mg', '900_bcalfcal_mg']
  titles = ['BCAL_FCAL diphoton mass status', 'BCAL_FCAL diphoton mass (cluster E > 300 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 500 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 700 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 900 MeV)']   # Graph titles
  values = [-1, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics.
  # Metrics can be None if unknown.
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.


  dirname = '/bcal_inv_mass/'          # directory containing that histogram

  min_counts = 1000
  
  histoname = 'bcal_fcal_diphoton_mass_300'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[1] = bcal_fcal_fitmasshisto(h)
  else :
    values[1] = None


  histoname = 'bcal_fcal_diphoton_mass_500'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[2] = bcal_fcal_fitmasshisto(h)
  else :
    values[2] = None

    
  histoname = 'bcal_fcal_diphoton_mass_700'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[3] = bcal_fcal_fitmasshisto(h)
  else :
    values[3] = None

    
  histoname = 'bcal_fcal_diphoton_mass_900'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)



  if h:
    #print('900 fit',fitmasshisto(h))
    values[4] = bcal_fcal_fitmasshisto(h)
  else :
    values[4] = None
    

  status=1
  for i in range(1,5) :
    if values[i] == None :
      status = -1
      
  for i in range(1,5) :
    if values[i] != None :
      if values[i] < llim or values[i] > ulim :
        status = 0

  values[0] = status

  return values       # return array of values, status first
  


def fitmasshisto(h) :

  max = h.GetMaximum()

  fitfunc = TF1("fitfunc", "gaus(0)+pol3(3)", 0.07, 0.2)
  fitfunc.SetParameters(0.5*max, 0.135, 0.01)

  fitfunc.SetParLimits(0, 0.2*max, 1.1*max)
  fitfunc.SetParLimits(1,0.06,0.18);
  fitfunc.SetParLimits(2,0.006,0.02);

  fitresult = h.Fit(fitfunc,"RQS0");
  
  if int(fitresult) == 0 :
    mean = 1000 * fitresult.Parameter(1)
    mean = float('%.1f'%mean)    
    
  else :
    mean = None

  return mean


def bcal_fcal_fitmasshisto(h) :

  max = h.GetMaximum()

  fitfunc = TF1("fitfunc", "gaus(0)+pol3(3)", 0.04, 0.2)
  fitfunc.SetParameters(0.2*max, 0.135, 0.01)

  fitfunc.SetParLimits(0, 0, 2.1*max)
  fitfunc.SetParLimits(1,0.02,0.3);
  fitfunc.SetParLimits(2,0.001,0.05);

  fitresult = h.Fit(fitfunc,"RQS0");
  
  if int(fitresult) == 0 :
    mean = 1000 * fitresult.Parameter(1)
    mean = float('%.1f'%mean)    
    
  else :
    mean = None

  return mean
