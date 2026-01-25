from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'CTOF'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [ctof_t, ctof_dt]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def ctof_t(rootfile) :

  names = ['t_status','t_1','t_2', 't_3', 't_4']
  titles = ['TDC time status', 'Mean TDC time, bar 1', 'Mean TDC time, bar 2','Mean TDC time, bar 3', 'Mean TDC time, bar 4'] 
  values = default_values(names)
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  tmin = 0
  tmax = 100

  histoname = 'h2_ctof_t'   # monitoring histogram to check
  dirname = '/FMWPC'      # directory containing the histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  myvals = []
  status = 1   # combined status for all 4, assume good to start with

  for bin in range(1,5):

    p = h.ProjectionY("p1",bin,bin)

    # find the bin with max content, histo looks like spike on gauss bg
    # just plot the bin value for now

    tmean = p.GetMean()

    myvals.append(float('%.1f'%(tmean)))

    if tmean < tmin  or tmean > tmax : 
        status = 0

  values = [status]

  values.extend(myvals)

  return values       # return array of values, status first


def ctof_dt(rootfile) :

  names = ['dt_status','dt_1','dt_2', 'dt_3', 'dt_4']
  titles = ['TDC-ADC time status', 'Mean TDC-ADC time, bar 1', 'Mean TDC-ADC time, bar 2','Mean TDC-ADC time, bar 3', 'Mean TDC-ADC time, bar 4']   # These will be the graph titles
  values = default_values(names)
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  tmin = 0
  tmax = 100

  histoname = 'h2_ctof_t_adc_tdc'   # monitoring histogram to check
  dirname = '/FMWPC'      # directory containing the histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  myvals = []
  status = 1   # combined status for all 4, assume good to start with

  for bin in range(1,5):

    p = h.ProjectionY("p1",bin,bin)

    # find the bin with max content, histo looks like spike on gauss bg
    # just plot the bin value for now

    tmean = p.GetMean()

    print(tmean)

    myvals.append(float('%.1f'%(tmean)))

    if tmean < tmin  or tmean > tmax : 
        status = 0

  values = [status]

  values.extend(myvals)
  
  return values       # return array of values, status first


