from utils import get_histo

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1
  pagename = 'CDC'
  titles = ['CDC status']   # add column at the start for overall CDC status
  names = ['cdc_status']
  values = [-1]

  occ = occupancy(False)  # return names, titles, values
  eff = efficiency(False)
  d = dedx(False)
  dmean = dedx_mean(False)
  t = ttod(False)

  for thing in [ occ, eff, d, dmean, t ] : 

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # If the histogram is missing or the hit fails, status is set to -1 and data are set to None
  
  # acceptable value limits, defined here for accessibility

  occmax = 25 # expect 9 dead but more look dead in ET runs

  dedxmin = 1.9998
  dedxmax = 2.0402
  dedxresmin = 0.25
  dedxresmax = 0.37

  dedxmeanmin = 2.5  # for overall dedx, 0 to 10 GeV
  dedxmeanmax = 4.5
  dedxsigmin = 1.0
  dedxsigmax = 4.0


  e0min = 0.97
  e5min = 0.96
  e6min = 0.89

  ttodmeanmax = 15.0
  ttodsigmamax = 150.0

  # these return an array [names, values] 

  occ = occupancy(rootfile, occmax)
  eff = efficiency(rootfile, e0min, e5min, e6min)
  d = dedx(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)
  dmean = dedx_mean(rootfile, dedxmeanmin, dedxmeanmax, dedxsigmin, dedxsigmax)
  t = ttod(rootfile, ttodmeanmax, ttodsigmamax)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [ occ, eff, d, dmean, t ] : 
    statuslist.append(thing[0])   # status is the first value in the array

  cdc_status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [cdc_status]
  for thing in [ occ, eff, d, dmean, t ] :   
    allvals.extend(thing) 

  return allvals


def occupancy(rootfile, occmax=9) :

  titles = ['Occupancy status','Missing straw count']
  names = ['occ_status','n_missing']
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'an30_100ns'
  dirname = '/CDC_amp'

  from array import array

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  Nstraws = array("I", [42, 42, 54, 54, 66, 66, 80, 80, 93, 93, 106, 106, 123, 123, 135, 135, 146, 146, 158, 158, 170, 170, 182, 182, 197, 197, 209, 209])

  Ndead = 0
  Nfirst = 0

  #deadstraws = []

  for ring in range(0,28) :
    
    ahisto = h.ProjectionY("ring", Nfirst+2, Nfirst+Nstraws[ring]+1 );  #straw 1 is in bin 2

    hits_ring = ahisto.GetEntries()
   
    floatnstraws = float(Nstraws[ring])

    mean_hits_per_straw = int(hits_ring/floatnstraws)

    if mean_hits_per_straw < 20 :  
      continue

    for straw in range(Nfirst+1, Nfirst+Nstraws[ring]+1) :

      ahisto = h.ProjectionY("straw_"+str(straw), straw+1, straw+1 )  #straw 1 is in bin 2

      hits_straw = ahisto.GetEntries()

      eff = 1

      if (hits_straw < 0.25 * mean_hits_per_straw) :
        eff = 0

      if eff == 0:
        Ndead = Ndead + 1
        #deadstraws.append(straw)

        #print "straw " + str(straw) + " counts " + str(hits_straw) + " mean for ring " + str(mean_hits_per_straw)
        #disconnected: 709, 2384.  # problem: 244


    Nfirst = Nfirst + Nstraws[ring]

  # return values, good if less than 10 dead straws

  status=0
  if Ndead < occmax:
    status=1

  values = [status,Ndead]

  return values
  


