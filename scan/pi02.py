from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1, TFile

# Define the page name
PAGENAME = 'Pi0'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [pi0_mass]
  
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def pi0_mass(rootfile, llim=130, ulim=140) :

  names = ['pi0_status', 'ecal', 'ecal_err']
  names.extend(['fcal', 'fcal_err'])
  names.extend(['bcal', 'bcal_err'])
  names.extend(['bcal_ecal', 'bcal_ecal_err'])
  names.extend(['bcal_fcal', 'bcal_fcal_err'])  
  
  titles = ['diphoton mass status', 'ECAL diphoton mass (MeV)', 'ECAL diphoton width']
  titles.extend(['FCAL diphoton mass (MeV)', 'FCAL diphoton width'])
  titles.extend(['BCAL diphoton mass (MeV)', 'BCAL diphoton width'])
  titles.extend(['BCAL+ECAL diphoton mass (MeV)', 'BCAL+ECAL diphoton width'])
  titles.extend(['BCAL+FCAL diphoton mass (MeV)', 'BCAL+FCAL diphoton width'])      

  values = default_values(names)
  png = ['fit_pi0', 'fit_pi0', 'fit_pi0', 'fit_pi0', 'fit_pi0', 'fit_pi0', '', '', '', '', '', '']
  
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  dirname = '/FCAL2_invmass/'          # directory containing that histogram

  min_counts = 1000

  histonames = ['h_2gamma_ECAL_ECAL', 'h_2gamma_FCAL_FCAL', 'h_2gamma_BCAL_BCAL', 'h_2gamma_BCAL_ECAL', 'h_2gamma_ECAL_FCAL']

  status=1
  
  for i in range(0, len(histonames)):
    
    histoname = histonames[i]
    h = get_histo(rootfile, dirname, histoname, min_counts)
    j = 2*i  + 1
    
    if h:
      values[j],values[j+1] = fitmasshisto(h)
      if values[j] == None:
        if status == 1:
          status = -1
      elif values[j] < llim or values[j] > ulim :
        status = 0
      
    else :
      values[j],values[j+1] = [None,None]
      if status == 1:
        status = -1


  values[0] = status

  return values       # return array of values, status first


def fitmasshisto(h) :

  h.GetXaxis().SetRangeUser(0.08, 0.18)
  max = h.GetMaximum()

  fitfunc = TF1("fitfunc", "gaus(0)+expo(3)", 0.09, 0.17)

  histoname = h.GetName()
  
  if "ECAL_ECAL" in histoname:
    fitfunc.SetParameters(max, 0.125, 0.004, 2, -10, 0)
    
  elif "FCAL_FCAL" in histoname:
    fitfunc.SetParameters(max, 0.135, 0.008, 2, -10, 0)

  elif "ECAL_FCAL" in histoname:
    fitfunc.SetParameters(max, 0.135, 0.008, 2, -10, 0)
    
  else: #BCAL combos
    fitfunc.SetParameters(max, 0.135, 0.01, 2, -10, 0)


  fitresult = h.Fit(fitfunc,"SQ0");
  
  if int(fitresult) == 0 :
    mean = 1000 * fitresult.Parameter(1)
    width = 1000 * fitresult.Parameter(2)    
    mean = float('%.1f'%mean)    
    width = float('%.1f'%width)
#    widthovermean = float('%.1f'%100*width/mean)
  else :
    mean = None
    width = None

  return [mean,width]



'''
# code to test the module standalone
import os
from glob import glob
histofilelist = sorted(glob('hists/*.root'))
#
for histofile in histofilelist:
  rootfile = TFile(histofile)
  values = pi0_mass(rootfile)
  print(values)
'''
