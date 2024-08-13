
# To test a new module, 
#   add it to the list of imports
#   add it to the list modules = []
#   switch it to True in run_module 
#
# Run this script with one argument, the monitoring histogram directory
# eg python test_new_module.py /work/halld/data_monitoring/RunPeriod-2022-05/mon_ver24/rootfiles/
#
# It should create 4 files:
#   filename_graphs = 'test_new_module_graphs.root'   # root file of graphs
#   filename_csv = 'test_new_module_data.csv'         # csv file of metrics
#   filename_badruns = 'test_new_module_badruns.txt'  # list of runs with overall status not good
#   filename_pagenames = 'test_new_module_pagenames.txt' # list of module page titles and graphs
#
# To test over more runs, adjust the variable runlimit

import os
import sys
import subprocess
import glob
import re
import csv

from ROOT import TFile, TGraph
from ROOT import gROOT
gROOT.SetBatch(True)

import new_module,rho        # import new module 

modules = [new_module,rho]   # list of function names
run_module = [True,True]      # call the function if true

testing = 1  # stop after <runlimit> files, print diagnostics
runlimit = 2 # process this number of runs if testing=1

max_errcount = 10 #set larger than the number of modules, suppress messages 
max_file_errcount = 10 # for file errors, filenames
err_mismatches = False  # set this true if there are value array length mismatches

script = sys.argv.pop(0)
nargs = len(sys.argv)

if nargs == 0 or nargs > 1 or sys.argv[0] == "-h" or sys.argv[0] == "--help":
  exit("Usage: python test_new_module.py path_to_monitoring_histogram_directory")

histdir = sys.argv.pop(0)
nargs -= 1
#histdir = "/cache/halld/offline_monitoring/RunPeriod-2021-08/ver08/hists/hists_merged"   #path to find the root files

filename_graphs = 'test_new_module_graphs.root'
filename_csv = 'test_new_module_data.csv'
filename_badruns = 'test_new_module_badruns.txt'
filename_pagenames = 'test_new_module_pagenames.txt' # list of module page titles and graphs

# remove old output files

for thisfile in [ filename_graphs, filename_csv, filename_badruns ] :
    try:
        os.remove(thisfile)
    except OSError:
        pass


# Make sure the monitoring histogram directory exists

if not os.path.isdir(histdir):
  exit("Cannot find directory " + histdir)

# Make list of filenames

cwd = os.getcwd()
os.chdir(histdir)
histofilelist = sorted(glob.glob('*.root'))
os.chdir(cwd)

if len(histofilelist) == 0:
  exit("No monitoring files found")


pagenames = []       # title for each module's set of graphs, eg "CDC","FDC", etc
gcount = []          # number of graphs for each module
gnames = ['run']            # graph names eg cdc_dedx.  Start the list with run.
gtitles = ['Run number']    # graph titles 

allruns_values = []   # giant array of all metrics
combined_status = []  # status indicator for all metrics for each run
readiness = []        # percent readiness of the run (100% if every metric's status =1)

firstrun = True # set false after processing one file 
runcount = 0    # number of runs processed so far
errcount = 0    # count of module errors
file_errcount = 0   # count of file errors

badruns = []    # list of problem runs

# run the init functions to get the graph names, titles and default values from the modules
# defaults are used later if the module fails for a run

defaults = []



for imod in range(len(modules)) : 

    if run_module[imod] :  
        try: 
    
          arrays = modules[imod].init() 
        
        except:
    
          print('ERROR Init %s failed' % (str(modules[imod])) )   # don't suppress
          run_module[imod] = False

          print('Calling it again, to show the error')
          arrays = modules[imod].init()

        else:

          if len(arrays[1]) != len(arrays[2]) or len(arrays[1]) != len(arrays[3]):
              print('ERROR Init %s array length mismatch ' % (str(modules[imod])) )  # don't suppress
              run_module[imod] = False
          else : 
              pagenames.append(arrays[0])   # page title
              gcount.append(len(arrays[1]))  # number of graphs for this page
              gnames.extend(arrays[1])  # 1D list
              gtitles.extend(arrays[2])
              defaults.append(arrays[3]) # list of lists

              if testing:
                  print('\nInitialisation for %s' % str(modules[imod]) )
                  print('Page name:')
                  print('%s'%(arrays[0]))
                  print('Graph names:')
                  print('%s'%(arrays[1]))
                  print('Graph titles:')
                  print('%s'%(arrays[2]))
                  print('Defaults (array of -1) :')
                  print('%s'%(arrays[3]))


# add overall readiness to the end of the names & titles 
gnames.append('readiness')
gtitles.append('Run readiness')


# make a list of the active modules, then run over these from now on
active_modules=[]

for imod in range(len(modules)) : 
    if run_module[imod] :  
       active_modules.append(modules[imod])



# loop through the runs, running the module check functions to gather status and other metrics


