* new_module.py is a template module which should be copied, renamed and customized.
* test_new_module.py is the script to run to test the new module, after changing 3 lines (it contains instructions).
  

The module (new_module.py) contains several functions:
* init
* check
* histogram inspection functions, one for each histogram to be inspected.  

The functions init and check call all of the histogram-inspection functions.  

When the histogram-inspection functions are called by init (the file pointer is set false), then they return lists of the names, titles and default status (-1) of whatever quantities are to be graphed.  

When they are called by check (with a valid pointer to the opened root file), they extract the required quantities from the histogram, assess them, and return a list of the quantities and associated status values.  The status values should be 1 (good), 0 (bad) or -1 (undefined).  If there is no real good or bad range for a quantity, its status should be set to 1 (good). 

The quantities and their assigned status ratings will appear on graphs on the module's web page.  A combined status graph for each  module is concocted from the status ratings of all of that module's quantities.  The combined status graph is shown on the module's page and also on the overview page.  An overall status is derived from all of these combined status values and shown as 'readiness' on the overview page. 
