##########
# Name:			config-int-descrip-shut.py
# Vers:			4.01
# Date:			230606
# Auth:			Ronald Meijer
# Pyth:			version 3
# Dependency	05-cluster-port-allocation_RON-SAMPLE_v4.0
# ChangeLog		4.01	if RESERVED-SPB in interface name no further action is taken
#
##########
# Variables:
#	intrfc__id		interface id
#	intrfc__nm		interface name; "none" sets to default
#	snmp_lnktr		snmp link trap; "no" disables
#	transceivr		"shut" in column "Transceiver"
#	switch_id1		left switch name
#	switch_id2		right switch name
#
#	filename	list of the *.csv files in working directory
#	location	specifies working directory
#	fileset		filenames in the list filename
#	outfil		name of the out-file 
##########
# Run:      python3 config-int-descrip-shut.py
##########

import csv
import glob
# 'location' specifies working directory
# location = 'c:/test/temp/'
import os.path
import re

print("\nThis script configures the interface 'name', admin-status and SNMP link trap for VOSS:")
print ("\nFile(s) found in local directory:")
fileset = [file for file in glob.glob("05*.csv", recursive=False)]

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
	print("\n\t**** INFORM file found\n\n")
	answer = input("\nPress enter to continue")
	print("Column \t Header")
else:
	print("\n\t**** WARNING cannot open file")
	quit()


with open (filename) as f:
	reader = csv.reader(f)
	header_row = next(reader)
	for index, column_header in enumerate(header_row):
		print(index, "\t" ,column_header.strip())
		if int(0) == index:
			switch_id1 = column_header.strip()
		if int(13) == index:
			switch_id2 = column_header.strip()

	answer = input("\nPress enter to continue")
	intrfc__id = []
	intrfc__nm = []
	snmp_lnktr = []
	transceivr = []
	for row in reader:
		try:
			intrfc__id.append(row[0])
			intrfc__nm.append(row[3])
			snmp_lnktr.append(row[4])
			transceivr.append(row[5])
		except IndexError:
			print("\n\n\t**** WARNING excel header not as expected!!!")
			quit()
	intrfc__id = [x.strip(" ") for x in intrfc__id]
	print(intrfc__id)
	intrfc__nm = [x.strip(" ") for x in intrfc__nm]
	print(intrfc__nm)
	snmp_lnktr = [x.strip(" ") for x in snmp_lnktr]
	snmp_lnktr = [x.lower() for x in snmp_lnktr]
	print(snmp_lnktr)
	transceivr = [x.strip(" ") for x in transceivr]
	transceivr = [x.lower() for x in transceivr]
	print(transceivr)
answer = input("Press enter to continue")
lenintrfc__id = len(intrfc__id)
lenintrfc__nm = len(intrfc__nm)
lensnmp_lnktr = len(snmp_lnktr)
lentransceivr = len(transceivr)
print(lenintrfc__id)
print(lenintrfc__nm)
print(lensnmp_lnktr)
print(lentransceivr)
answer = input("Press enter to continue with the left-hand switch")
	
if not "NONE" in switch_id1:
	outfil = "05-2-out-config-int-descrip-shut-" + switch_id1 + ".cfg"
	print("\nThe name of the out-file is " + outfil + " \n")
	answer = input("\nPress enter to continue")
	with open(outfil, 'w') as outfile:
		outfile.write('\n# ***** start of ' + outfil + ' ***** ')
	with open(outfil, 'a') as outfile:
		outfile.write('\n\n')
	script = "rwa"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("rwa\n")
	script = "rwa"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("rwa\n")
	script = "enable " + " "
	print (script)
	with open(outfil, 'a') as outfile:
		outfile.write("enable " + "\n\n")
	script = "configure terminal " + " "
	print (script)
	with open(outfil, 'a') as outfile:
		outfile.write("configure terminal\n\n")

	# script = "# During this phase we set all interfaces as tagged - encapsulation dot1q " + " "
	# print (script)
	# with open(outfil, 'a') as outfile:
		# outfile.write("# During this phase we set all interfaces as tagged - encapsulation dot1q \n\n")

	for value in range(0,lenintrfc__id):
		if "RESERVED-SPB" in intrfc__nm[value]:
			script = "# No action is taken on a RESERVED-SPB interface " + intrfc__id[value] + " ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on a RESERVED-SPB interface " + intrfc__id[value] + " ** ")
		else:
			if intrfc__id[value]:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				# script = "encapsulation dot1q " + " "
				# print(script)
				# with open(outfil, 'a') as outfile:
					# outfile.write("encapsulation dot1q " + "\n")		
				# script = "spoof-detect enable " + " "
				# print(script)
				# with open(outfil, 'a') as outfile:
					# outfile.write("spoof-detect enable " + "\n")
				if intrfc__nm[value]:
					if "none" in intrfc__nm[value]:
						script = 'default name ' + ' '
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write('default name ' + '\n')
					else:	
						script = 'name "' + intrfc__nm[value] + '" '
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write('name "' + intrfc__nm[value] + '"\n')
				if "shut" == transceivr[value]:
					script = "shutdown " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("shutdown " + "\n")
				else:
					script = "no shutdown " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no shutdown " + "\n")
				if "no" == snmp_lnktr[value]:
					script = "no snmp trap link-status " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no snmp trap link-status " + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")

