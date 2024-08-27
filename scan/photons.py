import csv
from utils import get_histo     # demon's helper functions
import time
from ROOT import gROOT, TF1,TH1I

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#
#
# Change all instances of new_module to your module's name 
#
# Adapt the example custom functions (new_module_occupancy and new_module_e) to retrieve the metrics needed from their histogram.
# Add more custom functions, or remove one if it is not required.
#
# Add the custom functions to the list of functions in 'init' and 'check'.
#
# In 'check', provide the set of limits for each metric, and adapt the code to use these. 
#



def init() : 

  pagename = 'Photon_beam'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['photon_beam_status']    # Graph name, rho_status 
  titles = ['Photon beam status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False


  ps = rho_psigma_pse(False)

  things = [ ps ]

  
  for thing in things :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  ps = rho_psigma_pse(rootfile)
  
  things = [ps]

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in things :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in things :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 





def rho_psigma_pse(rootfile) : 

  # Example custom function to check another histogram

  # Acceptable value limits, defined here for accessibility
  status = 1
  # none yet
  
  # Provide unique graph names, starting with 'rho_'. The first must be the status code from this function.

  names = ['photons_psigma_pse_status', 'photons_ps_e', 'photons_ps_e_err', 'photons_rho_psigma',  'photons_rho_psigma_err', 'photons_rho_psigma_0', 'photons_rho_psigma_0_err', 'photons_rho_psigma_90', 'photons_rho_psigma_90_err', 'photons_rho_psigma_135', 'photons_rho_psigma_135_err', 'photons_rho_psigma_45', 'photons_rho_psigma_45_err', 'photons_rho_phi0_diamond', 'photons_rho_phi0_diamond_err', 'photons_rho_phi0_amo', 'photons_rho_phi0_amo_err' ]
  titles = ['PS E and Rho P#Sigma status', 'Photon beam energy (diamond edge, amo peak) from PS pair E (GeV)', 'PS E err','Abs(P#Sigma) from #rho(770) production', 'Abs(P#Sigma)_err', 'P#Sigma (0)', 'P#Sigma(0)err', 'P#Sigma (90)', 'P#Sigma(90)err', 'P#Sigma (135)', 'P#Sigma(135)err', 'P#Sigma (45)', 'P#Sigma(45)err','#phi_{0} diamond', '#phi_{0} diamond err', '#phi_{0} amo', '#phi_{0} amo err' ]   # Graph titles
  values = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]                      # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'PiPlusPsi_t'                       # monitoring histogram to check
  dirname = '/p2pi_preco/Custom_p2pi_hists/'      # directory containing the histogram

  min_counts = 100
  hpsit = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'PS_E'   # monitoring histogram to check
  dirname = '/PS_flux/PSC_PS'      # directory containing the histogram

  min_counts = 1000
  hps = get_histo(rootfile, dirname, histoname, min_counts)

  if (not (hpsit and hps)) :
    return values

  # find out if this has a sharp peak (diamond) or broad peak (amo)
  # diamond coh peak is about 1 GeV wide
  
  # See if counts exceed half max at 1 GeV either side of maximum, yes = amo.
  
  psmaxbin = hps.GetMaximumBin()
  psmaxe = hps.GetBinCenter(psmaxbin)

  halfmaxcounts = 0.5*hps.GetMaximum()
  
  counts_before = hps.GetBinContent(hps.FindBin(psmaxe-1.0))
  counts_after = hps.GetBinContent(hps.FindBin(psmaxe+1.0))   

  amo = False

  if counts_before > halfmaxcounts and counts_after > halfmaxcounts :
    amo = True

  if amo :     # for amo, just take fitted peak,  # for diamond, find steepest part of edge

    g = TF1('g','gaus',psmaxe-0.5, psmaxe+0.5) 

    fitstat = hps.Fit('g','RQ')
  
    if int(fitstat) != 0 :
      return values

    epeak = g.GetParameter(1)
    errors = g.GetParErrors()    
    epeakerr = errors[1]     

  else : 
  
    hdiff = TH1I('hdiff','hdiff',20,0,20)      # find negative values in derivative, fit to find where slope is max  

    nprev = hps.GetBinContent(psmaxbin-10)
    for i in range(1,20):
      nnext = hps.GetBinContent(psmaxbin-10 + i)
      diff = nnext - nprev
      if (diff < 0) :
        hdiff.SetBinContent(i,-1*diff)
      nprev = nnext

    # bin 1 : filled with (maxbin-9) - (maxbin-10) : maxbin - 9.5 : has bin center 0.5  

    f = TF1('f','gaus')
    fitstat=hdiff.Fit(f,'Q')

    if int(fitstat) != 0 :
      return values

    binwidth = hps.GetBinWidth(1)    
    epeak = psmaxe + (f.GetParameter(1)- 10)*binwidth
    errors = f.GetParErrors()
    epeakerr = errors[1]*binwidth

      
  values[0] = 0    # status, update later on
  values[1] = float('%.2f'%(epeak))
  values[2] = float('%.2f'%(epeakerr))


  # --- p2pi hists psi histo ---

  hp = hpsit.ProjectionY()

  hp.Rebin(4)
  #  #psi_{#pi^{+}}");

  f = TF1('f','[0]*(1.0 + [1]*cos(2*(x + [2])/180.*3.14159))',-180.,180.)
  fitstat = hp.Fit('f','Q')

  if int(fitstat) != 0 :
    return values
  
  PSigma = f.GetParameter(1)
  PSigmaErr = f.GetParError(1)
  
  Phi0 = f.GetParameter(2)
  Phi0Err = f.GetParError(2)

  if Phi0 > 360:
    Phi0 = Phi0%360.0   # deal with few extra rotations

    
  PSigma0 =None
  PSigma0Err = None
  PSigma90 = None
  PSigma90Err = None
  PSigma135 = None
  PSigma135Err = None
  PSigma45 = None
  PSigma45Err = None

  if amo : 
    Phi0Amo = Phi0
    Phi0ErrAmo = Phi0Err
    Phi0D = None
    Phi0ErrD = None

  else:

    Phi0Amo = None
    Phi0ErrAmo = None
    Phi0D = Phi0
    Phi0ErrD = Phi0Err

    
  if not amo:
    if PSigma>0 and abs(Phi0)<22 : # 0 para
      pol=0
      PSigma0 = PSigma
      PSigma0Err = PSigmaErr
    elif PSigma<0 and abs(Phi0)<22 : # 90 perp
      pol=90
      PSigma90 = PSigma
      PSigma90Err = PSigmaErr
    elif PSigma>0 and abs(Phi0)>22 : # 135 para
      pol=135
      PSigma135 = PSigma
      PSigma135Err = PSigmaErr
    elif PSigma<0 and abs(Phi0)>22 : # 45 perp
      pol=45
      PSigma45 = PSigma
      PSigma45Err = PSigmaErr

      
  PSigma = abs(PSigma)    # report abs value for overall graph to make it simpler

  values[0] = 1    # status
  index = 3

  for x in [PSigma, PSigmaErr, PSigma0, PSigma0Err, PSigma90, PSigma90Err, PSigma135, PSigma135Err, PSigma45, PSigma45Err, Phi0D, Phi0ErrD, Phi0Amo, Phi0ErrAmo] :
    if x == None :
      values[index] = x
    else : 
      values[index] = float('%.2f'%(x))
    index = index + 1

      
  return values       # return array of values, status first




#  Quantiles code  
#  from array import array
#  probsum = array('d',[0.25, 0.5, 0.75])
#  q = array('d',[0,0,0])
#  y=h.GetQuantiles(3,q,probsum)




