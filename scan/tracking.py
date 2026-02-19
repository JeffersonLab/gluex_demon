from utils import get_histo     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'Tracking'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [fom, ncandidates, ntracks, bcal_matchrate, ecal_matchrate, fcal_matchrate, sc_matchrate, tof_matchrate]
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



def ntracks(rootfile) :

  names = ['ntracks_status','wire_ntracks_mg','time_ntracks_mg']  
  titles = ['Number of tracks status','Mean number of wire-based tracks','Mean number of time-based tracks']
  values = [-1, None, None]
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'NumWireBasedTracks'   # monitoring histogram to check
  dirname = '/Independent/Hist_NumReconstructedObjects'      # directory containing the histogram

  llim = 4    # acceptability limit, same for both
  llim2 = 10
  
  min_counts = 1000
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = h.GetMean()

  status = 1
  if mean < llim : 
      status=0

  values[1] = float('%.1f'%(mean))

  histoname = 'NumTimeBasedTracks'   # monitoring histogram to check
  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = h.GetMean()

  status1 = 1
  if mean < llim2 : 
      status1=0

  values[2] = float('%.1f'%(mean))
  
  values[0] = status and status1
  
  return values       # return array of values, status first


def bcal_matchrate(rootfile) :

  names = ['bcal_status','all_bcal_mg','z_160_190cm_bcal_mg','bcal_matchpertrack_mg']  
  titles = ['BCAL track match rate status','BCAL match rate','BCAL match rate (160 to 190cm)','BCAL match rate (160 to 190cm) / N time-based tracks'] # graph titles
  values = [-1, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]


  dirname = '/Independent/Hist_DetectorMatching/TimeBased/BCAL'
  
  llim1 = 0.75    # acceptability limit
  llim2 = 0.85    # acceptability limit  

  min_counts=100

  histoname = 'TrackBCALModuleVsZ_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackBCALModuleVsZ_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  status2 = 0
  
  if h1 and h2 :
    hits = h1.GetEntries()
    nohits = h2.GetEntries()

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim1 :
        status1 = 1

    bin1 = h1.GetXaxis().FindBin(160)
    bin2 = h1.GetXaxis().FindBin(190)
    
    p1 = h1.ProjectionX('p1')
    p2 = h2.ProjectionX('p2')

    hits = p1.Integral(bin1,bin2)
    nohits = p2.Integral(bin1,bin2)

    chances = hits + nohits
    
    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))

      if match_rate >= llim2 :
        status2 = 1
         
  # match rate / N TBT
  tbt = ntracks(rootfile)

  ntbt = tbt[2]

  status3 = 0
  ratio = 0
  if ntbt > 0:
    ratio = match_rate/ntbt
    values[3] = float('%.4f'%(ratio))
    status3 = 1
        
  values[0] = status1 and status2 and status3
   
  return values       # return array of values, status first



def ecal_matchrate(rootfile) :

  names = ['ecal_match_status','all_ecal_mg','z45_65cm_1g_ecal_mg','ecal_matchpertrack_mg']
  titles = ['ECAL track match rate status','ECAL match rate', 'ECAL match rate > 1 GeV (20-40cm)', 'ECAL match rate > 1 GeV (20-40cm) / N time-based tracks'] # graph titles] # graph titles
  values = [-1, None, None, None]

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
    bin1 = h1.GetXaxis().FindBin(20)
    bin2 = h1.GetXaxis().FindBin(40)

    hits = h1.Integral(bin1,bin2)
    nohits = h2.Integral(bin1,bin2)

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))

      if match_rate >= llim2 :
        status2 = 1

  # match rate / N TBT
  tbt = ntracks(rootfile)

  ntbt = tbt[2]

  status3 = 0
  ratio = 0
  if ntbt > 0:
    ratio = match_rate/ntbt
    values[3] = float('%.4f'%(ratio))
    status3 = 1
        
  values[0] = status1 and status2 and status3
  
  return values       # return array of values, status first



