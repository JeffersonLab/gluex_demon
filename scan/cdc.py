import csv

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1
  pagename = 'CDC'
  titles = ['CDC status']   # add column at the start for overall CDC status
  names = ['cdc_status']
  values = [-1]

  occ = cdc_occupancy(False)  # return names, titles, values
  eff = cdc_efficiency(False)
  dedx = cdc_dedx(False)
  ttod = cdc_ttod(False)

  for thing in [ occ, eff, dedx, ttod ] : 

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # acceptable value limits, defined here for accessibility

  occmax = 9

  dedxmin = 1.9998
  dedxmax = 2.0402
  dedxresmin = 0.25
  dedxresmax = 0.37

  e0min = 0.97
  e5min = 0.96
  e6min = 0.89

  ttodmeanmax = 15.0
  ttodsigmamax = 150.0

  # these return an array [names, values] 

  occ = cdc_occupancy(rootfile, occmax)
  eff = cdc_efficiency(rootfile, e0min, e5min, e6min)
  dedx = cdc_dedx(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)
  ttod = cdc_ttod(rootfile, ttodmeanmax, ttodsigmamax)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [occ, eff, dedx, ttod] : 
    statuslist.append(thing[0])   # status is the first value in the array

  cdc_status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [cdc_status]
  for thing in [occ, eff, dedx, ttod] : 
    allvals.extend(thing) 

  return allvals


def cdc_occupancy(rootfile, occmax=9) :

  titles = ['Occupancy status','Missing straw count']
  names = ['cdc_occ','cdc_missing']
  values = [-1, -1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  histoname = 'an30_100ns'
  dirname = '/CDC_amp'

  from array import array

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
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
  


def cdc_efficiency(rootfile, e0min=0.97, e5min=0.96, e6min=0.89) :

  titles = ['Efficiency status','Hit efficiency at 0.04mm','Hit efficiency at 5mm','Hit efficiency at 6.4mm']
  names = ['cdc_eff','cdc_eff0','cdc_eff5','cdc_eff6']
  values = [-1,-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_Efficiency/Online'
  histoname = 'Efficiency Vs DOCA'

  from array import array

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values

  if h.GetEntries()<100 :
    values[0] = -2
    return values

  else :

    e0 = h.GetBinContent(1) # // 0.04 mm 
    e5 = h.GetBinContent(65) # // 5 mm 
    e6 = h.GetBinContent(83) # // 6.4 mm

    e0 = float('%.6f'%(e0))
    e5 = float('%.6f'%(e5))
    e6 = float('%.6f'%(e6))

    status = 1

    if e0 < e0min or e5 < e5min or e6 < e6min:
      status = 0

    values = [status, e0, e5, e6]

    return values



def cdc_dedx(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['dE/dx status','dE/dx mean at 1.5 GeV/c (keV/cm)','dE/dx resolution at 1.5 GeV/c']
  names = ['cdc_dedx','cdc_dedxmean','cdc_dedxres']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_dedx'
  histoname = 'dedx_p_pos'

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values

  pcut = 1.5 #;    // draw cut through histo at p=1.5 GeV/c
  pbin = h.GetXaxis().FindBin(pcut)
  p = h.ProjectionY("p1",pbin,pbin)

  if p.GetEntries()<5 :
    return values 

  g = TF1('g','gaus',0,12)

  fitstat = p.Fit('g','0qwes')
  
  #print 'fit status ',fitstat.IsValid(), fitstat.Status()

  if fitstat == 0:
    mean = g.GetParameter(1)
    res = 2.0*g.GetParameter(2)/mean

    status = 1
    if mean < dedxmin or mean > dedxmax:
      status=0
    if res < dedxresmin or res > dedxresmax:
      status=0

    values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
  
  return values


def cdc_ttod(rootfile, ttodmeanmax=15.0, ttodsigmamax=150.0) :

  titles = ['TTOD status','TTOD residual mean (#mum)','TTOD residual width (#mum)']
  names = ['cdc_ttod','cdc_ttodmean','cdc_ttodres']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_TimeToDistance'
  histoname = 'Residual Vs. Drift Time'

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values

  if h.GetEntries()<3e5 :  # NB need 1e6 to fit the histo.
    return values 

  mean = 1e4*h.GetMean(2)   # convert from cm to um
  sigma = 1e4*h.GetRMS(2)   # convert from cm to um

  status = 1

  if abs(mean) > ttodmeanmax or abs(sigma) > ttodsigmamax:
    status=0

  values = [status, float('%.3f'%(mean)), float('%.3f'%(sigma))]
  
  return values


