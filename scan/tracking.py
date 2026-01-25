from utils import get_histo     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'Tracking'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [fom, ncandidates, nwirebasedtracks, ntimebasedtracks, bcal_matchrate, ecal_matchrate, fcal_matchrate, sc_matchrate, tof_matchrate]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def fom(rootfile) :

  names = ['fom_min_status','fom_min']            
  titles = ['Tracking FOM status','Tracking FOM histo minimum']   # Graph titles
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'TrackingFOM'      # monitoring histogram to check
  dirname = '/Independent/Hist_Reconstruction/Tracking/'          # directory containing that histogram
  llim=0.3
  ulim=0.9
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  tracking_fom_min = h.GetXaxis().GetBinCenter(h.GetMinimumBin())

  status=1

  if tracking_fom_min < llim:
    status=0

  if tracking_fom_min > ulim:
    status=0

  values = [status, float('%.2f'%(tracking_fom_min)) ]

  return values       # return array of values, status first
  


def ncandidates(rootfile) :

  names = ['ncandidates_status','candidates']  
  titles = ['Track candidates status','Mean number of track candidates'] # graph titles
  values = [-1, None]                                    

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'NumTrackCandidates'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0

  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def nwirebasedtracks(rootfile) :

  names = ['nwirebasedtracks_status','wire_based']  
  titles = ['Wire-based tracks status','Mean number of wire-based tracks'] # graph titles
  values = [-1, None]                                    

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'NumWireBasedTracks'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0

  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def ntimebasedtracks(rootfile) :

  names = ['ntimebasedtracks_status','time_based']  
  titles = ['Time-based tracks status','Mean number of time-based tracks'] # graph titles
  values = [-1, None]                                    
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'NumTimeBasedTracks'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 3    # acceptability limit
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0

  values = [status, float('%.1f'%(mean)) ]
  
  return values       # return array of values, status first



def bcal_matchrate(rootfile) :

  names = ['bcalmatch_status','bcal_match']  
  titles = ['BCAL track match rate status','BCAL match rate'] # graph titles
  values = [-1, None]                                    

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'TrackBCALModuleVsZ_HasHit'
  dirname = '/Independent/Hist_DetectorMatching/TimeBased/BCAL'
  
  llim = 0.77    # acceptability limit

  min_counts=100
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  hits = h.GetEntries()

  histoname = 'TrackBCALModuleVsZ_NoHit'
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  nohits = h.GetEntries()

  chances = hits + nohits

  if chances == 0:
    return values
  
  match_rate = hits/chances

  status = 1
  if match_rate < llim : 
      status=0


  values = [status, float('%.3f'%(match_rate)) ]
  
  return values       # return array of values, status first



def ecal_matchrate(rootfile) :

  names = ['ecal_match_status','ecal_match','ecal_match_1g']  
  titles = ['ECAL track match rate status','ECAL match rate','ECAL match rate > 1GeV'] 
  values = [-1, None, None]                                      

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/ECAL'
  
  llim = 0.3    # acceptability limit
  llim2 = 0.55

  min_counts=100

  histoname = 'TrackECALP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackECALP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackECALR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackECALR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2
  
  return values       # return array of values, status first


def fcal_matchrate(rootfile) :

  names = ['fcal_match_status','fcal_match','fcal_match_1g']  
  titles = ['FCAL track match rate status','FCAL match rate','FCAL match rate > 1GeV'] # graph titles
  values = [-1, None, None]                                       # Defult values, keep as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/FCAL'
  
  llim = 0.33    # acceptability limit
  llim2 = 0.42

  min_counts=100

  histoname = 'TrackFCALP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackFCALP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackFCALR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackFCALR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2

  
  return values       # return array of values, status first



def sc_matchrate(rootfile) :

  names = ['sc_match_status','sc_match']  
  titles = ['SC track match rate status','SC match rate']
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/SC'
  
  llim = 0.86    # acceptability limit

  min_counts=100

  histoname = 'SCPaddleVsZ_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'SCPaddleVsZ_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        values[0] = 1
  
  return values       # return array of values, status first



def tof_matchrate(rootfile) :

  names = ['tof_match_status','tof_match','tof_match_1g']  
  titles = ['TOF track match rate status','TOF match rate','TOF match rate > 1GeV'] # graph titles
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/TOFPoint'
  
  llim = 0.25    # acceptability limit
  llim2 = 0.36

  min_counts=100

  histoname = 'TrackTOFP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

        
  # repeat for > 1 GeV histos
  histoname = 'TrackTOFR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))
      
      if match_rate >= llim2 :
        status2 = 1

  values[0] = status1 and status2

  
  return values

