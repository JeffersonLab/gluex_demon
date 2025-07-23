from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1,TH1I

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.


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

  
  # Provide unique graph names. The first must be the status code from this function.

  names = ['photons_psigma_pse_status', 'diamond_PSe_mg', 'diamond_PSe_mg_err', 'amo_PSe_mg', 'amo_PSe_mg_err', 'rho_psigma',  'rho_psigma_err', 'rho_psigma_0', 'rho_psigma_0_err', 'rho_psigma_90', 'rho_psigma_90_err', 'rho_psigma_135', 'rho_psigma_135_err', 'rho_psigma_45', 'rho_psigma_45_err', 'rho_phi0_diamond', 'rho_phi0_diamond_err', 'rho_phi0_amo', 'rho_phi0_amo_err' ]
  titles = ['PS E and Rho P#Sigma status', 'Photon beam energy from PS pair E (GeV)', 'PS E err (diamond)', 'Photon beam energy (amo peak) from PS pair E (GeV)', 'PS E err (amo)', 'Abs(P#Sigma) from #rho(770) production', 'Abs(P#Sigma)_err', 'P#Sigma (0)', 'P#Sigma(0)err', 'P#Sigma (90)', 'P#Sigma(90)err', 'P#Sigma (135)', 'P#Sigma(135)err', 'P#Sigma (45)', 'P#Sigma(45)err','#phi_{0} diamond', '#phi_{0} diamond err', '#phi_{0} amo', '#phi_{0} amo err' ]   # Graph titles
  values = [-1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]                      # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # Metrics can be None if unknown (no histo or bad fit)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'PiPlusPsi_t'                       # monitoring histogram to check
  dirname = '/p2pi_preco/Custom_p2pi_hists/'      # directory containing the histogram

  min_counts = 100
  hpsit = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'PS_E'   # monitoring histogram to check
  dirname = '/PS_flux/PSC_PS'      # directory containing the histogram

  min_counts = 20000
  hps = get_histo(rootfile, dirname, histoname, min_counts)

  if (not hps) :

    histoname = 'PSPairEnergy'      # this should be present in ver 1 instead of PSC_PS
    dirname = 'highlevel'
    hps = get_histo(rootfile, dirname, histoname, min_counts)

  
  if (not (hpsit and hps)) :
    return values


  amo = test_for_amo(hps)

  status = 1

  if amo :     # for amo, just take fitted peak,  # for diamond, find steepest part of edge

    psmaxbin = hps.GetMaximumBin()
    psmaxe = hps.GetBinCenter(psmaxbin)
    
    g = TF1('g','gaus',psmaxe-0.5, psmaxe+0.5) 

    fitstat = hps.Fit('g','RQ0')
  
    if int(fitstat) == 0 :
      epeak = g.GetParameter(1)
      errors = g.GetParErrors()    
      epeakerr = errors[1]

      values[3] = float('%.4f'%(epeak))
      values[4] = float('%.4f'%(epeakerr))
      
    else :
      status = -1
    

  else : 

    values[1], values[2] = find_edge(hps)
    
    if values[1] == None :
      status = -1




  # --- p2pi hists psi histo ---

  hp = hpsit.ProjectionY()

  hp.Rebin(4)
  #  #psi_{#pi^{+}}");

  f = TF1('f','[0]*(1.0 + [1]*cos(2*(x + [2])/180.*3.14159))',-180.,180.)
  fitstat = hp.Fit('f','Q0')

  if int(fitstat) != 0 :
    values[0] = -1
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

  values[0] = status
  index = 5

  for x in [PSigma, PSigmaErr, PSigma0, PSigma0Err, PSigma90, PSigma90Err, PSigma135, PSigma135Err, PSigma45, PSigma45Err, Phi0D, Phi0ErrD, Phi0Amo, Phi0ErrAmo] :
    if x == None :
      values[index] = x
    else : 
      values[index] = float('%.3f'%(x))
    index = index + 1

      
  return values       # return array of values, status first




def test_for_amo(hps) :
  # find out if this has a sharp peak (diamond) or broad peak (amo)
  # diamond coh peak is about 1 GeV wide
  
  # See if counts exceed half max at 1 GeV below maximum, 0.5 GeV above maximum, yes = amo.
  
  psmaxbin = hps.GetMaximumBin()
  psmaxe = hps.GetBinCenter(psmaxbin)

  halfmaxcounts = 0.5*hps.GetMaximum()
  
  counts_before = hps.GetBinContent(hps.FindBin(psmaxe - 1.0))
  counts_after = hps.GetBinContent(hps.FindBin(psmaxe + 0.5))   

  amo = False

  if counts_before > halfmaxcounts and counts_after > halfmaxcounts :
    amo = True

  return amo


def find_edge(h):
  

  # rebin the histo to find out where the coherent edge is
  
  rebinfactor = 5
  
  h2 = h.Clone("h2")

  h2.Rebin(rebinfactor)

  h2maxbin = h2.GetMaximumBin()

  h2_edge_end = 0
  
  for i in range(h2maxbin, h2maxbin + int(3*15/float(rebinfactor))) :     # edge width usually about 15 bins before rebinning
    if h2.GetBinContent(i+1) > h2.GetBinContent(i) :
      h2_edge_end = i-1
      break

  if h2_edge_end == 0 :
    return [None, None]


  edge_width = rebinfactor * (h2_edge_end - h2maxbin)

  edge_start = rebinfactor * h2maxbin
  edge_end = rebinfactor * h2_edge_end


  # find the derivative of the original histo for the edge region, fit to find the max    
  
  hdiff = TH1I('hdiff','hdiff',  edge_width, h.GetBinCenter(edge_start), h.GetBinCenter(edge_end))

  
  for i in range(1, edge_width) :
    hdiff.SetBinContent(i, h.GetBinContent(edge_start-1+i) - h.GetBinContent(edge_start+i))

  fitstat = hdiff.Fit("gaus","WSQ0")

  # The histo is shifted down by 0.5 bins, it contains diff between previous bin and present bin

  #hdiff.Draw()
  #input()
                      
  if int(fitstat) == 0:
    edge = 0.5*h.GetBinWidth(1) + fitstat.Parameter(1)
    edge_err = fitstat.GetErrors()[1]

    return_edge = float('%.4f'%(edge))
    return_err = float('%.4f'%(edge_err))    
    
  else :
    return_edge = None
    return_err = None

  
  return [return_edge, return_err]


#  Quantiles code  
#  from array import array
#  probsum = array('d',[0.25, 0.5, 0.75])
#  q = array('d',[0,0,0])
#  y=h.GetQuantiles(3,q,probsum)




