from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'SC'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [sc_dedx]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def sc_dedx(rootfile) :

  titles = ['SC dE/dx status', 'SC dE/dx q+ MPV at 1.5 GeV/c (keV/cm)','SC dE/dx q+ width at 1.5 GeV/c (keV/cm)', 'SC dE/dx q- MPV at 1.5 GeV/c (keV/cm)','SC dE/dx q- width at 1.5 GeV/c (keV/cm)']
  names = ['dedx_status', 'qp_dedx_mpv', 'qp_dedx_sig', 'qm_dedx_mpv','qm_dedx_sig']
  values = [-1, None, None, None, None ]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorPID/SC'
  min_counts = 1.1e5
  fitoptions = "0QWERS"
  
  histoname = 'dEdXVsP_q+'

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if h:
    qp = check_dedx(h,fitoptions)
  else :
    qp = [ -1, None, None]
    
    
  histoname = 'dEdXVsP_q-'

  h = get_histo(rootfile, dirname, histoname, min_counts)
  
  if h:
    qm = check_dedx(h,fitoptions)
  else :
    qm = [ -1, None, None]

  status = min(qp.pop(0),qm.pop(0))

  values = [status]
  values.extend(qp)
  values.extend(qm)
  
  return values




def check_dedx(h, fitoptions) :

  values = [ -1, None, None ]   # defaults in case fit fails

  p = h.ProjectionY("p1",38,38)
  p.GetXaxis().SetRangeUser(0,5)

  lan = TF1('lan','landau',0.5,10)

  fitstat = p.Fit('lan',fitoptions)

  if int(fitstat) == 0:
      mpv = lan.GetParameter(1)
      sigma = lan.GetParameter(2)
      status = 1
      
      values = [ status, float('%.5f'%(mpv)), float('%.5f'%(sigma)) ]
    
  return values
