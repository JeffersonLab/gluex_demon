from utils import get_histo
from ROOT import gROOT

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms
#                                                                         (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#


def init() : 
  
  pagename = 'TOF_1'          # Title for the page of graphs.  Best avoid spaces.
  
  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here
  
  names = ['tof_1_status']    # Graph name, tof_1_status 
  titles = ['tof_1 status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False
  
  dEdxPlane1 = tof_1_dEdxP1(False)
  dEdxPlane2 = tof_1_dEdxP2(False)
  
  dxpos = tof_1_dxpos(False) # xpos difference between horizontal plane dt data and tracking
  dypos = tof_1_dypos(False) # ypos difference between vertical plane dt data and tracking
  
  
  for thing in [ dEdxPlane1, dEdxPlane2, dxpos, dypos ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])
    
  return [pagename,names,titles,values]


def check(run, rootfile) :
  
  # This calls the custom functions to get an array of metrics,
  # concatenates those into one list, adds the overall status and returns the list
  
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # Metrics can be None if histo is missing or fit is bad
  
  # List of custom functions, called with arguments rootfile followed by the value limits.
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list
  
  dEdxPlane1 = tof_1_dEdxP1(rootfile)
  dEdxPlane2 = tof_1_dEdxP2(rootfile)
  
  dxpos = tof_1_dxpos(rootfile)
  dypos = tof_1_dypos(rootfile)
    
  # This finds the overall status, setting it to the min value of each histogram status
    
  statuslist = []
  for thing in [dEdxPlane1, dEdxPlane2, dxpos, dypos] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)
  
  # add overall status to the start of the lists before concatenating & returning.
  
  allvals = [status]
  
  for thing in [dEdxPlane1, dEdxPlane2, dxpos, dypos] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 

# tof dEdX Horizontal Plane
def tof_1_dEdxP1(rootfile) :
  
  # print('in tof_1_dEdxP1()...')
  
  # Provide unique graph names. The first must be the status code from this function.

  names = ['dEdxP1_status','dEdxP1','dEdxP1_err']  
  titles = ['dEdx Horizontal Plane','dEdx [GeV]','#sigma dEdx [GeV]']      # These will be the graph titles
  values = [-1, None, None]                                       # Default values, keep status as -1
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.
  
  histoname = 'TOFPointEnergyP1'   # monitoring histogram to check
  dirname = '/Independent/Hist_Reconstruction'      # directory containing the histogram
  
  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values
  
  # code to check the histogram and find the status values
  
  MAX = h.GetBinCenter(h.GetMaximumBin())
  r = h.Fit("landau","Q0","R", MAX*0.9, MAX*2.2)

  if int(r) != 0 :  # bad fit
    return values

  f1 = h.GetFunction("landau")
  MPV = f1.GetParameter(1);
  dMPV = f1.GetParError(1);  
  
  dEdxP1 = MPV
  dEdxP1_err = dMPV
  
  status = 1
  
  values = [status, float('%.5f'%(dEdxP1)), float('%.5f'%(dEdxP1_err)) ]
  
  return values       # return array of values, status first


# tof dEdX Vertical Plane
def tof_1_dEdxP2(rootfile) :
  
  # Example custom function to check another histogram
  
  #print('in tof_1_dEdxP2()...')
  
  # Provide unique graph names. The first must be the status code from this function.  
  
  names = ['dEdxP2_status','dEdxP2','dEdxP2_err']  
  titles = ['dEdx Vertical Plane','dEdx [GeV]','#sigma dEdx [GeV]']      # These will be the graph titles
  values = [-1,-1,-1]                                       # Default values, keep as -1
  
  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.

  histoname = 'TOFPointEnergyP2'   # monitoring histogram to check
  dirname = '/Independent/Hist_Reconstruction'      # directory containing the histogram

  min_counts = 1000

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values

  MAX = h.GetBinCenter(h.GetMaximumBin())

  r = h.Fit("landau","Q0","R", MAX*0.9, MAX*2.2)

  if int(r) != 0 :  # bad fit
    return values

  f1 = h.GetFunction("landau")
  MPV = f1.GetParameter(1);
  dMPV = f1.GetParError(1);
  
  dEdxP2 = MPV
  dEdxP2_err = dMPV
  
  status = 1
  
  values = [status, float('%.5f'%(dEdxP2)), float('%.5f'%(dEdxP2_err)) ]
  
  return values       # return array of values, status first