script = "\nend " + "\n\n"
print(script)
with open(outfil, 'a') as outfile:
	outfile.write("\nend " + "\n\n")
	

print("\n#### Left-hand switch parsed succesfully\n\n")

with open (filename) as f:
	reader = csv.reader(f)
	header_row = next(reader)
	answer = input("\nPress enter to continue")
	intrfc__id = []
	intrfc__nm = []
	snmp_lnktr = []
	transceivr = []
	for row in reader:
		try:
			intrfc__id.append(row[13])
			intrfc__nm.append(row[16])
			snmp_lnktr.append(row[17])
			transceivr.append(row[18])
		except IndexError:
			print("\n\n\t**** WARNING excel header not as expected!!!")
			quit()
	intrfc__id = [x.strip(" ") for x in intrfc__id]
	print(intrfc__id)
	intrfc__nm = [x.strip(" ") for x in intrfc__nm]
	print(intrfc__nm)
	snmp_lnktr = [x.strip(" ") for x in snmp_lnktr]
	snmp_lnktr = [x.lower() for x in snmp_lnktr]
	print(snmp_lnktr)
	transceivr = [x.strip(" ") for x in transceivr]
	transceivr = [x.lower() for x in transceivr]
	print(transceivr)
answer = input("\nPress enter to continue")
lenintrfc__id = len(intrfc__id)
lenintrfc__nm = len(intrfc__nm)
lensnmp_lnktr = len(snmp_lnktr)
lentransceivr = len(transceivr)
print(lenintrfc__id)
print(lenintrfc__nm)
print(lensnmp_lnktr)
print(lentransceivr)

answer = input("\nPress enter to continue with the right-hand switch")
	
if not "NONE" in switch_id2:
	outfil = "05-2-out-config-int-descrip-shut-" + switch_id2 + ".cfg"
	print("\nThe name of the out-file is " + outfil + " \n")
	answer = input("\nPress enter to continue")
	with open(outfil, 'w') as outfile:
		outfile.write('\n# ***** start of ' + outfil + ' ***** ')
	with open(outfil, 'a') as outfile:
		outfile.write('\n\n')
	script = "rwa"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("rwa\n")
	script = "rwa"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("rwa\n")
	script = "enable " + " "
	print (script)
	with open(outfil, 'a') as outfile:
		outfile.write("enable " + "\n\n")
	script = "configure terminal " + " "
	print (script)
	with open(outfil, 'a') as outfile:
		outfile.write("configure terminal\n\n")

	# script = "# During this phase we set all interfaces as tagged - encapsulation dot1q " + " "
	# print (script)
	# with open(outfil, 'a') as outfile:
		# outfile.write("# During this phase we set all interfaces as tagged - encapsulation dot1q \n\n")

	for value in range(0,lenintrfc__id):
		if "RESERVED-SPB" in intrfc__nm[value]:
			script = "# No action is taken on a RESERVED-SPB interface " + intrfc__id[value] + " ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on a RESERVED-SPB interface " + intrfc__id[value] + " ** ")
		else:
			if intrfc__id[value]:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				# script = "encapsulation dot1q " + " "
				# print(script)
				# with open(outfil, 'a') as outfile:
					# outfile.write("encapsulation dot1q " + "\n")		
				# script = "spoof-detect enable " + " "
				# print(script)
				# with open(outfil, 'a') as outfile:
					# outfile.write("spoof-detect enable " + "\n")
				if intrfc__nm[value]:
					if "none" in intrfc__nm[value]:
						script = 'default name ' + ' '
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write('default name ' + '\n')
					else:	
						script = 'name "' + intrfc__nm[value] + '" '
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write('name "' + intrfc__nm[value] + '"\n')
				if "shut" == transceivr[value]:
					script = "shutdown " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("shutdown " + "\n")
				else:
					script = "no shutdown " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no shutdown " + "\n")
				if "no" == snmp_lnktr[value]:
					script = "no snmp trap link-status " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no snmp trap link-status " + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")

script = "\nend " + "\n\n"
print(script)
with open(outfil, 'a') as outfile:
	outfile.write("\nend " + "\n\n")

print("\n#### Right-hand switch parsed succesfully\n\n")

answer = input("\nPress enter to continue")

script = "\n ***** program end ***** " + " "
print(script)

