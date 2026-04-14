from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'EVIO'

# Provide the names of the custom function(s) in this module
def declare_functions() : 
  list_of_functions = [badhits]
  return list_of_functions

def badhits(rootfile) :


    titles = ['EVIO status', 'Source of errors (0:swap, 1:TSscaler, 2:f250 scaler, 3:EPICS, 4:BOR, 5:Trigger, 10+:ROCid)','#2','#3', '#4']
    names = ['badhits_status', '1_roc_mg', '2_roc_mg', '3_roc_mg', '4_roc_mg']
    values = default_values(names)
    png = ['HistMacro_bad_hits']    


    if not rootfile :  # called by init function
        return [names, titles, values, png]

    dirname = '/bad_hits'
    histoname = 'roc'
    
    min_counts = 0 # minimum counts required, default 100    
    h = get_histo(rootfile, dirname, histoname, min_counts)

    if (not h) :
        return values

    if h.GetEntries() == 0 :    # good - no errors
      values[0] = 1
      return values


    
    counts = {}

    for i in range(1, 1+ h.GetNbinsX()) :
      n = int(h.GetBinContent(i))
      if n>0 :
         counts.update( { n : i})

    values = [0]

    for x in sorted(counts, reverse=True) :
      values.append(counts[x])

    for i in range(len(counts)+1,5) :
      values.append(None)

    return values

