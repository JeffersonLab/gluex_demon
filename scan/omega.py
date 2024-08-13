import csv

from ROOT import gROOT, TF1

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

  pagename = 'Omega_3pi'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['omega_status']    # Graph name, rho_status 
  titles = ['omega status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  m = omega_mass(False)
  mp = omega_mass_prekinfit(False)

  for thing in [ m, mp ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  m_omega = omega_mass(rootfile) 
  m_omega_prekinfit = omega_mass_prekinfit(rootfile) 

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [ m_omega, m_omega_prekinfit ] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [ m_omega, m_omega_prekinfit ] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 


def omega_mass(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.750
  mmax = 0.800
  ymin = 2.e2
  ymax = 1.e6

  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

  names = ['omega_mass_and_yield_status','omega_mass','omega_yield_ps','omega_resolution']
  titles = ['Omega->3pi status','3pi mass (GeV/c^{2})','Omega->3pi yield (counts, post kinfit)','Omega->3pi resolution (sigma, GeV)']   # Graph titles
  values = [-1,-1,-1,-1]                                          # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'InvariantMass'                                      # monitoring histogram to check
  dirname = 'p3pi_preco_any_kinfit/Hist_InvariantMass_Omega_PostKinFitCut'    # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  h_ps = get_histo(rootfile, "PS_flux/PSC_PS", "PS_E", min_counts)

  if (not h) :
    return values
  if (not h_ps) :
    return values

  # code to check the histogram and find the status values

  counts = h.Integral(150, 400)
  
  maximum = h.GetBinCenter(h.GetMaximumBin())
  fr = h.Fit("gaus", "SQ", "", maximum - 0.05, maximum + 0.05)
  
  mass = fr.Parameter(1)
  sigma = fr.Parameter(2)
  
  n_ps = h_ps.Integral()
  
  status = 1
  if counts < ymin or counts > ymax:
      status=0

  if mass < mmin or mass > mmax:
      status=0

      
  values = [status, float('%.3f'%(mass)), float('%.0f'%(1000.*float(counts)/(float(n_ps)))), float('%.3f'%(sigma)) ] 
  
  return values       # return array of values, status first


def omega_mass_prekinfit(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.750
  mmax = 0.800
  ymin = 1e2
  ymax = 1e6

  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

#   names = ['omega_mass_and_yield_status','omega_mass','omega_yield_ps','omega_resolution']
#   titles = ['Omega->3pi status','3pi mass (GeV/c^{2})','Omega->3pi yield (counts, post kinfit)','Omega->3pi resolution (sigma, GeV)']   # Graph titles
#   values = [-1,-1,-1,-1]                                          # Default values, keep as -1

  names = ['omega_prekinfit_status','omega_prekinfit_resolution']
  titles = ['Omega->3pi pre kin fit status','Omega->3pi resolution, pre kin fit (sigma, GeV)']   # Graph titles
  values = [-1,-1]                                          # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'InvariantMass'                                      # monitoring histogram to check
  dirname = 'p3pi_preco_any_kinfit/Hist_InvariantMass_Omega'    # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  counts = h.Integral(150, 400)

  maximum = h.GetBinCenter(h.GetMaximumBin())
  fr = h.Fit("gaus", "SQ", "", maximum - 0.05, maximum + 0.05)
  
  mass = fr.Parameter(1)
  sigma = fr.Parameter(2)

  status = 1
  if counts < ymin or counts > ymax:
      status=0

#   if mass < mmin or mass > mmax:
#       status=0

      
  values = [status, float('%.3f'%(sigma)) ] 
  
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
