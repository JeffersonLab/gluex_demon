from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1,TH1I
import math

# Define the page name
PAGENAME = 'PhotonBeam'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [rho_psigma_pse] #, trigger_asymmetry]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def rho_psigma_pse(rootfile) : 

  names = ['photons_psigma_pse_status', 'diamond_PSe_mg', 'diamond_PSe_mg_err', 'amo_PSe_mg', 'amo_PSe_mg_err', 'rho_psigma',  'rho_psigma_err', 'rho_psigma_0', 'rho_psigma_0_err', 'rho_psigma_90', 'rho_psigma_90_err', 'rho_psigma_135', 'rho_psigma_135_err', 'rho_psigma_45', 'rho_psigma_45_err', 'rho_phi0_diamond', 'rho_phi0_diamond_err', 'rho_phi0_amo', 'rho_phi0_amo_err' ]
  titles = ['PS E and Rho P#Sigma status', 'Photon beam energy from PS pair E (GeV)', 'PS E err (diamond)', 'Photon beam energy (amo peak) from PS pair E (GeV)', 'PS E err (amo)', 'Abs(P#Sigma) from #rho(770) production', 'Abs(P#Sigma)_err', 'P#Sigma (0)', 'P#Sigma(0)err', 'P#Sigma (90)', 'P#Sigma(90)err', 'P#Sigma (135)', 'P#Sigma(135)err', 'P#Sigma (45)', 'P#Sigma(45)err','#phi_{0} diamond', '#phi_{0} diamond err', '#phi_{0} amo', '#phi_{0} amo err' ]   # Graph titles
  values = [-1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

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




def trigger_asymmetry(rootfile) :

  names = ['trig_asym_status','trig_asym','trig_asym_err']  
  titles = ['Trigger asymmetry status','Beam asymmetry from the trigger', 'Beam asymmetry from the trigger err'] # graph titles
  values = [-1, None, None]                                       # Default values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]


  histoname = 'Heli_asym_gtp'
  dirname = 'highlevel'

  status = 1

  min_counts=100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # Main Trigger BCAL+FCAL2: GTP Bit 1

  bit = 1
  num = h.GetBinContent(bit,1) - h.GetBinContent(bit,2);
  den = h.GetBinContent(bit,1) + h.GetBinContent(bit,2);  

  asym = num/den
  err = 1/math.sqrt(den)

  print(asym,err)
  values = [status, float('%.5f'%(asym)), float('%.5f'%(err)) ]
  
  return values       # return array of values, status first
