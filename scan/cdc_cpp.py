import csv

from ROOT import gROOT,TF1,TH1,TH2


def init() : 

# call each function to get the names, titles and array of defaults set to -1

  pagename = 'CDC_CPP'
  titles = ['CDC status']   # add column at the start for overall CDC status
  names = ['cdc_status']
  values = [-1]

  occ = cdc_occupancy_cpp(False)  # return names, titles, values
  eff = cdc_efficiency_cpp(False)
  dedx = cdc_dedx_cpp(False)
  dedxmean = cdc_dedx_mean_cpp(False)
  ttod = cdc_ttod(False)

  for thing in [ occ, eff, dedx, dedxmean, ttod ] : 

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename, names, titles, values]



def check(run, rootfile) :

  # call each function to get array of metrics, concatenate those into one list, add overall status and return the list
  # the status checks are at the end of each function

  # status codes: 1 (good), 0 (bad) or -1 (some other problem, eg histogram missing or not enough data)

  # acceptable value limits, defined here for accessibility

  # exit if this is not a CPP run
  if run < 100000 or run > 109999 : 
    print('\nERROR - this module is for CPP runs, 100000-109999, not for run %s\n'%run)
    return 0

  occmax = 28 # CPP - expect 11 dead, handful more missing from tracking, many more missing in ET runs

#  dedxmin = 1.9998
#  dedxmax = 2.0402
#  dedxresmin = 0.25
#  dedxresmax = 0.37

  dedxmin = 1.82   # CPP limits
  dedxmax = 2.22
  dedxresmin = 0.25
  dedxresmax = 0.5 

#  e0min = 0.97
#  e5min = 0.96
#  e6min = 0.89

  e0min = 0.8  #CPP
  e5min = 0.7
  e75min = 0.3

#  ttodmeanmax = 15.0
#  ttodsigmamax = 150.0

  dedxmeanmin = 2.5  # for overall dedx, 0 to 10 GeV
  dedxmeanmax = 4.5
  dedxsigmin = 1.0
  dedxsigmax = 4.0
   

  ttodmeanmax = 20.0
  ttodsigmamax = 200.0

  # these return an array [names, values] 

  occ = cdc_occupancy_cpp(rootfile, occmax)
  eff = cdc_efficiency_cpp(rootfile, e0min, e5min, e75min)
  dedx = cdc_dedx_cpp(rootfile, dedxmin, dedxmax, dedxresmin, dedxresmax)
  dedxmean = cdc_dedx_mean_cpp(rootfile, dedxmeanmin, dedxmeanmax, dedxsigmin, dedxsigmax)
  ttod = cdc_ttod(rootfile, ttodmeanmax, ttodsigmamax)

  # set the overall status to the min value of each histogram status

  statuslist = []
  for thing in [occ, eff, dedx, dedxmean, ttod] : 
    statuslist.append(thing[0])   # status is the first value in the array

  cdc_status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [cdc_status]
  for thing in [occ, eff, dedx, dedxmean, ttod] : 
    allvals.extend(thing) 

  return allvals


def cdc_occupancy_cpp(rootfile, occmax=9) :

  titles = ['Occupancy status','Missing straw count']
  names = ['cdc_occ_status','cdc_missing']
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


#  NdeadExpected = array("I",[10, 11, 14, 13, 23, 22, 26, 21, 19, 21, 31, 31, 35, 29, 35, 34, 42, 43, 50, 55, 69, 69, 77, 90, 101, 110, 123, 131])


