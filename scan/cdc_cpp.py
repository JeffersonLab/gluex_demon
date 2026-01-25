from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1,TH1,TH2

# Define the page name
PAGENAME = 'CDC'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [cdc_occupancy_cpp, cdc_efficiency_cpp, cdc_dedx_cpp, cdc_dedx_mean_cpp, cdc_ttod]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def cdc_occupancy_cpp(rootfile) :

  titles = ['Occupancy status','Missing straw count']
  names = ['occ_status','missing']
  values = [-1, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  occmax = 50 # CPP - expect 11 dead, handful more missing from tracking, many more missing in ET runs

  histoname = 'an30_100ns'
  dirname = '/CDC_amp'

  from array import array

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
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

    if mean_hits_per_straw < 20 :  
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
  


def cdc_efficiency_cpp(rootfile) :

  titles = ['Efficiency status','Hit efficiency at 0.04mm','Hit efficiency at 5mm','Hit efficiency at 7.5mm']
  names = ['eff_status','eff0','eff5','eff7']
  values = [-1, None, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  e0min = 0.8  #CPP
  e5min = 0.7
  e75min = 0.3
  
  dirname = '/CDC_Efficiency/Online'
  histoname = 'Efficiency Vs DOCA'

  from array import array

  min_counts = 100

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
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



def cdc_dedx_cpp(rootfile) :

  titles = ['dE/dx status','dE/dx mean at 1.5 GeV/c (keV/cm)','dE/dx resolution at 1.5 GeV/c']
  names = ['dedx_status','dedxmean','dedxres']
  values = [-1,None,None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dedxmin = 1.82   # CPP limits
  dedxmax = 2.22
  dedxresmin = 0.25
  dedxresmax = 0.5 
  
  dirname = '/CDC_dedx'
  histoname = 'dedx_p'

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
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

  p.GetXaxis().SetRangeUser(0,5)

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


def cdc_dedx_mean_cpp(rootfile) :

  titles = ['dE/dx (overall mean, 0-10 GeV/c) status','dE/dx mean (keV/cm)','dE/dx RMS (keV/cm)']
  names = ['dedx_overallmean_status','dedx_overallmean','dedx_sigma']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  dedxmeanmin = 2.5  # for overall dedx, 0 to 10 GeV
  dedxmeanmax = 4.5
  dedxsigmin = 1.0
  dedxsigmax = 4.0

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



def cdc_ttod(rootfile) :

  titles = ['TTOD status','TTOD residual mean (#mum)','TTOD residual width (#mum)']
  names = ['ttod_status','ttodmean','ttodres']
  values = [-1, None, None]

  if not rootfile :  # called by init function
    return [names, titles, values]

  ttodmeanmax = 20.0
  ttodsigmamax = 200.0

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
