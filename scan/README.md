==How it works==

* scan.py is the control script that calls the contributed/detector modules and compiles graphs from their results.
* cdc.py, cdc_cpp.py etc are some of the contributed/detector modules that inspect monitoring histograms and return metrics.

_scan.py_ has provision for a module to be specific to a particular run period (eg _cdc\_cpp.py_ is for CPP/NPP data).

The contributed modules contain several functions:
* init
* check
* histogram-inspection functions, one for each histogram to be inspected.  

The functions _init_ and _check_ call all of the histogram-inspection functions.  

_scan.py_ first calls each detector module's _init_ function.  
This calls each of the histogram-inspection functions (without a file pointer) to obtain and return lists of the names, titles and default status (-1) of whatever quantities are to be graphed.   

It then loops through the directory of root files, opening each one and passing a file pointer to the modules's _check_ function. 
_check_ calls each of the histogram-inspection functions.  

When the histogram-inspection functions are called by _check_ (with a valid pointer to the opened root file), 
they extract the required quantities from the histogram, assess them, and return a list of the quantities and associated status values.  The status values should be 1 (good), 0 (bad) or -1 (undefined).  If there is no real good or bad range for a quantity, its status should be set to 1 (good). 

The quantities and their assigned status ratings are used to compile root graphs which will appear on the module's web page.  
A combined status graph for each  module is concocted from the status ratings of all of that module's quantities.  
The combined status graph is shown on the module's page and also on the overview page.  
An overall status is derived from all of these combined status values and shown as 'readiness' on the overview page. 

The overvew web page contains links to the root file containing all of the graphs and a csv file containing all of the quantities used to create the graphs.  The csv file might be useful for recalibration.