def fcal_matchrate(rootfile) :

  names = ['fcal_match_status','all_fcal_mg','r45_65cm_1g_fcal_mg','fcal_matchpertrack_mg']
  titles = ['FCAL track match rate status','FCAL match rate','FCAL match rate > 1 GeV (45-65cm)', 'FCAL match rate > 1 GeV (45-65cm) / N time-based tracks']
  values = [-1, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/FCAL'
  
  llim = 0.3    # acceptability limit
  llim2 = 0.4
  llim3 = 0.65
  
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
    bin1 = h1.GetXaxis().FindBin(45)
    bin2 = h1.GetXaxis().FindBin(65)

    hits = h1.Integral(bin1,bin2)
    nohits = h2.Integral(bin1,bin2)

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))

      if match_rate >= llim3 :
        status2 = 1

  # match rate / N TBT
  tbt = ntracks(rootfile)

  ntbt = tbt[2]

  status3 = 0
  ratio = 0
  if ntbt > 0:
    ratio = match_rate/ntbt
    values[3] = float('%.4f'%(ratio))
    status3 = 1
        
  values[0] = status1 and status2 and status3

  return values       # return array of values, status first



def sc_matchrate(rootfile) :

  names = ['sc_match_status','sc_match', 'sc_matchpertrack_mg']
  titles = ['SC track match rate status','SC match rate (z = 60 to 95cm)','SC match rate (z = 60 to 95cm) / N time-based tracks']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/SC'
  
  llim = 0.9    # acceptability limit
  
  min_counts=100

  histoname = 'SCPaddleVsZ_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'SCPaddleVsZ_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    bin1 = h1.GetXaxis().FindBin(60)
    bin2 = h1.GetXaxis().FindBin(95)

    p1 = h1.ProjectionX('p1')
    p2 = h2.ProjectionX('p2')

    hits = p1.Integral(bin1,bin2)
    nohits = p2.Integral(bin1,bin2)

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[1] = float('%.3f'%(match_rate))

      if match_rate >= llim :
        status1 = 1

  # match rate / N TBT
  tbt = ntracks(rootfile)

  ntbt = tbt[2]

  status2 = 0
  ratio = 0
  if ntbt > 0:
    ratio = match_rate/ntbt
    values[2] = float('%.4f'%(ratio))
    status2 = 1
        
  values[0] = status1 and status2
        
  return values       # return array of values, status first



def tof_matchrate(rootfile) :

  names = ['tof_match_status','tof_match_4_6g','tof_match_20_60cm','tof_matchpertrack_mg']  
  titles = ['TOF track match rate status','TOF match rate (4 to 6GeV)','TOF match rate (20 to 60cm)', 'TOF match rate (20 to 60cm) / Mean time-based track count'] # graph titles
  values = [-1, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorMatching/TimeBased/TOFPoint'
  
  limg = 0.6  # acceptability limit
  limr = 0.7
  
  min_counts=100

  histoname = 'TrackTOFP_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFP_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status1 = 0
  
  if h1 and h2 :
    bin1 = h1.GetXaxis().FindBin(4.0)
    bin2 = h1.GetXaxis().FindBin(6.0)

    hits = h1.Integral(bin1,bin2)
    nohits = h2.Integral(bin1,bin2)

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances

      values[1] = float('%.3f'%(match_rate))

      if match_rate >= limg :
        status1 = 1
        
        
  # repeat for > 1 GeV histos
  histoname = 'TrackTOFR_HasHit'
  h1 = get_histo(rootfile, dirname, histoname, min_counts)

  histoname = 'TrackTOFR_NoHit'
  h2 = get_histo(rootfile, dirname, histoname, min_counts)

  status2 = 0
  
  if h1 and h2 :
    bin1 = h1.GetXaxis().FindBin(20)
    bin2 = h1.GetXaxis().FindBin(60)

    hits = h1.Integral(bin1,bin2)
    nohits = h2.Integral(bin1,bin2)

    chances = hits + nohits

    if chances > 0 :
      match_rate = hits/chances
      values[2] = float('%.3f'%(match_rate))

      if match_rate >= limr :
        status2 = 1


  # match rate / N TBT
  tbt = ntracks(rootfile)

  ntbt = tbt[2]

  status3 = 0
  ratio = 0
  if ntbt > 0:
    ratio = match_rate/ntbt
    values[3] = float('%.4f'%(ratio))
    status3 = 1
        
  values[0] = status1 and status2 and status3

  
  return values

