from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1, TFile

# Define the page name
PAGENAME = 'Pi0'

from pi0 import bcal_inv_mass, fitmasshisto

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [bcal_inv_mass, bcal_fcal_inv_mass]
  
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.

def bcal_fcal_inv_mass(rootfile, llim=110, ulim=135) :

  names = ['bcal_fcal_2g_mass_status', 'gg500_bcalfcal_mg', 'gg500_bcalfcalw_mg', 'gg700_bcalfcal_mg', 'gg700_bcalfcalw_mg', 'gg900_bcalfcal_mg', 'gg900_bcalfcalw_mg']
  titles = ['BCAL_FCAL diphoton mass status', 'BCAL_FCAL diphoton mass [cluster E > 500 MeV]', 'BCAL_FCAL diphoton width [cluster E > 500 MeV]', 'BCAL_FCAL diphoton mass [cluster E > 700 MeV]', 'BCAL_FCAL diphoton width [cluster E > 700 MeV]', 'BCAL_FCAL diphoton mass [cluster E > 900 MeV]', 'BCAL_FCAL diphoton width [cluster E > 900 MeV]']   
  values = default_values(names)
  png = ['bcal_fcal_inv_mass']
         
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  min_counts = 1000
  dirname = '/bcal_inv_mass/'          # directory containing that histogram
  

  histoname = 'bcal_fcal_diphoton_mass_500'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[1],values[2] = bcal_fcal_fitmasshisto(h,500)
  else :
    values[1],values[2] = [None,None]

    
  histoname = 'bcal_fcal_diphoton_mass_700'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[3],values[4] = bcal_fcal_fitmasshisto(h,700)
  else :
    values[3],values[4] = [None,None]

    
  histoname = 'bcal_fcal_diphoton_mass_900'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    #print('900 fit',fitmasshisto(h))
    values[5],values[6] = bcal_fcal_fitmasshisto(h,900)
  else :
    values[5],values[6] = [None,None]


  status=1
  for i in range(1,7) :
    if values[i] == None :
      status = -1

  masses = [1,3,5]    
  for i in masses :
    if values[i] != None :
      if values[i] < llim or values[i] > ulim :
        status = 0

  values[0] = status

  return values       # return array of values, status first
  


def bcal_fcal_fitmasshisto(h,e) :

  # cluster energy specific fit param initial values
  if e == 300 :
    x = 0
  else :
    x = 1

  p0_scale = [0.5, 0.2]
  p1 = [0.1, 0.135]
  p2 = [0.009, 0.01]

  p0_low_scale = [0.2, 0] 
  
  p1_low = [0.06, 0.02]
  p1_high = [0.18, 0.3]

  p2_low = [0.006, 0.001]
  p2_high = [0.03, 0.05]
            
  max = h.GetMaximum()

  fitfunc = TF1("fitfunc", "gaus(0)+pol3(3)", 0.04, 0.2)
  fitfunc.SetParameters(p0_scale[x]*max, p1[x], p2[x]) 

  fitfunc.SetParLimits(0, p0_low_scale[x]*max, 1.1*max)
  fitfunc.SetParLimits(1, p1_low[x], p1_high[x])
  fitfunc.SetParLimits(2, p2_low[x], p2_high[x])  

  fitresult = h.Fit(fitfunc,"RSQ0");
  
  if int(fitresult) == 0 :
    mean = 1000 * fitresult.Parameter(1)
    width = 1000 * fitresult.Parameter(2)    
    mean = float('%.1f'%mean)    
    width = float('%.1f'%width)    
  else :
    mean = None
    width = None

  return [mean,width]



# code to test the module standalone
#import os
#from glob import glob
#histofilelist = sorted(glob('hists/*.root'))
#
#for histofile in histofilelist:
#  rootfile = TFile(histofile)
#  bcal_fcal_inv_mass(rootfile)
