from utils import get_histo     # demon's helper functions
from ROOT import gROOT

# Define the page name
PAGENAME = 'Tracking'

# No ECAL - import everything else from tracking2.py

from tracking2 import fom, ncandidates, ntracks, bcal_matchrate, fcal_matchrate, sc_matchrate, tof_matchrate

def declare_functions() : 
  list_of_functions = [fom, ncandidates, ntracks, bcal_matchrate, fcal_matchrate, sc_matchrate, tof_matchrate]
  return list_of_functions


