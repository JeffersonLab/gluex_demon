from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1, TH1I

# Define the page name
PAGENAME = 'PhotonBeam'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [rho_psigma_pse]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def rho_psigma_pse(rootfile) : 

  names = ['photons_psigma_pse_status', 'photons_ps_e', 'photons_ps_e_err', 'photons_rho_psigma', 'photons_rho_psigma_err', 'photons_rho_psigma_135', 'photons_rho_psigma_135_err', 'photons_rho_psigma_45', 'photons_rho_psigma_45_err', 'photons_rho_phi0_diamond', 'photons_rho_phi0_diamond_err', 'photons_rho_phi0_amo', 'photons_rho_phi0_amo_err' ]
  titles = ['PS E and Rho P#Sigma status', 'Photon beam energy (diamond edge, amo peak) from PS pair E (GeV)', 'PS E err','Abs(P#Sigma) from #rho(770) production', 'Abs(P#Sigma)_err', 'P#Sigma (135)', 'P#Sigma(135)err', 'P#Sigma (45)', 'P#Sigma(45)err','#phi_{0} diamond', '#phi_{0} diamond err', '#phi_{0} amo', '#phi_{0} amo err' ]   # Graph titles
  values = [-1, None, None, None, None, None, None, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'Psi_rho'                       # monitoring histogram to check
  dirname = '/cpp_hists/Custom_cpp_hists/'      # directory containing the histogram

  min_counts = 100
  hpsi = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'PS_E'   # monitoring histogram to check
  dirname = '/PS_flux/PSC_PS'      # directory containing the histogram

  min_counts = 1000
  hps = get_histo(rootfile, dirname, histoname, min_counts)

  if (not (hpsi and hps)) :
    return values

  # find out if this has a sharp peak (diamond) or broad peak (amo)
  # diamond coh peak is about 1 GeV wide
  
  # See if counts exceed half max at 0.5 GeV either side of maximum, yes = amo.
  
  psmaxbin = hps.GetMaximumBin()
  psmaxe = hps.GetBinCenter(psmaxbin)

  halfmaxcounts = 0.5*hps.GetMaximum()
  
  counts_before = hps.GetBinContent(hps.FindBin(psmaxe-0.5))
  counts_after = hps.GetBinContent(hps.FindBin(psmaxe+0.5))   

  amo = False

  if counts_before > halfmaxcounts and counts_after > halfmaxcounts :
    amo = True

  #print('amo:',amo) #***

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
    hdiff.SetDirectory(0)  # avoid RuntimeWarning: Replacing existing TH1

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


  # --- cpp hists psi histo ---
  #hpsi.Rebin(4)  

  f = TF1('f','[0]*(1.0 + [1]*cos(2*(x + [2])/180.*3.14159))',-180.,180.)
  fitstat = hpsi.Fit('f','Q')

  #print('fitstat',int(fitstat))

  if int(fitstat) != 0 :
    values[0] = -1
    return values
  
  PSigma = f.GetParameter(1)
  PSigmaErr = f.GetParError(1)
  
  Phi0 = f.GetParameter(2)
  Phi0Err = f.GetParError(2)

  if Phi0 > 360:
    Phi0 = Phi0%360.0   # deal with few extra rotations

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
    pol = -1
    
    if PSigma>0 and abs(Phi0)>22 : # 135 para
      pol=135
      PSigma135 = PSigma
      PSigma135Err = PSigmaErr
    elif PSigma<0 and abs(Phi0)>22 : # 45 perp
      pol=45
      PSigma45 = PSigma
      PSigma45Err = PSigmaErr

    if pol < 0 :       # could not determine polarization
      values[0] = -1
      return values

    
  PSigma = abs(PSigma)    # report abs value for overall graph to make it simpler

  values[0] = 1    # status
  index = 3

  for x in [PSigma, PSigmaErr, PSigma135, PSigma135Err, PSigma45, PSigma45Err, Phi0D, Phi0ErrD, Phi0Amo, Phi0ErrAmo] :
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