def efficiency(rootfile, e0min=0.97, e5min=0.96, e6min=0.89) :

  titles = ['Efficiency status', 'Hit efficiency at 0.04mm', 'Hit efficiency at 0.04mm error', 'Hit efficiency at 5mm', 'Hit efficiency at 5mm error', 'Hit efficiency at 6.4mm', 'Hit efficiency at 6.4mm error']
  names = ['eff_status', 'eff0_hitefficiency_mg', 'eff0_hitefficiency_mg_err', 'eff5_hitefficiency_mg', 'eff5_hitefficiency_mg_err', 'eff6_hitefficiency_mg', 'eff6_hitefficiency_mg_err']
  values = [-1, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_Efficiency/Online'
  histoname = 'Efficiency Vs DOCA'

  min_counts = 100

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  else :

    e0 = h.GetBinContent(1) # // 0.04 mm 
    e5 = h.GetBinContent(65) # // 5 mm 
    e6 = h.GetBinContent(83) # // 6.4 mm

    e0err = h.GetBinError(1)*100
    e5err = h.GetBinError(65)*100
    e6err = h.GetBinError(83)*100    
    
    status = 1

    if e0 < e0min or e5 < e5min or e6 < e6min:
      status = 0

    values = [status, float('%.2f'%(e0)), float('%.3f'%(e0err)),float('%.2f'%(e5)), float('%.3f'%(e5err)), float('%.2f'%(e6)), float('%.3f'%(e6err))]

    return values



def dedx(rootfile, dedxmin=1.9998, dedxmax=2.0402, resmin=0.25, resmax=0.37) :

  titles = ['dE/dx status', 'dE/dx q+ mean at 1.5 GeV/c (keV/cm)', 'dE/dx q+ resolution at 1.5 GeV/c', 'dE/dx q- mean at 1.5 GeV/c (keV/cm)', 'dE/dx q- resolution at 1.5 GeV/c', 'dE/dx q+ overall mean (keV/cm)', 'dE/dx q+ overall width']
  names = ['dedx_status', 'qp_dedx_mean', 'qp_dedx_res', 'qm_dedx_mean', 'qm_dedx_res', 'qp_dedx_allmean', 'qp_dedx_allsig']
  values = [-1, None, None, None, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_dedx'
  min_counts = 100
  fitoptions = "0QWERS"
  
  histoname = 'dedx_p_pos'

  qpstatus = 1
  qnstatus = 1
  
  h = get_histo(rootfile, dirname, histoname, min_counts)
  
  if h:

    # find the overall mean dedx first

    pp = h.ProjectionY("p1",0,10)
    oamean = pp.GetMean()
    oasig = pp.GetRMS()

    values[5] = float('%.5f'%(oamean))
    values[6] = float('%.5f'%(oasig)) 
    
    ntracks = h.GetEntries()    
    
    if ntracks > 1e6: 
      pbin1 = 38  # h.GetXaxis().FindBin(pcut)
      pbin2 = pbin1
      scale = 1.0
    elif ntracks >= 1000:
      pbin1 = 38
      pbin2 = 48
      scale = 1.0214     #scales 10bin q+ result to match 1bin q+ result
    else:
      scale = 0
  
    if scale > 0:
      mincounts1D = 1000      
      qp = check_dedx(h, mincounts1D, fitoptions, pbin1, pbin2, scale, dedxmin, dedxmax, resmin, resmax)
      qpstatus =  qp[0]
      values[1] = qp[1]
      values[2] = qp[2]
      
  else:
    qpstatus = -1   #unknown, no histo


    
  min_counts = 1e4
  histoname = 'dedx_p_neg'
  
  h = get_histo(rootfile, dirname, histoname, min_counts)
  
  if h:

    ntracks = h.GetEntries()    
    
    if ntracks > 1e6: 
      pbin1 = 38  # h.GetXaxis().FindBin(pcut)
      pbin2 = pbin1
      scale = 1.0
    elif ntracks >= 1000:
      pbin1 = 38
      pbin2 = 48
      scale = 1.0214     #scales 10bin q+ result to match 1bin q+ result
    else:
      scale = 0
  
    if scale > 0:
      mincounts1D = 1000      
      qn = check_dedx(h, mincounts1D, fitoptions, pbin1, pbin2, scale, dedxmin, dedxmax, resmin, resmax)
      qnstatus =  qp[0]
      values[3] = qn[1]
      values[4] = qn[2]

  else:
    qnstatus = -1   #unknown, no histo
      
  values[0] = min(qpstatus,qnstatus)
    
  return values



def dedx_mean(rootfile, dedxmeanmin=1.5, dedxmeanmax=2.5, dedxsigmin=0.2, dedxsigmax=3.0) :

  titles = ['dE/dx (overall mean, 0-10 GeV/c) status','dE/dx mean (keV/cm)','dE/dx RMS (keV/cm)']
  names = ['dedx_overallmean_status','dedx_overallmean','dedx_overallsigma']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_dedx'
  histoname = 'dedx_p'

  min_counts = 100

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  pp = h.ProjectionY("p1",0,10)

  mean = pp.GetMean()
  sig = pp.GetRMS()
    
  status = 1
  if mean < dedxmeanmin or mean > dedxmeanmax:
      status=0
  if sig < dedxsigmin or sig > dedxsigmax:
      status=0

  values = [status, float('%.5f'%(mean)), float('%.5f'%(sig)) ]
  
  return values



def ttod(rootfile, ttodmeanmax=15.0, ttodsigmamax=150.0) :

  titles = ['TTOD status','TTOD residual mean (#mum)','TTOD residual width (#mum)']
  names = ['ttod_status','ttod_mean','ttod_res']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_TimeToDistance'
  histoname = 'Residual Vs. Drift Time'

  min_counts = 3e5

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  mean = 1e4*h.GetMean(2)   # convert from cm to um
  sigma = 1e4*h.GetRMS(2)   # convert from cm to um

  status = 1

  if abs(mean) > ttodmeanmax or abs(sigma) > ttodsigmamax:
    status=0

  values = [status, float('%.3f'%(mean)), float('%.3f'%(sigma))]
  
  return values




def check_dedx(h, mincounts1D, fitoptions, bmin, bmax, scale, dedxmin, dedxmax, resmin, resmax) :

  values = [ -1, None, None ]   # defaults in case fit fails

  p = h.ProjectionY("p1", bmin, bmax) 

  if p.GetEntries()<1000 :
    return values 

  p.GetXaxis().SetRangeUser(0,5)
  
  g = TF1('g','gaus',0,12)

  fitstat = p.Fit('g',fitoptions)
  
  #print 'fit status ',fitstat.IsValid(), fitstat.Status()

  if int(fitstat) == 0:
    mean = scale*g.GetParameter(1)
    res = 2.0*g.GetParameter(2)/mean

    status = 1
    if mean < dedxmin or mean > dedxmax:
      status=0
    if res < resmin or res > resmax:
      status=0

    values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
    
  return values
