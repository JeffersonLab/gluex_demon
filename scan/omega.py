import csv

from utils import get_histo
from ROOT import gROOT, TF1

# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.


def init() : 

  pagename = 'Omega_3pi'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['omega_status']    # Graph name, rho_status 
  titles = ['omega status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  m3pi = omega_3pi_mass(False)
  m3pi_prek = omega_3pi_mass_prekinfit(False)
  mpi0g = omega_pi0g_mass(False)

  
  for thing in [ m3pi, m3pi_prek, mpi0g ] :   # loop through the arrays returned from each function

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

  m3pi = omega_3pi_mass(rootfile)
  m3pi_prek = omega_3pi_mass_prekinfit(rootfile)
  mpi0g = omega_pi0g_mass(rootfile)  

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [ m3pi, m3pi_prek, mpi0g ] :   # loop through the arrays returned from each function
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [ m3pi, m3pi_prek, mpi0g ] :   # loop through the arrays returned from each function  
    allvals.extend(thing) 

  return allvals
 


def omega_3pi_mass(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.750
  mmax = 0.800
  ymin = 2.e2
  ymax = 1.e6

  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

  names = ['3pi_mass_and_yield_status','3pi_mass','3pi_yield_per_k_ps','3pi_resolution']
  titles = ['Omega->3pi status','3pi mass (GeV/c^{2})','Omega->3pi yield per 1000 PS pairs','Omega->3pi width (sigma, GeV)']   # Graph titles
  values = [-1, None, None, None]                                          # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics.
  # Metrics can be None for fit fail or histo missing
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
    histoname = 'PSPairEnergy'      # this should be present in ver 1 instead of PSC_PS
    dirname = 'highlevel'
    h_ps = get_histo(rootfile, dirname, histoname, min_counts)

    if (not h_ps) :
      return values


  # code to check the histogram and find the status values

  counts = h.Integral(150, 400)

  maximum = h.GetBinCenter(h.GetMaximumBin())
  fitstatus = h.Fit("gaus", "SQ0", "", maximum - 0.05, maximum + 0.05)

  if int(fitstatus) == 0 :
    mass = fitstatus.Parameter(1)
    sigma = fitstatus.Parameter(2)

    return_mass = float('%.3f'%(mass))
    return_sigma = float('%.3f'%(sigma))

    status = 1
    
    if mass < mmin or mass > mmax:
      status = 0

  else :
    
    return_mass = None
    return_sigma = None
    status = -1
  
  n_ps = h_ps.Integral()

  if n_ps > 0:
    return_yield = float('%.2f'%(1000.*float(counts)/(float(n_ps))))
  else :
    return_yield = None
      
  values = [status, return_mass, return_yield, return_sigma]
  
  return values       # return array of values, status first


def omega_3pi_mass_prekinfit(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.750
  mmax = 0.800
  ymin = 1e2
  ymax = 1e6

  
  # Provide unique graph names. The first must be the status code from this function.

  names = ['omega_prekinfit_status','omega_prekinfit_resolution']
  titles = ['Omega->3pi pre kin fit status','Omega->3pi width, pre kin fit (sigma, GeV)']   # Graph titles
  values = [-1, None]                                          # Default values, keep as -1

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
  fitstatus = h.Fit("gaus", "SQ0", "", maximum - 0.05, maximum + 0.05)
  
  status = 1

  if int(fitstatus) == 0 :
    #mass = fitstatus.Parameter(1)
    sigma = fitstatus.Parameter(2)

    #return_mass = float('%.3f'%(mass))
    return_sigma = float('%.3f'%(sigma))

  else :
    
    return_mass = None
    return_sigma = None

  values = [status, return_sigma ] 
  
  return values       # return array of values, status first



def omega_pi0g_mass(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.750
  mmax = 0.800

  # Unique graph names

  names = ['pi0g_mass_and_yield_status','pi0g_mass','pi0g_yield_ps']
  titles = ['Omega->pi0gamma status','Omega->pi0gamma mass (GeV/c^{2})','Omega->pi0gamma yield per 1000 PS triggers'] # Graph titles
  values = [-1, None, None]                                          # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'InvariantMass'                                      # monitoring histogram to check
  dirname = 'ppi0gamma_preco_any_kinfit/Hist_InvariantMass_Omega_PostKinFitCut'    # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  h_ps = get_histo(rootfile, "PS_flux/PSC_PS", "PS_E", min_counts)

  if (not h) :
    return values
  
  if (not h_ps) :
    histoname = 'PSPairEnergy'      # this should be present in ver 1 instead of PSC_PS
    dirname = 'highlevel'
    h_ps = get_histo(rootfile, dirname, histoname, min_counts)

    if (not h_ps) :
      return values


  # code to check the histogram and find the status values

  n_ps = h_ps.Integral()

  
  counts = h.Integral(100, 400)     # was 150-400 for 3pi

  h.Rebin(10)

  fomega = TF1("fomega", "gaus(0)+pol0(3)", 0.65, 0.9)
  fomega.SetParameter(1,0.782)
  fomega.SetParameter(2,0.04)      # not 0.03
  fomega.SetParameter(3,h.GetBinContent(50))   # not bin 0

  fitstatus = h.Fit(fomega, "SQ0")

  if int(fitstatus != 0) :
    fitstatus = h.Fit(fomega,"ESQ0")        # second go seems to work when first fails

  status = 1
  
  if int(fitstatus) == 0 :
    omega_mass = fitstatus.Parameter(1)
    #omega_width = fitstatus.Parameter(2)

    if omega_mass < mmin or omega_mass > mmax:
      status = 0

    return_mass = float('%.3f'%(omega_mass))

  else :
    
    return_mass = None
    status = -1


  if n_ps > 0:
    return_yield = float('%.2f'%(1000.*float(counts)/(float(n_ps))))
  else :
    return_yield = None

    
  values = [status, return_mass, return_yield]
  
  return values       # return array of values, status first


