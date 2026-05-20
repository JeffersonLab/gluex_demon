from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1,TH1I

# Define the page name
PAGENAME = 'FDC_t0'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [resids]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.



def resids(rootfile) :

  names = ['t0_status']  
  titles = ['FDC t0']
  values = [-1]
  png = ['FDC_resi']

  for x in range (1,25) :
    names.append('L_plane_' + str(x) + '_mg')
    names.append('L_plane_' + str(x) + '_mg_err')
    titles.append('Plane ' + str(x) + " residuals")
    titles.append('Plane ' + str(x) + " residuals width, left")
    values.extend([None,None])

  for x in range (1,25) :
    names.append('R_plane_' + str(x) + '_mg')
    names.append('R_plane_' + str(x) + '_mg_err')
    titles.append('Plane ' + str(x) + " residuals, right")
    titles.append('Plane ' + str(x) + " residuals width, right")
    values.extend([None,None])
    
  
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  status = 1

  for x in range (1,25) :

    dirname = "/TrackingPulls/FDCPulls_Plane%02d"%(x)
    min_counts = 1000
    ix = 4*(x-1) + 1    # array index

    # Left
    
    histoname = 'wire_residual_left'
  
    h = get_histo(rootfile, dirname, histoname, min_counts)

    if (h) :
      values[ix+1] = float('%.4f'%(h.GetRMS()))
      
      max = h.GetBinCenter(h.GetMaximumBin())
      fitresult = h.Fit("gaus","SQ0","",max-0.01,max+0.01)

      if int(fitresult) == 0 :
        mean = fitresult.Parameter(1)
        values[ix] = float('%.4f'%(mean))
      else :
        status = -1
        
    else :
      status = -1

    # Right        

    histoname = 'wire_residual_right'
  
    h = get_histo(rootfile, dirname, histoname, min_counts)
    
    if (h) :
      values[ix+3] = float('%.4f'%(h.GetRMS()))      

      max = h.GetBinCenter(h.GetMaximumBin())
      fitresult = h.Fit("gaus","SQ0","",max-0.01,max+0.01)

      if int(fitresult) == 0 :
        mean = fitresult.Parameter(1)
        values[ix+2] = float('%.4f'%(mean))
      else :
        status = -1
        
    else :
      status = -1
        

  values[0] = status
  
  return values       # return array of values, status first
