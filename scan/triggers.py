from utils import get_histo     # demon's helper functions
from ROOT import gROOT

#
# This module contains two control functions, 'init' and 'check', and the custom functions which inspect the histograms (one custom function for each histogram).
#
# 'init' and 'check' call the custom functions.  'init' returns graph names and titles. 'check' returns the numbers to be graphed.
#


def init() : 

  pagename = 'Triggers'          # Title for the page of graphs.  Best avoid spaces.

  # These lists are the headers for the overall status summary for this module
  # Do not add any more list elements here

  names = ['triggers_status']    # Graph name, triggers_status 
  titles = ['triggers status']   # Graph title
  values = [-1]                 # Default status, keep it at -1
  
  # This is the list of custom functions, called with one argument: False

  t = triggers(False)  # return names, titles, values



  for thing in [ t ] :   # loop through the arrays returned from each function

    names.extend(thing[0])
    titles.extend(thing[1])
    values.extend(thing[2])

  return [pagename,names,titles,values]



def check(run, rootfile) :

  # This calls the custom functions to get an array of metrics, concatenates those into one list, adds the overall status and returns the list

  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)

  # List of custom functions, called with argument rootfile
  # Each function checks one histogram and returns a list, its status code followed by the values to be graphed.
  # Add or remove custom functions from this list

  t = triggers(rootfile)

  # This finds the overall status, setting it to the min value of each histogram status


  statuslist = []
  for thing in [ t ] :         # Add or remove the list names assigned above.  
    statuslist.append(thing[0])   # status is the first value in the array

  status = min(statuslist)

  # add overall status to the start of the lists before concatenating & returning.

  allvals = [status]

  for thing in [ t ] :  # Add or remove the list names assigned above.  
    allvals.extend(thing) 

  return allvals
 
'percent_bcal_trig_mg'
'bcal_trigratio_mg'

def triggers(rootfile) : 

  names = ['trig_status','main_trig','bcal_trig','bcal_trigratio_mg','ps_trig','ps_trigratio_mg','random_trig','random_trigratio_mg']
  titles = ['tr_status','Main triggers','BCAL triggers','BCAL triggers/Main triggers (%)','PS triggers','PS triggers/Main triggers (%)','Random triggers','Random triggers/Main triggers (%)']
  values = [-1, None, None, None, None, None, None, None ]

  if not rootfile :  # called by init function
    return [names, titles, values]

  # The following code finds the histogram, extracts metrics, checks them against the limits provided, assigns a status code and then returns a list of status code followed by the metrics. 
  # Status codes are 1 (good), 0 (bad) or -1 (don't know/file problem/not enough data/some other error)
  # If you just want to plot a metric without comparing it to limits, set its status code to 1, so that it doesn't make the overall status look bad.
        
  # Main Trigger BCAL+FCAL: GTP Bit 1
  # BCAL Trigger: GTP Bit 3            
  # PS Trigger: GTP Bit 4
  # Random Trigger: FP Bit 12		
  
  # The histograms are in one place for the REST production files and another for monitoring files.

  test=rootfile.GetDirectory('/L1')
  
  if test :
    dirname = '/L1'
    histoname = 'trig_bit'
    histoname2 = 'trig_bit_fp'
  else:
    dirname = '/highlevel'
    histoname = 'L1bits_gtp'
    histoname2 = 'L1bits_fp'
    
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
            

  status = 1

  if nmain > 0 :
    bcalpercent = 100*nbcal/nmain
    bcalpercent = float('%.1f'%(bcalpercent))
    pspercent = 100*nps/nmain
    pspercent = float('%.1f'%(pspercent))    
    randompercent = 100*nrandom/nmain
    randompercent = float('%.3f'%(randompercent))    
  else :
    bcalpercent = None
    pspercent = None
    randompercent = None

  if nmain == 0 or nbcal == 0 or nps == 0 or nrandom == 0:
    status = 0
  
  values = [status, int(nmain), int(nbcal), bcalpercent, int(nps), pspercent, int(nrandom), randompercent ]

  return values       # return array of values, status first
  



