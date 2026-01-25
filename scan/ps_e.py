from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'PS_E'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [ps_e]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def ps_e(rootfile) :

  names = ['ps_e_status','ps_e_peak','ps_e_q1','ps_e_q2','ps_e_q3']   
  titles = ['PS pair E status','PS pair Epeak(GeV)','E quartile 1 (GeV)','E quartile 2 (GeV)','E quartile 3 (GeV)'] 
  values = default_values(names)

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'PS_E'   # monitoring histogram to check
  dirname = '/PS_flux/PSC_PS'      # directory containing the histogram

  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  
  from array import array

  probsum = array('d',[0.25, 0.5, 0.75])

  q = array('d',[0,0,0])

  y=h.GetQuantiles(3,q,probsum)

  

  max = h.GetBinCenter(h.GetMaximumBin())

  status=1

  values = [status, float('%.3f'%(max)), float('%.2f'%(q[0])), float('%.2f'%(q[1])), float('%.2f'%(q[2])) ]
  
  return values       # return array of values, status first
