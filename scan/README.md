# How it works

* scan.py is the control script that calls the contributed/detector modules and compiles graphs from their results.
* cdc.py, cdc_cpp.py etc are some of the contributed/detector modules that inspect monitoring histograms and return metrics.
* run_demon.sh is a script to run scan.py and copy the output into halldweb.
* extract_col.py extracts the run numbers and the named values specified from the output csv file. 
  
_scan.py_ has provision for a module to be specific to a particular run period (eg _cdc\_cpp.py_ is for CPP/NPP data).

The contributed modules contain a constant to define their page name, arrays to define titles, names and default values for the graphs to be created, and one or more custom functions to inspect the monitoring histograms and provide the desired graph values.

_scan.py_ first calls the _init_ function to retrieve the graph titles, names and default values from each custom function by calling it without the root file pointer.  Next, it loops through the directory of root files, opening each one and using the _check_ function to pass a file pointer to each modules's custom functions.

When the custom functions are given a valid root file pointer, they extract the required quantities from the histogram, assess them, and return a list of the quantities values and associated status codes.  The status codes should be 1 (good), 0 (bad) or -1 (undefined).  If there is no real good or bad range for a quantity, its status should be set to 1 (good).  If a fit fails, the quantity should have the value None and the corresponding status should be -1 (undefined).

_scan.py_ uses the values and their assigned status codes to compile root graphs which will appear on the module's web page.  
A combined status graph for each  module is created from the status ratings of all of that module's quantities.  
The combined status graph is shown on the module's page and also on the overview page.  
An overall status is derived from all of these combined status values and shown as 'readiness' on the overview page. 

The overvew web page contains links to the root file containing all of the graphs and a csv file containing all of the quantities used to create the graphs.  The csv file might be useful for recalibration.


# How to add a module

[Follow the instructions here](https://github.com/JeffersonLab/gluex_demon/tree/main/make_new_module)

Contact Naomi when you're happy with it and ready to add it to the collection.


# Where to find the graphs online

[Here!](https://halldweb.jlab.org/gluex_demon/demon.html)
