from utils import get_histo     # demon's helper functions
from ROOT import gROOT, TF1

# Define the page name
PAGENAME = 'FDC'

# Provide the names of the custom functions in this module
def declare_functions() : 
  list_of_functions = [fdc_efficiency, fdc_dedxpos, fdc_dedxneg]
  return list_of_functions


# Custom functions follow.
# Quantities that could not be evaluated (not enough data/bad fit etc) should be assigned a value of None and status -1.
# Quantities that were evaluated and compared with limits should have status code 1 if acceptable and 0 if not.
# Quantities that were evaluated but not compared with limits should have a status code of 1.


def fdc_dedxpos(rootfile) :

  titles = ['q+ dE/dx status','FDC q+ dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q+ dE/dx resolution at 1.5 GeV/c']
  names = ['dedxpos_status','dedxposmean','dedxposres']
  values = [-1, None, None]
  png = ['HistMacro_Tracking_p3']
  
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5
  
  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q+'

  min_counts = 5e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  pcut = 1.5 #;    // draw cut through histo at p=1.5 GeV/c
  pbin = h.GetXaxis().FindBin(pcut)
  p = h.ProjectionY("p1",pbin,pbin)

  if p.GetEntries() < 1000 :
    return values 

  p.GetXaxis().SetRangeUser(0,5)

  g = TF1('g','gaus',0,12)

  fitstat = p.Fit('g','0qwes')
  
  #print 'fit status ',fitstat.IsValid(), fitstat.Status()

  if int(fitstat) == 0:
    mean = g.GetParameter(1)
    res = 2.0*g.GetParameter(2)/mean

    status = 1
    if mean < dedxmin or mean > dedxmax:
      status=0
    if res < dedxresmin or res > dedxresmax:
      status=0

    values = [status, float('%.5f'%(mean)), float('%.5f'%(res)) ]
  
  return values


def fdc_dedxneg(rootfile) :

  titles = ['q- dE/dx status','FDC q- dE/dx mean at 1.5 GeV/c (keV/cm)','FDC q- dE/dx resolution at 1.5 GeV/c']
  names = ['dedxneg_status','dedxnegmean','dedxnegres']
  values = [-1, None, None]
  png = ['HistMacro_Tracking_p3']  
  
  if not rootfile :  # called by init function
    return [names, titles, values, png]

  dedxmin = 1.5 # 1.9
  dedxmax = 2.5 #2.0
  dedxresmin = 0.2# 0.3
  dedxresmax = 0.5
  
  dirname = '/Independent/Hist_DetectorPID/FDC'
  histoname = 'dEdXVsP_q-'

  min_counts = 5e4

  h = get_histo(rootfile, dirname, histoname, min_counts)

  if (not h) :
    return values

  pcut = 1.5 #;    // draw cut through histo at p=1.5 GeV/c
  pbin = h.GetXaxis().FindBin(pcut)
  p = h.ProjectionY("p1",pbin,pbin)

  if p.GetEntries() < 1000 :
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


def fdc_efficiency(rootfile) :

  titles = ['Average wire efficiency status']
  names = ['eff_status'] #, 'eff0_efficiency_mg', 'eff0_efficiency_mg_err', 'eff2_efficiency_mg', 'eff2_efficiency_mg_err', 'eff4_efficiency_mg', 'eff4_efficiency_mg_err', 'eff5_efficiency_mg', 'eff5_efficiency_mg_err']
  values = [-1]
  png = ['']  

  for x in range(1,25):
    titles.append('Average wire efficiency [Plane ' + str(x) + ']')
    names.append('plane_' + str(x) + '_eff_mg')
    values.append(None)
    png.append('')

  if not rootfile :  # called by init function
    return [names, titles, values, png]
    
  dirname = '/FDC_Efficiency/FDC_View'

  status = 1

  min_counts = 0
  
  for x in range(1,25):
    
    histoname1 = 'fdc_wire_expected_cell[' + str(x) + ']'
    histoname2 = 'fdc_wire_measured_cell[' + str(x) + ']'

    h1 = get_histo(rootfile, dirname, histoname1, min_counts)
    h2 = get_histo(rootfile, dirname, histoname2, min_counts)    
    
    if (not h1 or not h2) :   
        continue

    h2.Divide(h1)  

    eff = h2.Integral()/h2.GetNbinsX()

    values[x] = float('%.3f'%(eff))
    
    if eff < 0.8:
      status = 0

  values[0] = status    
      
  return values




