import csv

from ROOT import gROOT,TF1


def init() : 

# call each function to get the names, titles and array of defaults set to -1
  pagename = 'FDC'
  titles = ['FDC status']   # add column at the start for overall FDC status
  names = ['fdc_status']
  values = [-1]

#  occ = fdc_occupancy(False)  # return names, titles, values
  tdc = fdc_tdc(False)
  dedxpos = fdc_dedxpos(False)
  dedxneg = fdc_dedxneg(False)

  for thing in [ tdc, dedxpos, dedxneg ] : 

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # acceptable value limits, defined here for accessibility

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5

  tdcmin = -10
  tdcmax = 10


  # these return an array [names, values] 

  tdc = fdc_tdc(rootfile, tdcmin, tdcmax)

  dedxpos = fdc_dedxpos(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)

  dedxneg = fdc_dedxneg(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [tdc, dedxpos, dedxneg] : 
    statuslist.append(thing[0])   # status is the first value in the array

  fdc_status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [fdc_status]
  for thing in [tdc, dedxpos, dedxneg] : 
    allvals.extend(thing) 

  return allvals



def fdc_dedxpos(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['q+ dE/dx status','q+ dE/dx mean at 1.5 GeV/c (keV/cm)','q+ dE/dx resolution at 1.5 GeV/c']
  names = ['fdc_dedxpos_status','fdc_dedxposmean','fdc_dedxposres']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q+'

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

  p.GetXaxis().SetRangeUser(0,5)

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


def fdc_dedxneg(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['q- dE/dx status','q- dE/dx mean at 1.5 GeV/c (keV/cm)','q- dE/dx resolution at 1.5 GeV/c']
  names = ['fdc_dedxneg_status','fdc_dedxnegmean','fdc_dedxnegres']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q-'

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



def fdc_tdc(rootfile, tdcmin=-2, tdcmax=2) :

  titles = ['FDC TDC status','FDC hit wire time peak, max diff from mean (ns)']
  names = ['fdc_tdc_status','fdc_tdc_max_diff']
  values = [-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/HLDetectorTiming/Physics Triggers/FDC'
  histoname = 'FDCHit Wire time vs. module'

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values

  n = h.GetEntries()

  nmin = 0.5*(n/48)   # 0.5 x entries/number of modules (one is always missing?) 
  # find the overall peak time, then look at each module to find the tdiff

  p = h.ProjectionY("p",1,48)   # 400 bins !

  maxbin = p.GetMaximumBin()
  overall_epeak = p.GetXaxis().GetBinCenter(maxbin)
  max_tdiff = 0

  for mod in range(1,49):
    p = h.ProjectionY("p",mod,mod)   # 400 bins !
    #p.Rebin(8)
    if p.GetEntries() > nmin:

      # find the bin with max content, histo looks like spike on flat bg
      maxbin = p.GetMaximumBin()
      epeak = p.GetXaxis().GetBinCenter(maxbin)
      tdiff = epeak - overall_epeak
      if abs(tdiff) > abs(max_tdiff):
        max_tdiff = tdiff  

  status = 1
  if max_tdiff < tdcmin or max_tdiff > tdcmax:
    status=0

  values = [status, float('%.1f'%(max_tdiff)) ]
  
  return values




