from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'Pi0'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [bcal_inv_mass, bcal_fcal_inv_mass]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def bcal_inv_mass(rootfile, llim=130, ulim=140) :

  names = ['bcal_2g_mass_status', '300_bcal_mg', '500_bcal_mg', '700_bcal_mg', '900_bcal_mg']
  titles = ['BCAL diphoton mass status', 'BCAL diphoton mass (cluster E > 300 MeV)', 'BCAL diphoton mass (cluster E > 500 MeV)', 'BCAL diphoton mass (cluster E > 700 MeV)', 'BCAL diphoton mass (cluster E > 900 MeV)']   # Graph titles
  values = [-1, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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

  names = ['bcal_fcal_2g_mass_status', '300_bcalfcal_mg', '500_bcalfcal_mg', '700_bcalfcal_mg', '900_bcalfcal_mg']
  titles = ['BCAL_FCAL diphoton mass status', 'BCAL_FCAL diphoton mass (cluster E > 300 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 500 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 700 MeV)', 'BCAL_FCAL diphoton mass (cluster E > 900 MeV)']   
  values = [-1, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  min_counts = 1000
  dirname = '/bcal_inv_mass/'          # directory containing that histogram
  
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