# tof dxpos: X-position from delta T Horizontal plane minus x position from tracking
def tof_1_dxpos(rootfile):                      
  
  #print('in tof_1_dxpos()...')

  # Provide unique graph names. The first must be the status code from this function. 

  
  names = ['dx_status',
           'dx14','dx14_err',
           'dx15','dx15_err',
           'dx16','dx16_err',
           'dx17','dx17_err',
           'dx18','dx18_err',
           'dx19','dx19_err',
           'dx20','dx20_err',
           'dx21','dx21_err',
           'dx22','dx22_err',
           'dx23','dx23_err',
           'dx24','dx24_err',
           'dx25','dx25_err',
           'dx26','dx26_err',
           'dx27','dx27_err',
           'dx28','dx28_err',
           'dx29','dx29_err',
           'dx30','dx30_err',
           'dx31','dx31_err',
           'dx32','dx32_err',
           'dx33','dx33_err']  
  titles = ['dx status',
            '#Deltax Paddle 14','#sigma #DeltaX Paddle 14',
            '#Deltax Paddle 15','#sigma #DeltaX Paddle 15',
            '#Deltax Paddle 16','#sigma #DeltaX Paddle 16',
            '#Deltax Paddle 17','#sigma #DeltaX Paddle 17',
            '#Deltax Paddle 18','#sigma #DeltaX Paddle 18',
            '#Deltax Paddle 19','#sigma #DeltaX Paddle 19',
            '#Deltax Paddle 20','#sigma #DeltaX Paddle 20',
            '#Deltax Paddle 21','#sigma #DeltaX Paddle 21',
            '#Deltax Paddle 22','#sigma #DeltaX Paddle 22',
            '#Deltax Paddle 23','#sigma #DeltaX Paddle 23',
            '#Deltax Paddle 24','#sigma #DeltaX Paddle 24',
            '#Deltax Paddle 25','#sigma #DeltaX Paddle 25',
            '#Deltax Paddle 26','#sigma #DeltaX Paddle 26',
            '#Deltax Paddle 27','#sigma #DeltaX Paddle 27',
            '#Deltax Paddle 28','#sigma #DeltaX Paddle 28',
            '#Deltax Paddle 29','#sigma #DeltaX Paddle 29',
            '#Deltax Paddle 30','#sigma #DeltaX Paddle 30',
            '#Deltax Paddle 31','#sigma #DeltaX Paddle 31',
            '#Deltax Paddle 32','#sigma #DeltaX Paddle 32',
            '#Deltax Paddle 33','#sigma #DeltaX Paddle 33']      # These will be the graph titles
  values = [-1,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None]                                       # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.
  
  histoname = 'TOFTrackDeltaXVsHorizontalPaddle'   # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorMatching/TimeBased/TOFPoint'      # directory containing the histogram
  
  min_counts = 4e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  POS = []
  dPOS = []                       

  for n in range(14,34): 
    
    POSval = -1   # default, meaning unknown
    dPOSval = -1

    h1dnew = h.ProjectionY("pj",n,n)
  
    if (h1dnew.GetEntries() >= 2000):

        h1d = h1dnew;
        if h1dnew.GetEntries()<5000:
          h1d = h1dnew.Rebin(2)

        pos = h1d.GetBinCenter(h1d.GetMaximumBin())
    
        h1d.Fit("gaus", "Q0","R", pos-4., pos+4.)
        f1 = h1d.GetFunction("gaus")
        pos = f1.GetParameter(1)
        r = h1d.Fit("gaus", "Q0","R", pos-4., pos+4.)
        f1 = h1d.GetFunction("gaus")

        if int(r) == 0:
          POSval = f1.GetParameter(1)
          dPOSval = f1.GetParError(1)    
  
    POS.append(POSval)
    dPOS.append(dPOSval)

  status = 1
  values = []
  values.append(status)

  for n in range(0,20):
    values.append(float('%.5f'%(POS[n])))
    values.append(float('%.5f'%(dPOS[n])))
    
  return values       # return array of values, status first


