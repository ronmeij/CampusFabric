##########
# Name: 		05-1-config-dict-vlan-isid.py
# Vers: 		1.61
# Date: 		241116
# Auth: 		Ronald Meijer
# Pyth: 		version 3
# Dependency:	03-vlan-id-name-isid-ip_RON-SAMPLE_v2.0
# ChangeLog:	1.61	Detects the csv file delimiter
##########
# Variables:
#	vlan____id	vlan-id
#	isid____id	i-sid that maps to the vlan-id
#	vlan__elan	vlan-id to elan-id mapping dictionary
#
#	filename	list of the *.csv files in working directory
#	location	specifies working directory
#	fileset		filenames in the list filename
#	outfilename	name of the out-file 
##########
# Run:      python3 config-dict-vlan-isid.py
##########

import csv
import glob
# 'location' specifies working directory
# location = 'c:/test/temp/'
import os.path
import re

print("\nThis script populates the VLAN to I-SID dictionary used in 05-x-config-flex-uni-x.xx.py")
print ("\nFile(s) found in local directory:")
fileset = [file for file in glob.glob("03*.csv", recursive=False)]

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
	print("Column \t Header")
else:
	print ("\n\t**** WARNING cannot open file")
	quit()

with open (filename) as f:
	reader = csv.reader(f, delimiter=dialect.delimiter)
	header_row = next(reader)
	for index, column_header in enumerate(header_row):
		print(index, "\t" ,column_header.strip())
	answer = input("\nPress enter to continue")
	vlan____id = []
	isid____id = []
	for row in reader:
		try:
			vlan____id.append(row[0])
			isid____id.append(row[2])
		except IndexError:
			print("\n\n\t**** WARNING excel header not as expected!!!")
			quit()
	vlan____id = [x.strip(" ") for x in vlan____id]
	print(vlan____id)
	isid____id = [x.strip(" ") for x in isid____id]
	print(isid____id)
len_vlan____id = len(vlan____id)
len_isid____id = len(isid____id)
print(len_vlan____id)
print(len_isid____id)
answer = input("\nPress enter to continue")
outfilename = "05-1-out-dict-vlan-isid"
print("\nThe name of the out-file is " + outfilename + ".txt \n")
answer = input("\nPress enter to continue")

vlan__isid = {}

# build dictionary
for value in range(0,len_vlan____id):
	if vlan____id[value]:
		vlan__isid[vlan____id[value]] = isid____id[value]
# print number of vlans in excel file
print("Number of entries in excel file: " + str(len_vlan____id))
# print the number of keys in dictionary
print("Number of entries in dictionary: " + (str(len(vlan__isid.keys()))))
len_vlan__isid = len(vlan__isid.keys())

answer = input("\nPress enter to continue")

for key, value in vlan__isid.items():
	print("VLAN: " + key + "\tI-SID: " + value)

# convert key to integer
new_vlan_isid = {int(old_key): val for old_key, val in vlan__isid.items()}

# sort dictionary as vlan_isid_sorted
vlan__isid_sorted = {}
for i in sorted(new_vlan_isid):
   vlan__isid_sorted[i] = new_vlan_isid[i]
# print(vlan__isid_sorted)

# write file
print("\nSorted output:")
with open(outfilename + '.txt', 'w') as outfile:
	outfile.write("{")
for key, value in vlan__isid_sorted.items():
	print("VLAN: " + str(key) + "\tI-SID: " + value)
	with open(outfilename + '.txt', 'a') as outfile:
		outfile.write("\n    " + str(key) + " : " + value + ",")
with open(outfilename + '.txt', 'a') as outfile:
	outfile.write("\n    }" + "\n")

# Finding duplicated vlan ids
if len_vlan__isid < len_vlan____id:
	print("\n\t**** WARNING duplicated VLAN id(s) found: ")
# Printing original list
# print ("Original list is : " + str(vlan____id))

# convert list to integers
for i in range(0, len(vlan____id)):
	vlan____id[i] = int(vlan____id[i])

# Printing modified list 
# print ("Modified list is : " + str(vlan____id))
# Searching duplicate intergers in list
def repeat(x):
	_size = len(x)
	repeated = []
	for i in range(_size):
		k = i + 1
		for j in range(k, _size):
			if x[i] == x[j] and x[i] not in repeated:
				repeated.append(x[i])
	return repeated

# Print duplicates
# print("\t\t\tThe following VLAN id(s) are duplicated: " + str(repeat(vlan____id)))
len_repeat = len(repeat(vlan____id))
# print(len_repeat)
for vlan in range(0,len_repeat):
	print("\t\t Duplicated VLAN: " + str(repeat(vlan____id)[vlan]) + " ")

# Finding duplicate isid values in a dictionary

# printing initial_dictionary
# print("Initial_dictionary :", str(vlan__isid_sorted))

# finding duplicate values in dictionary
rev_dict = {}
  
for key, value in vlan__isid_sorted.items():
    rev_dict.setdefault(value, set()).add(key)

result = [key for key, values in rev_dict.items() if len(values) > 1]

# printing result
if str(result) != "[]":
	print("\n\n\t**** WARNING duplicate I-SIDs found: ")
	# print("\n\n\t**** WARNING duplicate I-SIDs found: " + str(result) + " Please check information!!!")

def getKeysByValue(dictOfElements, valueToFind):
	listOfKeys = list()
	listOfItems = dictOfElements.items()
	for item  in listOfItems:
		if item[1] == valueToFind:
			listOfKeys.append(item[0])
	return listOfKeys

for isid in result:
	listOfKeys = getKeysByValue(vlan__isid_sorted, isid)
	print("\t\tVLANs with an I-SID equal to " + str(isid) + ": ")
	for key  in listOfKeys:
		print("\t\t\t VLAN: " + str(key))

answer = input("\nPress enter to continue")

script = "\n ***** program end ***** " + " "
print(script)

