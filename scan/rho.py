from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'Rho'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [rho_mass_yield, rho_ps_triggers]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def rho_mass_yield(rootfile) : 

  names = ['rho_mass_and_yield_status','rho_yield','rho_mass','rho_mass_err','rho_width', 'rho_width_err']
  titles = ['Rho status','Rho yield (counts, post kinfit)','Rho mass (GeV/c^{2})','Rho mass std dev','Rho width (GeV/c^{2})','Rho width std dev']   # Graph titles
  values = [-1, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  mmin = 0.766
  mmax = 0.774
  ymin = 1e3
  ymax = 1e6

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

  names = ['rho_ps_pair_status','ps_pair_count','rho_per_kpspairs']
  titles = ['Rho per k PS pair status','PS pair count','Rho yield per 1000 PS pairs']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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
