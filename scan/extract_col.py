import sys
import os
import csv

script = sys.argv.pop(0)
nargs = len(sys.argv)

if nargs<2 or sys.argv[0] == "--help":
    exit("This script extracts the run number and data from the column name provided from demon's csv file.\nUsage: python3.6 extract_col.py <filename> <column-name>\n    eg python3.6 extract_col.py monitoring_data_2022-08_ver13.csv cdc_dedxmean.")

infile = sys.argv[0]

colname = sys.argv[1]

if not os.path.exists(infile) : 
    exit('Could not find file ',infile)

firstrow=True
with open(infile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['run'], row[colname])
