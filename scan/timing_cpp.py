from utils import get_histo, default_values     # demon's helper functions
from ROOT import gROOT,TF1

# Define the page name
PAGENAME = 'Timing'

# No SC or ECAL - import everything else from tracking2.py

from timing2 import tof_rf_time, bcal_rf_time, fcal_rf_time, cdc_rf_time, fdc_rf_time, ps_rf_time, tagh_rf_time, tagm_rf_time, fdc_tdc_diff, tagh_rf_channels, tagm_rf_channels, tof_adctdc_channels, tagh_adctdc_channels, tagm_adctdc_channels

def declare_functions() : 
  list_of_functions = [tof_rf_time, bcal_rf_time, fcal_rf_time, cdc_rf_time, fdc_rf_time, ps_rf_time, tagh_rf_time, tagm_rf_time, fdc_tdc_diff, tagh_rf_channels, tagm_rf_channels, tof_adctdc_channels, tagh_adctdc_channels, tagm_adctdc_channels]

  return list_of_functions

