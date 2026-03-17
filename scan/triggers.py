from utils import get_histo, default_values     # demon's helper functions
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

  names = ['trig_status','GTP_trigger_count','main_GTPtriggers_mg','bcal_GTPtriggers_mg','ps_GTPtriggers_mg','random_trigger_count',
           'main_Hadronic_mg','bcal_Hadronic_mg','ps_Hadronic_mg',
           'main_CP_mg','bcal_CP_mg','ps_CP_mg']
  titles = ['trig_status','All GTP triggers','GTP triggers (%) [main]','GTP triggers (%) [BCAL]','GTP triggers (%) [PS]','Random triggers',
            'Hadronic triggers (%) [main]', 'Hadronic triggers (%) [BCAL]', 'Hadronic triggers (%) [PS]',
            'Hadronic triggers, coherent peak (%) [main]', 'Hadronic triggers, coherent peak (%) [BCAL]', 'Hadronic triggers, coherent peak (%) [PS]']
            
  values = default_values(names)
  png = ['HistMacro_Trigger']

  if not rootfile :  # called by init function
    return [names, titles, values, png]

  # Main Trigger BCAL+FCAL: GTP Bit 1
  # BCAL Trigger: GTP Bit 3            
  # PS Trigger: GTP Bit 4
  # Random Trigger: FP Bit 12		
  
  # The histograms are in one place for the REST production files and another for monitoring files.

#  test=rootfile.GetDirectory('/L1')
    #if test :
  #  dirname = '/L1'
  #  histoname = 'trig_bit'
  #  histoname2 = 'trig_bit_fp'
  #else:

  dirname = '/highlevel'
  histoname = 'L1bits_gtp'
  histoname2 = 'L1bits_fp'
  histoname3 = 'NumTriggers'
  
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

    
  h = get_histo(rootfile, dirname, histoname3, min_counts)

  # all L1 triggers.  NB several bits could be set in the same event.
  ntot = h.GetBinContent(33,1)
  
  status = 1

  values[1] = int(ntot)

  values[5] = int(nrandom)
  
  if ntot > 0 :
    mainpercent = 100*nmain/ntot
    values[2] = float('%.1f'%(mainpercent))

    bcalpercent = 100*nbcal/ntot
    values[3] = float('%.1f'%(bcalpercent))

    pspercent = 100*nps/ntot
    values[4] = float('%.1f'%(pspercent))    

  if nmain>0 :
    main_hadronic = 100*h.GetBinContent(1,3)/nmain
    main_cp = 100*h.GetBinContent(1,4)/nmain

    values[6] = float('%.1f'%(main_hadronic))
    values[9] = float('%.1f'%(main_cp))
    
  if nbcal>0:
    bcal_hadronic = 100*h.GetBinContent(3,3)/nbcal
    bcal_cp = 100*h.GetBinContent(3,4)/nbcal

    values[7] =  float('%.1f'%(bcal_hadronic))
    values[10] =  float('%.1f'%(bcal_cp))    

  if nps >0:
    ps_hadronic = 100*h.GetBinContent(4,3)/nps
    ps_cp = 100*h.GetBinContent(4,4)/nps

    values[8] =  float('%.1f'%(ps_hadronic))
    values[11] =  float('%.1f'%(ps_cp))    

  # trigger status  
  if nmain == 0 or nbcal == 0 or nps == 0 or nrandom == 0:
    status = 0
    
  values[0] = status

  return values       # return array of values, status first
  



