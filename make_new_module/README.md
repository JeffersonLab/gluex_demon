# Examples to adapt

* example.py is a template module which should be copied, renamed and customized. For inspiration, see the completed modules in [the scan directory](https://github.com/JeffersonLab/gluex_demon/tree/main/scan).
* test_new_module.py is the script to run to test the new module, after changing 3 lines (it contains instructions).

# How it works

The example module (_example.py_) contains several functions to inspect the monitoring histograms and define graphs to be created. 

_test\_new\_module.py_ calls each function in this module once (with rootfile=False) to collect the graph titles and names,
and then again for each root file, to get the values for that run.  Each function will extract the required quantities from the histogram, assess them, and return a list of the quantities and associated status values.  If a quantity is unavailable (not enough stats to calculate it), its value should be set to None.  The status values should be 1 (good), 0 (bad) or -1 (undefined).  If there is no real good or bad range for a quantity, its status should be set to 1 (good).  

The quantities and their assigned status ratings are used to compile root graphs which will appear on the module's web page.  A combined status graph for each module is created from the status ratings of all of that module's quantities.  The combined status graph is shown on the module's page and also on the overview page.  An overall status is derived from all of these combined status values and shown as 'readiness' on the overview page. 

The overvew web page shows links to download the root file containing all of the graphs and a csv file containing all of the quantities used to create the graphs.  The csv file might be useful for recalibration.

# How to make your own module

Download the two scripts.  Rename _example.py_ to suit your detector or purpose, and follow the instructions inside to customize it.  Then follow the instructions inside _test\_new\_module.py_ to test it.  Send it to Naomi when it's ready for use.