# ring                    1   2   3  4   5   6    7   8   9  10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25   26   27   28
  FirstLive = array("I",[10, 10, 13, 12, 19, 20, 23, 17, 19, 19,  28,  28,  31,  30,  33,  33,  35,  36,  38,  41,  44,  44,  46,  47,  49,  50,  53,  53])
  LastLive = array("I", [41, 40, 52, 52, 62, 63, 76, 80, 93, 93, 103, 103, 119, 123, 135, 135, 141, 142, 154, 153, 165, 164, 181, 182, 196, 194, 205, 205]) 

  KnownDead = array("I",[244, 421, 422, 423, 424, 425, 426, 577, 669, 670, 709])


  Nfirst = 0

  for ring in range(0,28) :
    
    first = Nfirst + FirstLive[ring]
    last = Nfirst + LastLive[ring]

    ahisto = h.ProjectionY("ring", first+1, last+1 );  #straw 1 is in bin 2
    hits_ring = ahisto.GetEntries()
    floatnstraws = float(1+last-first)
    mean_hits_per_straw = int(hits_ring/floatnstraws)

    if mean_hits_per_straw < 10 :  
      continue

#    print ('ring ',ring+1, ' straws: ',1+last-first, ' hits/straw: ',mean_hits_per_straw)


    for straw in range(first, last+1) :    # range(0,2) is "0 1"

      ahisto = h.ProjectionY("straw_"+str(straw), straw+1, straw+1 )  #straw 1 is in bin 2

      hits_straw = ahisto.GetEntries()

      eff = 1

      if (hits_straw < 0.25 * mean_hits_per_straw) :
        eff = 0

      if eff == 0:
        Ndead = Ndead + 1

#       if not straw in KnownDead:
#          print(str(straw),' dead straw in ring ',ring+1,', av counts ', str(int(mean_hits_per_straw)))

    Nfirst = Nfirst + Nstraws[ring]

    

  # return values, good if less than 10 dead straws

  status=0

  if Ndead <= occmax:
    status=1

  values = [status,Ndead]

  return values
  


def cdc_efficiency_cpp(rootfile, e0min=0.97, e5min=0.96, e75min=0.89) :

  titles = ['Efficiency status','Hit efficiency at 0.04mm','Hit efficiency at 5mm','Hit efficiency at 7.5mm']
  names = ['cdc_eff_status','cdc_eff0','cdc_eff5','cdc_eff7']
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
    return values

  else :

    e0 = h.GetBinContent(1) # // 0.04 mm 
    e5 = h.GetBinContent(65) # // 5 mm 
#    e6 = h.GetBinContent(83) # // 6.4 mm
    e6 = h.GetBinContent(97) # // 7.5 mm

    e0 = float('%.6f'%(e0))
    e5 = float('%.6f'%(e5))
    e6 = float('%.6f'%(e6))

    status = 1

    if e0 < e0min or e5 < e5min or e6 < e75min:
      status = 0

    values = [status, float('%.2f'%(e0)), float('%.2f'%(e5)), float('%.2f'%(e6))]

    return values



def cdc_dedx_cpp(rootfile, dedxmin=1.9998, dedxmax=2.0402, dedxresmin=0.25, dedxresmax=0.37) :

  titles = ['dE/dx status','dE/dx mean at 1.5 GeV/c (keV/cm)','dE/dx resolution at 1.5 GeV/c']
  names = ['cdc_dedx_status','cdc_dedxmean','cdc_dedxres']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_dedx'
  histoname = 'dedx_p'

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
    return values

  p = h.ProjectionY("p1",38,48)

  if p.GetEntries()<500 :
    return values 


  # compress the histo and then find the max bin. Make the Gaussian mean close to this. 

  p4 = p.Clone()
  p4.Rebin(4)
  maxbin = p4.GetMaximumBin()
  maxval = p4.GetXaxis().GetBinCenter(maxbin);

  g = TF1('g','gaus',0,5)

  g.SetParameter(1,maxval)   # mean
  g.SetParLimits(1,maxval*0.9,maxval*1.1)
  g.SetParameter(2,0.3*maxval)   # sigma - root limits this if mean is limited
  g.SetParLimits(2,0.25*maxval,0.75*maxval)


  fitstat = p.Fit('g','q0wB')
  
  pars = []
  for i in range(3):
    pars.append(g.GetParameter(i))

