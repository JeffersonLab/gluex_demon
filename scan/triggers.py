from utils import get_histo     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'Triggers'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [triggers]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def triggers(rootfile) : 

  names = ['trig_status','main_trig','bcal_trig','bcal_trigratio_mg','ps_trig','ps_trigratio_mg','random_trig','random_trigratio_mg']
  titles = ['tr_status','Main triggers','BCAL triggers','BCAL triggers/Main triggers (%)','PS triggers','PS triggers/Main triggers (%)','Random triggers','Random triggers/Main triggers (%)']
  values = [-1, None, None, None, None, None, None, None ]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # Main Trigger BCAL+FCAL: GTP Bit 1
  # BCAL Trigger: GTP Bit 3            
  # PS Trigger: GTP Bit 4
  # Random Trigger: FP Bit 12		
  
  # The histograms are in one place for the REST production files and another for monitoring files.

  test=rootfile.GetDirectory('/L1')
  
  if test :
    dirname = '/L1'
    histoname = 'trig_bit'
    histoname2 = 'trig_bit_fp'
  else:
    dirname = '/highlevel'
    histoname = 'L1bits_gtp'
    histoname2 = 'L1bits_fp'
    
  min_counts = 100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  nmain = h.GetBinContent(1)
  nbcal = h.GetBinContent(3)
  nps = h.GetBinContent(4)

  min_counts = 0
  h = get_histo(rootfile, dirname, histoname2, min_counts)

  if (h) :
    nrandom = h.GetBinContent(12)
  else :
    nrandom = 0
            

  status = 1

  if nmain > 0 :
    bcalpercent = 100*nbcal/nmain
    bcalpercent = float('%.1f'%(bcalpercent))
    pspercent = 100*nps/nmain
    pspercent = float('%.1f'%(pspercent))    
    randompercent = 100*nrandom/nmain
    randompercent = float('%.3f'%(randompercent))    
  else :
    bcalpercent = None
    pspercent = None
    randompercent = None

  if nmain == 0 or nbcal == 0 or nps == 0 or nrandom == 0:
    status = 0
  
  values = [status, int(nmain), int(nbcal), bcalpercent, int(nps), pspercent, int(nrandom), randompercent ]

  return values       # return array of values, status first
  



