from utils import get_histo     # demon's helper functions
from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'SC'
  names = ['sc_status']    # This will be the overall status graph name for this module, must start with modulename_
  titles = ['SC status']   # This will be the status graph title
  values = [-1]                 # Default status, keep it at -1


  # list of functions to check, here they should be called with one argument: False, to return names, titles & defaults

  dedx = sc_dedx(False)  # return names, titles, values
  
  things = [ dedx ]

  for thing in things :   # loop through the arrays returned from each function    

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # If the histogram is missing or the hit fails, status is set to -1 and data are set to None

  # list of functions to check, here they should be called with rootfile, followed by the status limits, then the fit and momentum limits, then the error limit, and return an array of values

  dedx = sc_dedx(rootfile)  
  
  things = [ dedx ]

  # set the overall status to the min value of each histogram status

  statuslist = []
  
  for thing in things : # loop through the arrays returned from each function
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]
  for thing in things :
    allvals.extend(thing) 
    
  return allvals


#############
  
def sc_dedx(rootfile) :

  #print("in sc_dedx() ... ")

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
