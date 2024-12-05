##########
# Name: display-header.py
# Vers: 1.31
# Date: 241115
# Auth: Ronald Meijer
# Pyth: version 3
##########
# Dependency:	none
# ChangeLog:	1.30	first version to check csv file
#				1.31	detects the csv file delimiter
##########
# Variables:
#	filename	list of the '*.csv' files in working directory
#	location	specifies working directory
#	fileset		filenames in the list filename
#	suffix		'.csv'
##########
# Run:      python3 000-display-header-1.xx.py
##########

import csv
import glob
# 'location' specifies working directory
# location = 'c:/test/temp/'
import os.path
import re

print("\nThis script reads the header of a CSV file")
print ("\nFile(s) found in local directory:")
fileset = [file for file in glob.glob("*.csv", recursive=False)]

for file in fileset:
	print(" " + file)

filename = input("\nPlease enter the filename: ")

if (filename != ""):
	filename = filename.strip()
else:
	print("\n\t**** WARNING no file was selected...")
	quit()

if re.findall (".csv", filename):
	print("\n\tFile name format correct")
else:
	suffix = ".csv"
	filename = filename + suffix
	print("\n\tFile name format corrected")
if os.path.isfile(filename):
	print("\n\t**** INFORM file found\n")
	with open(filename) as f:
		dialect = csv.Sniffer().sniff(f.read(100))
		print("\t**** The delimiter used in the csv file is '" + dialect.delimiter + "' \n\n")
	answer = input("\nPress enter to continue")
	print("\nColumn \t Header")
else:
	print("\n\t**** WARNING cannot open file")
	quit()

with open(filename) as f:
	reader = csv.reader(f, delimiter=dialect.delimiter)
	header_row = next(reader)
	for index, column_header in enumerate(header_row):
		print(index, "\t" ,column_header.strip())
answer = input("\nPress enter to continue")

script = "\n ***** program end ***** " + " "
print(script)