for filename in histofilelist:

    if os.path.splitext(filename)[1] == '.root' :

        fullfilepath = histdir + "/" + filename
    
        findrunnum = re.findall('\d+',filename)   #makes a list of numbers found in the filename
    
        if len(findrunnum) == 0:
            run = 0
            if file_errcount < max_file_errcount:
                print('ERROR Cannot find run number in filename %s' % (fullfilepath) )
            file_errcount = file_errcount + 1
            continue
        else:
            run = int(findrunnum[0])

    
        try:
            rootfile = TFile(fullfilepath)
        except :
            if file_errcount < max_file_errcount:
                print('ERROR Cannot open %s' % (fullfilepath))
            file_errcount = file_errcount + 1
            continue
            

        if testing : 
            print('\nRun %i - processing %s\n' % (run,filename))


        thisrun_values = [run]   # collect all the returned values
        thisrun_status = []      # collect the returned status values, use them later to create a combined status


        for imod in range(len(active_modules)) :

            if not run_module[imod] :  
               continue

            if testing:
                print('Calling %s' % (str(active_modules[imod])) )

            try: 

                newdata = active_modules[imod].check(run, rootfile)  # run, root file ptr

            except:
                if errcount < max_errcount:
                    print('ERROR run %i %s ' % (run, str(active_modules[imod])) )  

                print('Calling the module again, to show the error')
                newdata = active_modules[imod].check(run, rootfile)  # run, root file ptr

                errcount = errcount + 1

                newdata = defaults[imod] 

            else:

                # make sure the array is the correct length
                # if necessary, pad with defaults or truncate the array
                # so that the other modules results are not disturbed

                if not isinstance(newdata,list) :
                    if errcount < max_errcount+5 :  # make sure some get printed
                        print('ERROR run %i values array length mismatch from %s module ' % (run, str(active_modules[imod])) ) 
                    err_mismatches = True
                    errcount = errcount + 1

                    newdata = defaults[imod]


                elif len(newdata) != len(defaults[imod]) :

                    if errcount < max_errcount+5 :  # make sure some get printed
                        print('ERROR run %i values array length mismatch from %s module ' % (run, str(active_modules[imod])) ) 
                    err_mismatches = True
                    errcount = errcount + 1

                    temparray = newdata
                    temparray.extend(defaults[imod])

                    newdata = []
                    for i in range(len(defaults[imod])) :
                        newdata.append(temparray[i])
                

            thisrun_values.extend(newdata)        # extend the 2D list adding columns
            thisrun_status.append(newdata[1])     # append the 1D list adding a row

            if testing: 
                print('\nData from %s:' % (str(active_modules[imod])) )
                print('%s'%(newdata))



        # after running all histogram checking modules
        # make a combined status value 
        min_status = min(thisrun_status)

        combined_status.append(min_status)  # combined status value for all metrics is the lowest
        

        # sum up number of not-good metrics
        badcount = 0
        
        for status in thisrun_status :
            if (status != 1):
                badcount = badcount + 1
        
        readiness = 100.0*(len(thisrun_status) - badcount)/len(thisrun_status)

        if badcount > 0 :
           badruns.append(run)
        
        thisrun_values.append(readiness)

        # append list of values from this run to the collection
        allruns_values.append(thisrun_values)


        if testing:
            if err_mismatches :
                mismatchwarning = ' There were array length mismatches - check these!'
            else : 
                mismatchwarning = ''

            print('\nReadiness: %.1f %% %s\n' % (readiness, mismatchwarning) )


        runcount = runcount + 1
        if testing == 1 and runcount == runlimit:
            break


# skip the post-processing if all modules failed!

if len(gnames) == 1:
  exit('No runs were processed properly')




# make TGraphs file

from array import array

f = TFile(filename_graphs,'RECREATE')
        
nruns = len(allruns_values)  # number of runs

for igraph in range(1,len(gnames)) : # skip element 0, run number

  #print igraph,gnames[igraph],gtitles[igraph]

  x, y = array( 'd' ), array( 'd' )  

  for i in range(nruns) :
    x.append(allruns_values[i][0])
    y.append(allruns_values[i][igraph]) 
    
  gr = TGraph( nruns, x, y )
  gr.SetName( gnames[igraph] )
  gr.SetTitle( gtitles[igraph] )
  gr.GetXaxis().SetTitle( 'Run number' )
  gr.GetYaxis().SetTitle( gtitles[igraph] )
  gr.SetMarkerStyle( 21 )
  gr.Write()

  if testing:
      print('Created graph %s' % (gnames[igraph]) )

f.Close()
   

# write out text file in csv

f = open(filename_csv,"w")
writer = csv.writer(f)

writer.writerow(gnames)

for i in range(nruns):
  writer.writerow(allruns_values[i])

f.close()

if testing:
    print('Results saved to %s' % (filename_csv) )


# write out list of page titles and their graphs 
 
f = open(filename_pagenames,"w")
writer = csv.writer(f)

gstart=1

for i in range(len(pagenames)):
  newlist = []
  newlist.append(pagenames[i])
  newlist.append(gcount[i])

  for j in range(gstart,gstart+gcount[i]) : # use gcount to find the page titles to save
    newlist.append(gnames[j])
  
  writer.writerow(newlist)

  gstart = gstart + gcount[i]

f.close()

if testing:
    print('List of page titles and graph names saved to %s' % (filename_pagenames) )



# list of bad runs

if len(badruns) > 0 : 
    f = open(filename_badruns,"w")

    for x in badruns:
        f.write(str(x)+'\n')

    f.close()

    if testing:
        print('Bad runs listed in %s' % (filename_badruns) )

 
