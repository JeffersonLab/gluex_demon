# Examples to adapt

* new_module.py is a template module which should be copied, renamed and customized. For inspiration, see the completed modules in [the scan directory](https://github.com/JeffersonLab/gluex_demon/tree/main/scan).
* test_new_module.py is the script to run to test the new module, after changing 3 lines (it contains instructions).

# How it works

The module (new_module.py) contains several functions:
* init
* check
* histogram-inspection functions, one for each histogram to be inspected.  

The functions _init_ and _check_ call all of the histogram-inspection functions.  

_test\_new\_module.py_ first calls _new\_module.py_'s _init_ function.  This calls each of the histogram-inspection functions (without a file pointer) to obtain and return lists of the names, titles and default status (-1) of whatever quantities are to be graphed.   


		       
It then loops through the directory of root files, opening each one and passing a file pointer to _new\_module.py_'s _check_ function. _check_ calls each of the histogram-inspection functions.  

When the histogram-inspection functions are called by _check_ (with a valid pointer to the opened root file), they extract the required quantities from the histogram, assess them, and return a list of the quantities and associated status values.  The status values should be 1 (good), 0 (bad) or -1 (undefined).  If there is no real good or bad range for a quantity, its status should be set to 1 (good). 

The quantities and their assigned status ratings are used to compile root graphs which will appear on the module's web page.  A combined status graph for each  module is concocted from the status ratings of all of that module's quantities.  The combined status graph is shown on the module's page and also on the overview page.  An overall status is derived from all of these combined status values and shown as 'readiness' on the overview page. 

# How to make your own module

Download the two scripts.  Rename _new\_module.py_ to suit your detector or purpose, and follow the instructions inside to customize it.  Then follow the instructions inside _test\_new\_module.py_ to test it.  

The overvew web page shows links to download the root file containing all of the graphs and a csv file containing all of the quantities used to create the graphs.  The csv file might be useful for recalibration.

For graphs with error bars, link the measurement with its uncertainty by giving the uncertainty graph the same name as the measurement graph with the suffix '_err' added, eg yourmodule_thing for the measurement and yourmodule_thing_err for the std deviation. 

To omit points from the graph, set their value to None (eg in photons.py to make separate graphs for different radiators). For failed fits it's probably more useful to show the 'undefined' value on the graph to indicate that there was a problem for that run. The example module uses -1 as a default to indicate undefined, but if this is a terrible choice for the quantity that you want to plot, feel free to choose a different value. However, the status should still be set to -1 for problem runs. 

