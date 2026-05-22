from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'Triggers'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [triggers26]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def triggers26(rootfile) : 

  names = ['trig_status','GTP_trigger_count','bcal_GTPtriggers_mg','bcalfcal_GTPtriggers_mg','ps_GTPtriggers_mg','random_trigger_count',
           'bcal_Hadronic_mg','bcalfcal_Hadronic_mg','ps_Hadronic_mg',
           'bcal_CP_mg','bcalfcal_CP_mg','ps_CP_mg',
           'L1livetime','L1livetime_err','bcal_rate_mg','bcalfcal_rate_mg','ps_rate_mg']
  titles = ['trig_status','All GTP triggers','GTP triggers (%) [BCAL]','GTP triggers (%) [BCAL+FCAL]','GTP triggers (%) [PS]','Random triggers',
            'Hadronic triggers (%) [BCAL]', 'Hadronic triggers (%) [BCAL+FCAL]', 'Hadronic triggers (%) [PS]',
            'Hadronic triggers, coherent peak (%) [BCAL]', 'Hadronic triggers, coherent peak (%) [BCAL+FCAL]', 'Hadronic triggers, coherent peak (%) [PS]',
            'L1 livetime (%)','L1 livetime std. dev. (%)','Trigger rate (kHz) [BCAL]','Trigger rate (kHz) [BCAL+FCAL]','Trigger rate (kHz) [PS]']
            
  values = default_values(names)
  png = ['HistMacro_Trigger']

  if not rootfile :  # called by init function
    return [names, titles, values, png]

  # Main Trigger BCAL+FCAL: GTP Bit 1  became BCAL
  # BCAL Trigger: GTP Bit 3            became BCAL FCAL
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
  min_counts = 0
  
  nbcal = 0
  nbcalfcal = 0
  nps = 0
  nrandom = 0

  h = get_histo(rootfile, dirname, histoname, min_counts)
  
  if h :
    nbcal = h.GetBinContent(1)
    nbcalfcal = h.GetBinContent(3)
    nps = h.GetBinContent(4)

  h = get_histo(rootfile, dirname, histoname2, min_counts)

  if h :
    nrandom = h.GetBinContent(12)

    
  h = get_histo(rootfile, dirname, histoname3, min_counts)

  # all L1 triggers.  NB several bits could be set in the same event.
  ntot = h.GetBinContent(33,1)
  
  status = 1

  values[1] = int(ntot)

  values[5] = int(nrandom)
  
  if ntot > 0 :
    bcalpercent = 100*nbcal/ntot
    values[2] = float('%.1f'%(bcalpercent))

    bcalfcalpercent = 100*nbcalfcal/ntot
    values[3] = float('%.1f'%(bcalfcalpercent))

    pspercent = 100*nps/ntot
    values[4] = float('%.1f'%(pspercent))    

  if nbcal>0 :
    bcal_hadronic = 100*h.GetBinContent(1,3)/nbcal
    bcal_cp = 100*h.GetBinContent(1,4)/nbcal

    values[6] = float('%.1f'%(bcal_hadronic))
    values[9] = float('%.1f'%(bcal_cp))
    
  if nbcalfcal>0:
    bcalfcal_hadronic = 100*h.GetBinContent(3,3)/nbcalfcal
    bcalfcal_cp = 100*h.GetBinContent(3,4)/nbcalfcal

    values[7] =  float('%.1f'%(bcalfcal_hadronic))
    values[10] =  float('%.1f'%(bcalfcal_cp))    

  if nps >0:
    ps_hadronic = 100*h.GetBinContent(4,3)/nps
    ps_cp = 100*h.GetBinContent(4,4)/nps

    values[8] =  float('%.1f'%(ps_hadronic))
    values[11] =  float('%.1f'%(ps_cp))    


  dirname1 = '/occupancy'
  histoname4 = 'L1livetime'
  histoname5 = 'L1GTPRate'
  
  h4 = get_histo(rootfile, dirname1, histoname4, min_counts)

  if h4 :
    h4mean = h4.GetMean()
    h4sig = h4.GetRMS()
    values[12] = float('%.1f'%(h4mean))
    values[13] = float('%.2f'%(h4sig)) 

  h5 = get_histo(rootfile, dirname1, histoname5, min_counts)

  if h5 :
    h5xbin1 = h5.ProjectionY("h5xbin1",1,1)
    h5xbin1mean = h5xbin1.GetMean()
    h5xbin3 = h5.ProjectionY("h5xbin3",3,3)
    h5xbin3mean = h5xbin3.GetMean()
    h5xbin4 = h5.ProjectionY("h5xbin4",4,4)
    h5xbin4mean = h5xbin4.GetMean()
    #title = h5.GetTitle()
    #print(title)
    values[14] = float('%.1f'%(h5xbin1mean))
    values[15] = float('%.1f'%(h5xbin3mean))
    values[16] = float('%.1f'%(h5xbin4mean))
  
  # trigger status  
  if nbcal == 0 or nbcalfcal == 0 or nps == 0 or nrandom == 0:
    status = 0
    
  values[0] = status

  return values       # return array of values, status first
  



