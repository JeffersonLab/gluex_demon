# Detector monitoring histogram scanning script - calls contributed modules to inspect histograms
#
# To add a new detector monitoring module, 
#   import it
#   add it to the lists of modules, modules_def etc
#
# Run this script with arguments -r Year-Month -v Version and (optionally) a non-standard monitoring histogram directory.
# eg python3.6 scan.py -r 2022-05 -v 23 cpphists
#
# It should create 4 files, where X is like 2022-05_ver23
#
#   filename_graphs = 'monitoring_graphs_X.root'   # root file of graphs
#   filename_csv = 'monitoring_data_X.csv'         # csv file of metrics
#   filename_badruns = 'monitoring_badruns_X.txt'  # list of runs with overall status not good
#   filename_pagenames = 'monitoring_pagenames_X.txt' # list of module page titles and graphs
#

import sys
import os
import subprocess
import re
import csv

script = sys.argv.pop(0)
nargs = len(sys.argv)

if nargs<4 or nargs>5 or sys.argv[0] == "-h" or sys.argv[0] == "--h" or sys.argv[0] == "--help":
    exit("This script scans GlueX/Hall D detector monitoring histograms to create graphs.\nUsage: python3.6 scan.py -r Year-Month -v VersionNumber [path_to_monitoring_histogram_directory]\n    eg python3.6 scan.py -r 2022-05 -v 06\nThe histogram directory is optional if it is the usual one.")

# detector monitoring modules
import cdc 
import cdc_cpp   
import timing
import timing_MD
import tof_1

modules_def = [cdc,timing,timing_MD,tof_1]       # default list of modules
modules_cpp = [cdc_cpp,timing,timing_MD,tof_1]   # modules for CPP

testing = 0  # stop after <runlimit> files, print diagnostics
runlimit = 10 # process this number of runs if testing=1

RunPeriod=""
VersionNumber=""
histdir = ""

while len(sys.argv) > 0 :

    x = sys.argv.pop(0)
  
    if x == "-r" :
        RunPeriod = sys.argv.pop(0)
  
    elif x == "-v" :
        VersionNumber = sys.argv.pop(0)
  
    else :
        histdir = x
  
if RunPeriod == "" :
    exit('Please supply Run Period year and month, eg 2022-05')
if VersionNumber == "" : 
    exit('Please supply Monitoring Version Number, eg 06')

if histdir == "" : 
    histdir = '/work/halld/data_monitoring/RunPeriod-' + RunPeriod + '/mon_ver' + VersionNumber + '/rootfiles'


print('Looking for monitoring histograms inside directory',histdir)

# Make sure the monitoring histogram directory exists

if not os.path.exists(histdir):
    exit('Cannot find ' + histdir + '\n  It might have been moved from /work/halld/data_monitoring to /cache/halld/offline_monitoring.')


# import ROOT now (after passing early checks), as the import is slow

from ROOT import TFile, TGraph
from ROOT import gROOT
gROOT.SetBatch(True)


# set up list of modules to run for this run period
modules=[]
run_module=[]

if RunPeriod == '2022-05' :
    modules = modules_cpp
else :
    modules = modules_def

for x in modules:
    run_module.append(True)


# prepare output files

tag = '_' + RunPeriod + '_ver' + VersionNumber

filename_graphs = 'monitoring_graphs' + tag + '.root'      # graphs
filename_csv = 'monitoring_data' + tag + '.csv'            # graph data as one big csv file
filename_badruns = 'monitoring_badruns' + tag + '.txt'     # list of runs with overall status not good
filename_pagenames = 'monitoring_pagenames' + tag + '.txt' # list of module page titles and graphs

# remove old output files

for thisfile in [ filename_graphs, filename_csv, filename_badruns ] :
    try:
        os.remove(thisfile)
    except OSError:
        pass


# Make list of filenames

histofilelist = subprocess.check_output(["ls", histdir], universal_newlines=True).splitlines()

if len(histofilelist) == 0:
    exit("No monitoring files found")




max_errcount = len(modules) + 20 #set larger than the number of modules, suppress messages 
max_file_errcount = 20 # for file errors, filenames

err_mismatches = False  # set true if there are value array length mismatches

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

print('Initalising')

for imod in range(len(modules)) : 

    if run_module[imod] :  
        try: 
    
          arrays = modules[imod].init() 
        
        except:
    
          print('ERROR Init module %s failed' % (modules[imod].__name__) )   # don't suppress
          run_module[imod] = False

          print('Calling it again, to show the error')
          arrays = modules[imod].init()

        else:

          if len(arrays[1]) != len(arrays[2]) or len(arrays[1]) != len(arrays[3]):
              print('ERROR Init module %s array length mismatch ' % (modules[imod].__name__) )  # don't suppress
              run_module[imod] = False
          else : 
              pagenames.append(arrays[0])   # page title
              gcount.append(len(arrays[1]))  # number of graphs for this page
              gnames.extend(arrays[1])  # 1D list
              gtitles.extend(arrays[2])
              defaults.append(arrays[3]) # list of lists

              if testing:
                  print('\nInitialisation for module %s' % (modules[imod].__name__) )
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

print('Processing histograms')

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

            if testing:
                print('Calling module %s' % (active_modules[imod].__name__) )

            try: 

                newdata = active_modules[imod].check(run, rootfile)  # run, root file ptr

            except:
                if errcount < max_errcount:
                    print('ERROR run %i module %s ' % (run, active_modules[imod].__name__) )  

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
                        print('ERROR run %i values array length mismatch from module %s' % (run, active_modules[imod].__name__) ) 
                    err_mismatches = True
                    errcount = errcount + 1

                    newdata = defaults[imod]


                elif len(newdata) != len(defaults[imod]) :

                    if errcount < max_errcount+5 :  # make sure some get printed
                        print('ERROR run %i values array length mismatch from module %s' % (run, active_modules[imod].__name__) ) 
                    err_mismatches = True
                    errcount = errcount + 1

                    temparray = newdata
                    temparray.extend(defaults[imod])

                    newdata = []
                    for i in range(len(defaults[imod])) :
                        newdata.append(temparray[i])
                

            thisrun_values.extend(newdata)        # extend the 2D list adding columns
            thisrun_status.append(newdata[0])     # append the 1D list adding a row

            if testing: 
                print('\nData from module %s:' % (active_modules[imod].__name__) )
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

if len(gnames) == 0:
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

 
