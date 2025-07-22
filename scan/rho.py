from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.


def init() : 

  pagename = 'Rho'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['rho_status']    # Graph name, rho_status 
  titles = ['rho status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False


  m = rho_mass_yield(False)
  ps = rho_ps_triggers(False)

  things = [ m, ps ]

  
  for thing in things :   # loop through the arrays returned from each function

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

  m = rho_mass_yield(rootfile) 
  ps = rho_ps_triggers(rootfile)
  
  things = [m, ps]

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in things :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in things :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 


def rho_mass_yield(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility

  mmin = 0.766
  mmax = 0.774
  ymin = 1e3
  ymax = 1e6

  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

  names = ['rho_mass_and_yield_status','rho_yield','rho_mass','rho_mass_err','rho_width', 'rho_width_err']
  titles = ['Rho status','Rho yield (counts, post kinfit)','Rho mass (GeV/c^{2})','Rho mass std dev','Rho width (GeV/c^{2})','Rho width std dev']   # Graph titles
  values = [-1, None, None, None, None, None]                                          # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'InvariantMass'                                      # monitoring histogram to check
  dirname = 'p2pi_preco_kinfit/Hist_InvariantMass_Rho_PostKinFitCut'    # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  counts = h.Integral(200,700)

  values[1] = float('%.0f'%(counts))
   
  frho = TF1("frho", "[0] / ((x*x - [1]*[1])*(x*x- [1]*[1]) + x*x*x*x*[2]*[2]/[1]/[1])", 0.6, 0.9)
  frho.SetParameter(0,10)
  frho.SetParameter(1,0.770)
  frho.SetParameter(2,0.1)
  frho.SetParLimits(2,0.05,0.7)

  fitstat = h.Fit("frho", "RQ0S")

  status = 0
  
  if int(fitstat) == 0:

    mass = fitstat.Parameter(1)
    width = fitstat.Parameter(2)
    err_mass = fitstat.GetErrors()[1]    
    err_width = fitstat.GetErrors()[2]

    #    if counts >= ymin and counts <= ymax and mass >= mmin and mass <= mmax:
    if mass >= mmin and mass <= mmax:
      status=1
      
    values[0] = status  
    values[2] = float('%.4f'%(mass))
    values[3] = float('%.4f'%(err_mass))    
    values[4] = float('%.4f'%(width))
    values[5] = float('%.4f'%(err_width))    

  return values       # return array of values, status first


def rho_ps_triggers(rootfile) : 

  # not using acceptability limits here, just set it to 1. 
  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

  names = ['rho_ps_pair_status','ps_pair_count','rho_per_kpspairs']
  titles = ['Rho per k PS pair status','PS pair count','Rho yield per 1000 PS pairs']           # Graph titles
  values = [-1, None, None]                                                        # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'PS_E'            # monitoring histogram to check
  dirname = 'PS_flux/PSC_PS'                        # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :

    histoname = 'PSPairEnergy'      # this should be present in ver 1 instead of PSC_PS
    dirname = 'highlevel'
    h = get_histo(rootfile, dirname, histoname, min_counts)

    if (not h) :
      return values

  # code to check the histogram and find the status values

  pscounts = h.Integral()

  if pscounts < 1:
    return values

  histoname = 'InvariantMass'                                      # monitoring histogram to check
  dirname = 'p2pi_preco_kinfit/Hist_InvariantMass_Rho_PostKinFitCut'    # directory containing the histogram

  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  rhocounts = h.Integral(200,700)

  rateperktriggers = 1000*rhocounts/float(pscounts)
  
  status = 1
      
  values = [status, float('%.0f'%(pscounts)), float('%.3f'%(rateperktriggers)) ] 
  
  return values       # return array of values, status first