#  lan = TF1('lan','landau',0,12);
  pars.append(4.5*pars[0])
  pars.append(0.83*pars[1])
  pars.append(2.0*pars[2])

#  lan.SetParameters(4.5*pars[0], 0.83*pars[1], 2.0*pars[2])

#  fitstat = p.Fit('lan','0qw')

#  for i in range(3):
#    pars.append(lan.GetParameter(i))


  fsum = TF1("fsum","gaus(0)+landau(3)",0,12)
  for i in range(6) : 
    fsum.SetParameter(i,pars[i]) 
 

  llim = []
  ulim = []
  startval = []

  llim.append(0.5*pars[0])   # gauss height
  ulim.append(1.5*pars[0])
  startval.append(pars[0])

  llim.append(pars[1])   # gauss mean
  ulim.append(1.2*pars[1])
  startval.append(1.001*pars[1])

  llim.append(0) # not used 0.25*pars[1]) # gauss sigma
  ulim.append(0) # not used  pars[2])
#  startval.append(0.5*pars[1]) 
  startval.append(pars[2])

  llim.append(0.2*pars[3])  # area of landau
  ulim.append(0.9*pars[3]) 
  startval.append(0.3*pars[3])

  llim.append(0.8*pars[4])  #mpv
  ulim.append(pars[4])
  startval.append(0.9*pars[4])

  llim.append(0.3*pars[5])  # landau sigma
  ulim.append(2*pars[5])
  startval.append(pars[5])

  for i in [ 0,1,3,4,5] : 
    fsum.SetParLimits(i,llim[i],ulim[i]);
    fsum.SetParameter(i,startval[i]);
#    print("Param %i start val %.3f limits %.3f to %.3f\n" % (i,startval[i],llim[i],ulim[i]))
  
  fsum.SetParameter(2,startval[2])

  fitstat = p.Fit(fsum,"qBELL");

  #if int(fitstat) != 0:     # all these fits looked ok
    #print(rootfile.GetName(),'fit status',int(fitstat))
    #c = TCanvas("c","c",700,500)
    #p.Draw()
    #g.SetLineColor(4)
    #g.Draw("same")
    #p.GetXaxis().SetRangeUser(0,12)
    #c.SaveAs("dedx.png")

  if int(fitstat)%70 != 0 :     #0: successful, 70:hit limits, 140: more limits
    return values

  par = []

  for i in range(6) : 
    pars[i] = fsum.GetParameter(i)


  res = (float)(2.0*pars[2]/pars[1])
    #    // For dedxp histo summed over several runs, projection of bin 38 had gauss mean 2.0666 and projection of bins 38-48
     # had gauss mean 2.03999
    #//mean = 1.02174*(float)pars[1];
  mean = 1.01306*float(pars[1])   

    
  status = 1
  if mean < dedxmin or mean > dedxmax:
      status=0
  if res < dedxresmin or res > dedxresmax:
      status=0

  values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
  
  return values


def cdc_dedx_mean_cpp(rootfile, dedxmeanmin=1.5, dedxmeanmax=2.5, dedxsigmin=0.2, dedxsigmax=3.0) :

  titles = ['dE/dx (overall mean, 0-10 GeV/c) status','dE/dx mean (keV/cm)','dE/dx RMS (keV/cm)']
  names = ['cdc_dedx_overallmean_status','cdc_dedx_overallmean','cdc_dedx_sigma']
  values = [-1,-1,-1]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dirname = '/CDC_dedx'
  histoname = 'dedx_p'

  test = rootfile.cd(dirname)

  if test == False: 
    print('Could not find ' + dirname)
    return values

  h = gROOT.FindObject(histoname)

  if (not not h) == False :
    print('Could not find ' + histoname)
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







def cdc_ttod(rootfile, ttodmeanmax=15.0, ttodsigmamax=150.0) :

  titles = ['TTOD status','TTOD residual mean (#mum)','TTOD residual width (#mum)']
  names = ['cdc_ttod_status','cdc_ttodmean','cdc_ttodres']
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


