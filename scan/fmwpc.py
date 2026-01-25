from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'FMWPC'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [fmwpc_e]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def fmwpc_e(rootfile) :

  names = ['fmwpc_e_status','fmwpc_e_1','fmwpc_e_2', 'fmwpc_e_3', 'fmwpc_e_4', 'fmwpc_e_5', 'fmwpc_e_6']  
  titles = ['E status','E chamber 1 (GeV)','E chamber 2 (GeV)', 'E chamber 3 (GeV)', 'E chamber 4 (GeV)', 'E chamber 5 (GeV)', 'E chamber 6 (GeV)']         # These will be the graph titles
  values = default_values(names)
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  emin = 500
  emax = 600
  
  histoname = 'h2_fmwpc_pi_chamber'   # monitoring histogram to check
  dirname = '/FMWPC'      # directory containing the histogram

  min_counts = 100

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  myvals = []
  status = 1   # combined status for all 4, assume good to start with

  for bin in range(1,7):

    p = h.ProjectionY("p1",bin,bin)

    # find the bin with max content, histo looks like spike on gauss bg
    # just plot the bin value for now

    maxbin = p.GetMaximumBin()
    epeak = p.GetXaxis().GetBinCenter(maxbin)

    myvals.append(float('%.1f'%(epeak)))

    if epeak < emin  or epeak > emax : 
        status = 0

  values = [status]

  values.extend(myvals)
  
  return values       # return array of values, status first
