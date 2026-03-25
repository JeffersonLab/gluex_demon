from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1, TFile

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

  names = ['bcal_2g_mass_status', 'gg300_bcal_mg', 'gg300_bcalw_mg','gg500_bcal_mg', 'gg500_bcalw_mg','gg700_bcal_mg','gg700_bcalw_mg', 'gg900_bcal_mg', 'gg900_bcalw_mg',]
  titles = ['BCAL diphoton mass status', 'BCAL diphoton mass [cluster E > 300 MeV]', 'BCAL diphoton width [cluster E > 300 MeV]', 'BCAL diphoton mass [cluster E > 500 MeV]', 'BCAL diphoton width [cluster E > 500 MeV]', 'BCAL diphoton mass [cluster E > 700 MeV]', 'BCAL diphoton width [cluster E > 700 MeV]', 'BCAL diphoton mass [cluster E > 900 MeV]',  'BCAL diphoton width [cluster E > 900 MeV]']   # Graph titles
  values = default_values(names)
  png = ['bcal_inv_mass']
  
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  dirname = '/bcal_inv_mass/'          # directory containing that histogram

  min_counts = 1000
  
  histoname = 'bcal_diphoton_mass_300'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[1],values[2] = fitmasshisto(h)
  else :
    values[1],values[2] = [None,None]


  histoname = 'bcal_diphoton_mass_500'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[3],values[4] = fitmasshisto(h)
  else :
    values[3],values[4] = [None,None]

    
  histoname = 'bcal_diphoton_mass_700'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[5],values[6] = fitmasshisto(h)
  else :
    values[5],values[6] = [None,None]

    
  histoname = 'bcal_diphoton_mass_900'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[7],values[8] = fitmasshisto(h)
  else :
    values[7],values[8] = [None,None]
    

  status=1
  for i in range(1,9) :
    if values[i] == None :
      status = -1


  masses = [1,3,5,7]    
  for i in masses :
    if values[i] != None :
      if values[i] < llim or values[i] > ulim :
        status = 0

  values[0] = status

  return values       # return array of values, status first



def bcal_fcal_inv_mass(rootfile, llim=110, ulim=135) :

  names = ['bcal_fcal_2g_mass_status', 'gg300_bcalfcal_mg', 'gg300_bcalfcalw_mg', 'gg500_bcalfcal_mg', 'gg500_bcalfcalw_mg', 'gg700_bcalfcal_mg', 'gg700_bcalfcalw_mg', 'gg900_bcalfcal_mg', 'gg900_bcalfcalw_mg']
  titles = ['BCAL_FCAL diphoton mass status', 'BCAL_FCAL diphoton mass [cluster E > 300 MeV]', 'BCAL_FCAL diphoton width [cluster E > 300 MeV]', 'BCAL_FCAL diphoton mass [cluster E > 500 MeV]', 'BCAL_FCAL diphoton width [cluster E > 500 MeV]', 'BCAL_FCAL diphoton mass [cluster E > 700 MeV]', 'BCAL_FCAL diphoton width [cluster E > 700 MeV]', 'BCAL_FCAL diphoton mass [cluster E > 900 MeV]', 'BCAL_FCAL diphoton width [cluster E > 900 MeV]']   
  values = default_values(names)
  png = ['bcal_fcal_inv_mass']
         
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  min_counts = 1000
  dirname = '/bcal_inv_mass/'          # directory containing that histogram
  
  histoname = 'bcal_fcal_diphoton_mass_300'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[1],values[2] = bcal_fcal_fitmasshisto(h,300)
  else :
    values[1],values[2] = [None,None]


  histoname = 'bcal_fcal_diphoton_mass_500'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[3],values[4] = bcal_fcal_fitmasshisto(h,500)
  else :
    values[3],values[4] = [None,None]

    
  histoname = 'bcal_fcal_diphoton_mass_700'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    values[5],values[6] = bcal_fcal_fitmasshisto(h,700)
  else :
    values[5],values[6] = [None,None]

    
  histoname = 'bcal_fcal_diphoton_mass_900'      # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    #print('900 fit',fitmasshisto(h))
    values[7],values[8] = bcal_fcal_fitmasshisto(h,900)
  else :
    values[7],values[8] = [None,None]


  status=1
  for i in range(1,9) :
    if values[i] == None :
      status = -1

  masses = [1,3,5,7]    
  for i in masses :
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
    width = 1000 * fitresult.Parameter(2)    
    mean = float('%.1f'%mean)    
    width = float('%.1f'%width)    
  else :
    mean = None
    width = None

  return [mean,width]



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

  fitfunc.SetParLimits(0, p0_low_scale[x]*max, 2.1*max)
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