# tof dxpos: Y-position from delta T Vertical plane minus x position from tracking
def tof_1_dypos(rootfile):                      
  
  #print('in tof_1_dypos()...')
  
  # Provide unique graph names. The first must be the status code from this function.
  
  names = ['dy_status',
           'dy14','dy14_err',
           'dy15','dy15_err',
           'dy16','dy16_err',
           'dy17','dy17_err',
           'dy18','dy18_err',
           'dy19','dy19_err',
           'dy20','dy20_err',
           'dy21','dy21_err',
           'dy22','dy22_err',
           'dy23','dy23_err',
           'dy24','dy24_err',
           'dy25','dy25_err',
           'dy26','dy26_err',
           'dy27','dy27_err',
           'dy28','dy28_err',
           'dy29','dy29_err',
           'dy30','dy30_err',
           'dy31','dy31_err',
           'dy32','dy32_err',
           'dy33','dy33_err']  
  titles = ['dy status',
            '#Deltay Paddle 14','#sigma #DeltaY Paddle 14',
            '#Deltay Paddle 15','#sigma #DeltaY Paddle 15',
            '#Deltay Paddle 16','#sigma #DeltaY Paddle 16',
            '#Deltay Paddle 17','#sigma #DeltaY Paddle 17',
            '#Deltay Paddle 18','#sigma #DeltaY Paddle 18',
            '#Deltay Paddle 19','#sigma #DeltaY Paddle 19',
            '#Deltay Paddle 20','#sigma #DeltaY Paddle 20',
            '#Deltay Paddle 21','#sigma #DeltaY Paddle 21',
            '#Deltay Paddle 22','#sigma #DeltaY Paddle 22',
            '#Deltay Paddle 23','#sigma #DeltaY Paddle 23',
            '#Deltay Paddle 24','#sigma #DeltaY Paddle 24',
            '#Deltay Paddle 25','#sigma #DeltaY Paddle 25',
            '#Deltay Paddle 26','#sigma #DeltaY Paddle 26',
            '#Deltay Paddle 27','#sigma #DeltaY Paddle 27',
            '#Deltay Paddle 28','#sigma #DeltaY Paddle 28',
            '#Deltay Paddle 29','#sigma #DeltaY Paddle 29',
            '#Deltay Paddle 30','#sigma #DeltaY Paddle 30',
            '#Deltay Paddle 31','#sigma #DeltaY Paddle 31',
            '#Deltay Paddle 32','#sigma #DeltaY Paddle 32',
            '#Deltay Paddle 33','#sigma #DeltaY Paddle 33']      # These will be the graph titles
  values = [-1,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None,
            None, None]                                       # Default values, keep status as -1

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.
  
  histoname = 'TOFTrackDeltaYVsVerticalPaddle'   # monitoring histogram to check
  dirname = '/Independent/Hist_DetectorMatching/TimeBased/TOFPoint'      # directory containing the histogram
  
  min_counts = 4e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  # code to check the histogram and find the status values
  POS = []
  dPOS = []                       

  for n in range(14,34):

    POSval = -1  # default, unknown
    dPOSval = -1

    h1dnew = h.ProjectionY("pj",n,n)
    
    if (h1dnew.GetEntries() >= 2000):

        h1d = h1dnew;
        if h1dnew.GetEntries()<5000:
          h1d = h1dnew.Rebin(2)
    
        pos = h1d.GetBinCenter(h1d.GetMaximumBin())
        
        h1d.Fit("gaus", "Q0","R", pos-4., pos+4.)
        f1 = h1d.GetFunction("gaus")
        pos = f1.GetParameter(1)
        r = h1d.Fit("gaus", "Q0","R", pos-4., pos+4.)
        f1 = h1d.GetFunction("gaus");
  
        if int(r) == 0:
          POSval = f1.GetParameter(1)
          dPOSval = f1.GetParError(1)    

    POS.append(POSval)
    dPOS.append(dPOSval)
      
  status = 1
  values = []
  values.append(status)

  for n in range(0,20):
    values.append(float('%.5f'%(POS[n])))
    values.append(float('%.5f'%(dPOS[n])))
    
  return values       # return array of values, status first


