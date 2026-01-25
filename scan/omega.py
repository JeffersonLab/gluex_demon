from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'Omega'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [omega_3pi_mass, omega_3pi_mass_prekinfit, omega_pi0g_mass]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def omega_3pi_mass(rootfile) : 

  names = ['3pi_mass_and_yield_status','3pi_mass','3pi_yield_per_k_ps','3pi_resolution']
  titles = ['Omega->3pi status','3pi mass (GeV/c^{2})','Omega->3pi yield per 1000 PS pairs','Omega->3pi width (sigma, GeV)']   # Graph titles
  values = [-1, None, None, None]                                          # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  mmin = 0.750
  mmax = 0.800
  ymin = 2.e2
  ymax = 1.e6

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

  names = ['3pi_prekinfit_status','3pi_prekinfit_resolution']
  titles = ['Omega->3pi pre kin fit status','Omega->3pi width, pre kin fit (sigma, GeV)']   # Graph titles
  values = [-1, None]                                          # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  mmin = 0.750
  mmax = 0.800
  ymin = 1e2
  ymax = 1e6
  
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

  names = ['pi0g_mass_and_yield_status','pi0g_mass','pi0g_yield_ps']
  titles = ['Omega->pi0gamma status','Omega->pi0gamma mass (GeV/c^{2})','Omega->pi0gamma yield per 1000 PS triggers'] # Graph titles
  values = [-1, None, None]                                          # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  mmin = 0.750
  mmax = 0.800
  
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


