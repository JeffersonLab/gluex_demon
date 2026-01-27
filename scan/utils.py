from ROOT import gROOT

#-------------------------------------------------------------------------------------------------------------------------

def init(modulename) : 

  # These lists are the headers for the overall status summary for the module

  pagename = modulename.PAGENAME
  
  names = [pagename.lower() + '_status']  # Graph name
  titles = [pagename + ' status']                 # Graph title
  values = [-1]                                          # Default to unknown
  
  list_of_functions = modulename.declare_functions()

  for func in list_of_functions :
    arr = func(False)
    names.extend(arr[0])
    titles.extend(arr[1])
    values.extend(arr[2])
    
  return [pagename, names, titles, values]

#-------------------------------------------------------------------------------------------------------------------------

def check(modulename, run, rootfile) :

# Call the custom functions to get an array of metrics, concatenate those into one list, prepend with the overall status

  list_of_functions = modulename.declare_functions()
  statuslist = []
  allvals = []
  
  for func in list_of_functions :
    arr = func(rootfile)

    statuslist.append(arr[0])
    allvals.extend(arr)

  status = min(statuslist)

  return [status] + allvals

#-------------------------------------------------------------------------------------------------------------------------

def get_histo(rootfile, dirname, histoname, min_counts=100) :

  test = rootfile.GetDirectory(dirname) 

  # file pointer contains tobj if dir exists, set false if not

  if (not test):
    #print('Could not find ' + dirname)
    return False

  rootfile.cd(dirname)

  h = gROOT.FindObject(histoname)

  if (not h) :
    #print('Could not find ' + histoname)
    return False

  if h.GetEntries() < min_counts :
    return False

  return h

#-------------------------------------------------------------------------------------------------------------------------

def default_values(names) :
  defaults = []
  for name in names :
    if name.endswith('_status') :
      defaults.append(-1)
    else :
      defaults.append(None)
      
  return defaults

