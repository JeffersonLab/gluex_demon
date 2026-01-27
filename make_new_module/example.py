from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'EXAMPLE'

# Provide the names of the custom function(s) in this module
def declare_functions() : 
  list_of_functions = [example_graph, example_graph_with_errors, example_multigraph]
  return list_of_functions

#
# The custom functions must return 3 arrays describing the graphs to be built: titles, names and values.
# Titles may include spaces and character codes, eg #rho.
# Names must be valid root graph names (no spaces), and might include special suffixes described later.
#
# The first graph must be a status (quality indicator) graph for the custom function.
#
# Scan.py calls each function in this module once (with rootfile=False) to collect the graph titles and names,
# and then again for each root file, to get the values for that run.
#
# Quantities that could not be obtained (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were obtained and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were obtained but not compared with limits should have a status code of 1.
#
# An overall status code for the module is created automatically by combining the status value from each custom function.
# The status graphs from each function will be combined automatically in a multigraph for the module.
#
# TGraphErrors are defined by naming a pair of graphs like (for example) xx and xx_err, where xx_err is the std dev
# eg mass and mass_err
#
# TMultiGraphs are defined by giving the set of graph names the suffix _mmm_mg where mmm is the name of the multigraph
# eg doca1_efficiency_mg and doca2_efficiency_mg would appear on the multigraph named efficiency_mg
# doca1_efficiency_mg and doca1_efficiency_mg_err would appear as a TGraphErrors on the multigraph efficiency_mg
#
# This shows the minimum content required for a custom function:
#
#def minimalist_custom_function(rootfile):
#
#    titles = ['Status','Thing']
#    names = ['status','thing']
#    values = default_values(names)  # defaults are -1 for status and None for all other values
#
#    if not rootfile :  # called by init function
#        return [names, titles, values]
#
#    # code to read the histogram and extract values goes here    
#    # values = [mystatus, myvalue]
#
#    return values
      

#-------------------------------------------------------------------------------------------------------------------------            

def example_graph(rootfile):

    print('in function example_graph()')
  
    titles = ['Bin 1 efficiency status','Bin 1 efficiency']
    names = ['bin1eff_status','bin1eff']
    values = default_values(names)  # defaults are -1 for status and None for all other values

    if not rootfile :  # called by init function
        return [names, titles, values]

    dirname = '/CDC_Efficiency/Online'
    histoname = 'Efficiency Vs DOCA'

    min_counts = 50 # minimum counts required, default 100
    h = get_histo(rootfile, dirname, histoname, min_counts)  

    if (not h) :
        return values

    eff = h.GetBinContent(1)
    
    llim = 0.9
    status = 1

    if eff < llim :
        status = 0

    values = [status, float('%.3f'%(eff))]

    return values

#-------------------------------------------------------------------------------------------------------------------------            



def example_graph_with_errors(rootfile):

    print('in function example_graph_with_errors()')
  
    titles = ['Mean efficiency status','Mean efficiency','Std dev efficiency']
    names = ['meaneff_status','meaneff','meaneff_err']
    values = default_values(names)  # defaults are -1 for status and None for all other values

    if not rootfile :  # called by init function
        return [names, titles, values]
              
    dirname = '/CDC_Efficiency/Online'
    histoname = 'Efficiency Vs DOCA'

    min_counts = 1000 # minimum counts required, default 100    
    h = get_histo(rootfile, dirname, histoname, min_counts) 

    if (not h) :
        return values

    meaneff = h.GetMean()
    rms = h.GetRMS()
    status = 1

    llim = 0.3 
    if meaneff < llim :
        status = 0

    values = [status, float('%.3f'%(meaneff)), float('%.3f'%(rms))]

    return values

#-------------------------------------------------------------------------------------------------------------------------            
  
def example_multigraph(rootfile) :

    print('in function example_multigraph()')
                          
    titles = ['Efficiency status', 'CDC hit efficiency at 0.04mm', 'Std dev 0.04mm', 'CDC hit efficiency at 5mm', 'Std dev 5mm', 'CDC hit efficiency at 6.4mm', 'Std dev 6.4mm']
    names = ['eff_status', 'eff0_hitefficiency_mg', 'eff0_hitefficiency_mg_err', 'eff5_hitefficiency_mg', 'eff5_hitefficiency_mg_err', 'eff6_hitefficiency_mg', 'eff6_hitefficiency_mg_err']
    values = default_values(names)

    if not rootfile :  # called by init function
        return [names, titles, values]

    e0min = 0.97
    e5min = 0.96
    e6min = 0.89

    dirname = '/CDC_Efficiency/Online'
    histoname = 'Efficiency Vs DOCA'
    
    min_counts = 1000 # minimum counts required, default 100    
    h = get_histo(rootfile, dirname, histoname, min_counts)

    if (not h) :
        return values

    e0 = h.GetBinContent(1) # // 0.04 mm 
    e5 = h.GetBinContent(65) # // 5 mm 
    e6 = h.GetBinContent(83) # // 6.4 mm

    e0err = h.GetBinError(1)*100
    e5err = h.GetBinError(65)*100
    e6err = h.GetBinError(83)*100    
    
    status = 1

    if e0 < e0min or e5 < e5min or e6 < e6min:
        status = 0

    values = [status, float('%.3f'%(e0)), float('%.3f'%(e0err)),float('%.3f'%(e5)), float('%.3f'%(e5err)), float('%.3f'%(e6)), float('%.3f'%(e6err))]

    return values

