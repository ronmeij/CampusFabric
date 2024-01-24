##########
# Name: 		config-lag-mlt-flex-cvlan-uni-int.py
# Vers: 		4.13
# Date: 		231005
# Auth: 		Ronald Meijer
# Pyth: 		version 3
# Dependency	05-cluster-port-allocation_RON-SAMPLE_v4.0
#				Using external dictionary '05-1-out-dict-vlan-isid.txt'
# ChangeLog		4.01	Added the option for simplified vIST
#						Corrected vlan "0" in phase 3 & 4
#						LACP key id is interface id
#				4.02	Check for duplicate lag/mlt ids
#						Check for same mlt id in peer
#						Commented no spanning tree at interface level
#				4.03	accept n or , as delimiter
#				4.04	accept only ascii characters
#				4.05	correction for static mlt with more than one member
#				4.06	accept only ascii characters in part 2
#				4.07	correction for untagged traffic on tagged port cvlan & simplified
#				4.08	correction for flex-uni with only 1 vlan in list
#				4.09	correction for v-vlan with only 1 vlan in list
#				4.10	no untagged-frames-discard on flex-uni
#				4.11	if switch is stand-alone no peer-checks are to be executed at the end
#				4.12	support on vlan range 2,4-8,10
#				4.13	compare for vlan range did not work correct anymore
##########
# Variables:
#	intrfc__id 	interface id 
#	intrfc__nm	interface description used for mlt name if lag_mlt_id
#	tagged_int	tagging yes or no
#	fa_mgmt_tg	fabric attach setting, in connection to tagged
#	lacp___ena	set mlt as lacp mlt
#	lag_mlt_id	lag/mlt id
#	lag_mlt_pr	lag/mlt peer id
#	def_vln_id	default vlan id (used for untagged interfaces)
#	vlan____id	tagged vlan ids with a separator "n" or ","
#	cvid__list	customer tagged vlan list
#	cvid_value	customer tagged vlan id from list
#	cvid_intgr	customer tagged vlan id as integer
#	switch_id1	left switch name
#	switch_id2	right switch name
#	uni___type	selector for flex-uni or c-vlan uni
#	uni___name	selected type; used to determine the settings
#	fa_mgmt_is	mgmt i-sid for fa with cvlan-uni
#
#	filename	list of the *.csv files in working directory
#	location	specifies working directory
#	fileset		filenames in the list filename
#	outfil		name of the out-file 
##########
# Run:      python3 config-lag-mlt-flex-cvlan-uni-int.py
##########

import csv
import glob
# 'location' specifies working directory
# location = 'c:/test/temp/'
import os.path
import re
import ast

print("\nThis script configures LACP on interface or on (S)MLT for VOSS")
print("\nThis script configures MLT/SMLT or LAG/MLAG for VOSS")
print("\nThis script configures VLAN membership (CVLAN-UNI, Flex-UNI or Simplified-vIST syntax) for VOSS")
print("\nThis script is valid for CVLAN-UNI, Flex-UNI and Simplified-vIST\n")
print("\n\nFor Flex-UNI the dictionary file needs to be build with script 05-1, name is 05-1-out-dict-vlan-isid.txt\n")
# select uni-type
while True:
	try:
		uni___type = int(input("\nSelect the UNI-type:\n 1 for CVLAN-UNI (Customer-UNI)\n 2 for Flex-UNI  (switched-UNI)\n 3 for Simplified-vIST\n  : [2] ") or "2")
	except ValueError:
		print("Should be a value from 1 to 3")
		continue
	else:
		if uni___type <= 0:
			print("\nPlease select a value between 1 and 3")
			continue
		if uni___type >= 4:
			print("\nPlease select a value between 1 and 3")
			continue
		# uni-type number was succesfully parsed
		break
if uni___type == 1:
	uni___name = "CustUni"
elif uni___type == 2:
	uni___name = "FlexUni"
elif uni___type == 3:
	uni___name = "SimvIST"
print("\n")
# uni-name was successfully set

# if custuni is chosen we would need to have the mgmt i-sid for fa if required
if uni___name == "CustUni":
	while True:
		try:
			fa_mgmt_is = int(input("\nIf you are using Fabric Attach with management VLAN enter the mgmt i-sid or 0 to skip\n  : [0] ") or "0")
		except ValueError:
			print("Should be a value from 1 to 15999999")
			continue
		else:
			if fa_mgmt_is < 0:
				print("\nPlease select a value between 0 and 15999999")
				continue
			if fa_mgmt_is >= 16000000:
				print("\nPlease select a value between 0 and 15999999")
				continue
			# management i-sid was succesfully parsed
			break
	print("\n")

# load dictionary file into memory for flex-uni
if uni___name == "FlexUni":
	print("\n\n**** INFORM reading dictionary file in directory '05-1-out-dict-vlan-isid.txt'")
	# reading the dictionay data from the file
	dict__file = '05-1-out-dict-vlan-isid.txt'
	try:
		with open(dict__file) as dictionary_vlan_elan:
			data = dictionary_vlan_elan.read()
		print("\n# data type before reconstruction: ", type(data))
		# reconstructing the data as a dictionary
		vlan__elan = ast.literal_eval(data)
		print("# data type after reconstruction:  ", type(vlan__elan))
		print(vlan__elan)
		print("\n**** INFORM dictionary file '05-1-out-dict-vlan-isid.txt' succesfully loaded\n\n")
	except FileNotFoundError:
		print("\n**** WARNING dictionary file '05-1-out-dict-vlan-isid.txt' not found in directory !!!" + " ")
		print("\tcheck if the file '05-1-out-dict-vlan-isid.txt' exists" + " \n\n")
		answer = input("\nPress enter to quit")
		quit()
	except SyntaxError:
		print("\n\n#### WARNING syntax error in dictionary file !!!" + " ")
		answer = input("\nPress enter to quit")
		quit()
# dictionary file was loaded

# load 05-*.csv file into memory
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

	fa_mgmt_tg = []
	tagged_int = []
	lag_mlt_id = []
	intrfc__id = []
	intrfc__nm = []
	lacp___ena = []
	lag_mlt_pr = []
	lag_mlt_id = []
	def_vln_id = []
	vlan____id = []
	vlan_id_pr = []
	for row in reader:
		try:
			fa_mgmt_tg.append(row[7])
			tagged_int.append(row[6])
			lag_mlt_id.append(row[9])
			intrfc__id.append(row[0])
			intrfc__nm.append(row[3])
			lacp___ena.append(row[8])
			lag_mlt_pr.append(row[22])
			def_vln_id.append(row[10])
			vlan____id.append(row[11])
			vlan_id_pr.append(row[24])
		except IndexError:
			print("\n\n\t**** ERROR excel header not as expected!!!")
			quit()
	print("\n\n**** List data:")
	print("\t**** fa/fa-mgmt")
	fa_mgmt_tg = [x.encode("ascii", "ignore") for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.decode() for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.strip(" ") for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.lower() for x in fa_mgmt_tg]
	print(fa_mgmt_tg)
	print("\n\t**** tagged")
	tagged_int = [x.encode("ascii", "ignore") for x in tagged_int]
	tagged_int = [x.decode() for x in tagged_int]
	tagged_int = [x.strip(" ") for x in tagged_int]
	tagged_int = [x.lower() for x in tagged_int]
	print(tagged_int)
	print("\n\t**** mlag/smlt id")
	lag_mlt_id = [x.encode("ascii", "ignore") for x in lag_mlt_id]
	lag_mlt_id = [x.decode() for x in lag_mlt_id]
	lag_mlt_id = [x.strip(" ") for x in lag_mlt_id]
	print(lag_mlt_id)
	print("\n\t**** mlag/smlt id from peer switch")
	lag_mlt_pr = [x.encode("ascii", "ignore") for x in lag_mlt_pr]
	lag_mlt_pr = [x.decode() for x in lag_mlt_pr]
	lag_mlt_pr = [x.strip(" ") for x in lag_mlt_pr]
	print(lag_mlt_pr)
	print("\n\t**** interface id")
	intrfc__id = [x.encode("ascii", "ignore") for x in intrfc__id]
	intrfc__id = [x.decode() for x in intrfc__id]
	intrfc__id = [x.strip(" ") for x in intrfc__id]
	print(intrfc__id)
	print("\n\t**** interface name")
	intrfc__nm = [x.encode("ascii", "ignore") for x in intrfc__nm]
	intrfc__nm = [x.decode() for x in intrfc__nm]
	intrfc__nm = [x.strip(" ") for x in intrfc__nm]
	print(intrfc__nm)
	print("\n\t**** lacp")
	lacp___ena = [x.encode("ascii", "ignore") for x in lacp___ena]
	lacp___ena = [x.decode() for x in lacp___ena]
	lacp___ena = [x.strip(" ") for x in lacp___ena]
	lacp___ena = [x.lower() for x in lacp___ena]
	print(lacp___ena)
	print("\n\t**** default vlan id")
	def_vln_id = [x.encode("ascii", "ignore") for x in def_vln_id]
	def_vln_id = [x.decode() for x in def_vln_id]
	def_vln_id = [x.strip(" ") for x in def_vln_id]
	print(def_vln_id)
	print("\n\t**** vlan id (as in csv file)")
	print(vlan____id)
	print("\n\t**** vlan id (corrected format)")
	vlan____id = [x.encode("ascii", "ignore") for x in vlan____id]
	vlan____id = [x.decode() for x in vlan____id]
	vlan____id = [x.strip(" ") for x in vlan____id]
	vlan____id = [x.replace("n",",") for x in vlan____id]
	vlan____id = [x.rstrip(",") for x in vlan____id]
	vlan____id = [x.replace(" ","") for x in vlan____id]
	print(vlan____id)
	print("\n\t**** vlan id (list that we have to interprete to get all vlan ids)")
	vlan_tmpid = vlan____id [:]
	vlan_nw_id = []
	print(vlan_tmpid)
	print("\n\t**** number of items in vlan id list (number of interfaces in the list)")
	lenvlan_tmpid = len(vlan_tmpid)
	print(lenvlan_tmpid)
	for vlans_int in vlan_tmpid:
		if vlans_int != '':
			print("\n\n\t**** vlan ids for the interface")
			print(vlans_int)
			vlan__list = vlans_int.split(',')
			vlan_nlist = []
			print("\t**** vlan ids as list for the interface")
			print(vlan__list)
			for vlan_value in vlan__list:
				if "-" in vlan_value:
					vlan_range = vlan_value.split('-')
					for vlan____ids in vlan_range:
						a1 = int(vlan_range[0])
						a2 = int(vlan_range[1])
						if a1 > a2:
							print("\n\n\t**** ERROR in vlan range " + str(vlan__list) + " ")
							quit()
					for vlanid in range(a1,(a2+1)):
						vlan_nlist.append(str(vlanid))
				else:
					vlan_nlist.append(vlan_value)
			print("\t**** vlan ids as complete list for the interface")
			vlan_nlist.sort()
			vlan_nlist = [int(x) for x in vlan_nlist]
			vlan_nlist.sort()
			vlan__uniq = []
			[vlan__uniq.append(x) for x in vlan_nlist if x not in vlan__uniq]
			print(vlan__uniq)
			vlan_lst = ''
			for vlnid in vlan__uniq:
				vlan_lst = vlan_lst + str(vlnid) + ','
			vlan_nw_id.append(vlan_lst)
		else:
			vlan_nw_id.append(vlans_int)
	vlan_nw_id = [x.rstrip(",") for x in vlan_nw_id]
	print("\n\n\t**** vlan id (final result)")
	print(vlan_nw_id)
	print("\n\t**** vlan ids for each interface (final result)")
	vlan_orgid = []
	vlan_orgid = vlan____id [:]
	for vlan_lst in vlan_nw_id:
		print(vlan_lst)
	vlan____id = vlan_nw_id [:]
	print("\n\t**** vlan id original value")
	print(vlan_orgid)
	print("\n\t**** vlan id peer")
	vlan_id_pr = [x.encode("ascii", "ignore") for x in vlan_id_pr]
	vlan_id_pr = [x.decode() for x in vlan_id_pr]
	vlan_id_pr = [x.strip(" ") for x in vlan_id_pr]
	vlan_id_pr = [x.replace("n",",") for x in vlan_id_pr]
	vlan_id_pr = [x.rstrip(",") for x in vlan_id_pr]
	print(vlan_id_pr)
answer = input("\nPress enter to continue")
lenfa_mgmt_tg = len(fa_mgmt_tg)
lentagged_int = len(tagged_int)
lenlag_mlt_id = len(lag_mlt_id)
lenintrfc__id = len(intrfc__id)
lenintrfc__nm = len(intrfc__nm)
lenlacp___ena = len(lacp___ena)
lenlag_mlt_pr = len(lag_mlt_pr)
lendef_vln_id = len(def_vln_id)
lenvlan____id = len(vlan____id)
lenvlan_id_pr = len(vlan_id_pr)
print("\n\n**** Number of list entries (should be all the same):")
print(lenfa_mgmt_tg)
print(lentagged_int)
print(lenlag_mlt_id)
print(lenintrfc__id)
print(lenintrfc__nm)
print(lenlacp___ena)
print(lenlag_mlt_pr)
print(lendef_vln_id)
print(lenvlan____id)
print(lenvlan_id_pr)

answer = input("#### Press enter to continue with the " + switch_id1 + " switch")

catcherror = []

if not "NONE" in switch_id1:
	outfil = "05-3-out-config-lag-mlt-int-" + switch_id1 + ".cfg"
	print("\nThe name of the out-file is " + outfil + " \n")
	answer = input("\nPress enter to continue")
	with open(outfil, 'w') as outfile:
		outfile.write('\n# ***** start of ' + outfil + ' ***** ')
	with open(outfil, 'a') as outfile:
		outfile.write('\n# ***** ' + uni___name + '-Type was selected ***** ')
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

# check if NNI in mltid -> no action
# check if an mlt-id is configured then:
#	no flex-uni on interface level; it has to be set at mlt level
#	if CVLAN-UNI and yes in tagged -> untagged-frames-discard on interface
#	if CVLAN-UNI and no in tagged -> no encapsulation dot1q
#	if Simplified-vIST -> no flex-uni commands at interface or mlt level
#	if lacp-s/lacp-l in lacp -> configure lacp on interface level
#	if lacp-s/lacp-l in lacp and no value in mltid -> error
#	if lacp in lacp -> configure mltid as lacp-id
#	if lacp in lacp -> disable stp on interface
	script = "\n\n# STEP 1 - Check if MLTid is configured and modify underlying interface"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n# STEP 1 - Check if MLTid is configured and modify underlying interface \n")
	script = "#        - If no MLTid is configured then modify the interface\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("#        - If no MLTid is configured then modify the interface \n")
	for value in range(0,lenlag_mlt_id):
		if "NNI" in lag_mlt_id[value]:
			script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected **")
		else:
			if lag_mlt_id[value]:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				if uni___name != "SimvIST":
					script = "no flex-uni enable " 
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no flex-uni enable\n")
				if uni___name != "FlexUni":
					if "yes" in tagged_int[value]:
						if "0" == def_vln_id[value]:
							script = "untagged-frames-discard " 
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("untagged-frames-discard\n")
					if "no" in tagged_int[value]:
						script = "no encapulation dot1q " 
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("no encapsulation dot1q\n")
				if "lacp-s" in lacp___ena[value]:
					script = "lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time short "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time short " + " \n")
					script = "lacp enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp enable " + " \n")
					script = "# no spanning-tree mstp  force-port-state enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					script = "# y\n" + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# y\n" + "\n")
				if "lacp-l" in lacp___ena[value]:
					script = "lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time long "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time long " + " \n")
					script = "lacp enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp enable " + " \n")
					script = "# no spanning-tree mstp  force-port-state enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					script = "# y\n" + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# y\n" + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")
			else:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				if uni___name == "CustUni":
					script = "no flex-uni enable " 
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no flex-uni enable\n")
				if uni___name != "FlexUni":
					if "no" in tagged_int[value]:
						script = "no encapsulation dot1q " 
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("no encapsulation dot1q\n")
				# correction for version 4.10
				# if "yes" in tagged_int[value]:
					# if "0" == def_vln_id[value]:
						# script = "untagged-frames-discard " 
						# print(script)
						# with open(outfil, 'a') as outfile:
							# outfile.write("untagged-frames-discard\n")
				if "lacp-s" in lacp___ena[value]:
					print("\n\n#### ERROR you cannot configure LACP without configuring a LACP-key value !!!" + " ")
					print("\n\t# LACP key missing on interface " + intrfc__id[value] + " in column MLAG/SMLTid !!!" + " \n\n")
					quit()
					# script = "lacp key " + str(value + 1) + " aggregation enable timeout-time short "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp key " + str(value + 1) + " aggregation enable timeout-time short " + " \n")
					# script = "lacp enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp enable " + " \n")
					# script = "# no spanning-tree mstp  force-port-state enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					# script = "# y\n" + "\n"
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# y\n" + "\n")
				if "lacp-l" in lacp___ena[value]:
					print("\n\n#### ERROR you cannot configure LACP without configuring a LACP-key value !!!" + " ")
					print("\n\t# LACP key missing on interface " + intrfc__id[value] + " in column MLAG/SMLTid !!!" + " \n\n")
					quit()
					# script = "lacp key " + str(value + 1) + " aggregation enable "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp key " + str(value + 1) + " aggregation enable " + " \n")
					# script = "lacp enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp enable " + " \n")
					# script = "# no spanning-tree mstp  force-port-state enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					# script = "# y\n" + "\n"
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# y\n" + "\n")
				if uni___name != "SimvIST":
					if "fa" in fa_mgmt_tg[value]:
						script = "fa " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa" + "\n")
						script = "fa enable" + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa enable" + "\n")
					if "mgmt" in fa_mgmt_tg[value]:
						script = "fa " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa" + "\n")
						script = "fa enable" + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa enable" + "\n")
						if uni___name == "FlexUni":
							if "yes" in tagged_int[value]:
								if vlan____id[value]:
									if "," in vlan____id[value]:
										cvid__list = vlan____id[value].split(',')
										for cvid_value in cvid__list:
											cvid_intgr = int(cvid_value)
											script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + "\n")
							if "no" in tagged_int[value]:
								
								if vlan____id[value]:
									if "," in  vlan____id[value]:
										cvid__list = vlan____id[value].split(',')
										for cvid_value in cvid__list:
											cvid_intgr = int(cvid_value)
											try:
												script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + "\n")
											except KeyError:
												print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
												print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
												quit()
						if uni___name == "CustUni":
							if "yes" in tagged_int[value]:
								if vlan____id[value]:
									script = "fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + "\n")	
							if "no" in tagged_int[value]:
								
								if vlan____id[value]:
									script = "fa management i-sid " + str(fa_mgmt_is) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("fa management i-sid " + str(fa_mgmt_is) + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")

	script = "\n\n# STEP 2 - Configure the MLT interface"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n\n\n# STEP 2 - Configure the MLT interface")
	script = "#        - For SMLT check if VLAN list is coherent\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n#        - For SMLT check if the VLAN list is coherent \n")

	dup_lag_mlt_id_lft = []

	for value in range(0,lenlag_mlt_id):
		if "NNI" in lag_mlt_id[value]:
			script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
		else:
			if lag_mlt_id[value]:
				if lag_mlt_id[value] not in dup_lag_mlt_id_lft:
					dup_lag_mlt_id_lft.append(lag_mlt_id[value])
					# print (dup_lag_mlt_id_lft)
					script = "\n\nmlt " + lag_mlt_id[value] + ' enable name MLT--' + lag_mlt_id[value] + ' '
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("\n\nmlt " + lag_mlt_id[value] + ' enable name MLT--' + lag_mlt_id[value] + '\n')
					if not "lacp" in lacp___ena[value]:
						if "yes" in tagged_int[value]:
							script = "mlt " + lag_mlt_id[value] + " encapsulation dot1q " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("mlt " + lag_mlt_id[value] + " encapsulation dot1q " + "\n")
						script = "mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + "\n")
					if lag_mlt_id[value]:
						script = "\ninterface mlt " + lag_mlt_id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("\ninterface mlt " + lag_mlt_id[value] + "\n")
						if lag_mlt_id[value] in lag_mlt_pr:
							script = "smlt " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("smlt" + "\n")
							if vlan_orgid[value] != vlan_id_pr[value]:
								print("\n\n#### WARNING VLAN list not the same on SMLT peers for MLTid: " + str(lag_mlt_id[value]) + ", PLEASE review !!!\n")
								catcherror.append(lag_mlt_id[value])
								with open(outfil, 'a') as outfile:
									outfile.write("\n#### WARNING VLAN list not the same on SMLT peers for MLTid: " + str(lag_mlt_id[value]) + ", PLEASE review !!!\n\n\n")
# here you need to specify flex-uni
					if uni___name == "FlexUni":
						script = "flex-uni enable " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("flex-uni enable" + "\n")
					if "lacp" in lacp___ena[value]:
						script = "lacp enable key " + lag_mlt_id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("lacp enable key " + lag_mlt_id[value] + "\n")
					if uni___name != "SimvIST":
						if "fa" in fa_mgmt_tg[value]:
							script = "fa " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa" + "\n")
							script = "fa enable" + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa enable" + "\n")
						if "mgmt" in fa_mgmt_tg[value]:
							script = "fa " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa" + "\n")
							script = "fa enable" + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa enable" + "\n")
							if uni___name == "FlexUni":
								if "yes" in tagged_int[value]:
									
									if vlan____id[value]:
										if "," in vlan____id[value]:
											cvid__list = vlan____id[value].split(',')
											for cvid_value in cvid__list:
												cvid_intgr = int(cvid_value)
												try:
													script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + "\n")
												except KeyError:
													print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
													print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
													quit()
								if "no" in tagged_int[value]:
									
									if vlan____id[value]:
										if "," in vlan____id[value]:
											cvid__list = vlan____id[value].split(',')
											for cvid_value in cvid__list:
												cvid_intgr = int(cvid_value)
												script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + "\n")
							if uni___name == "CustUni":
								if "yes" in tagged_int[value]:
									if vlan____id[value]:
										script = "fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + "\n")	
								if "no" in tagged_int[value]:
									if vlan____id[value]:
										script = "fa management i-sid " + str(fa_mgmt_is) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("fa management i-sid " + str(fa_mgmt_is) + "\n")
					script = "exit " + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("exit" + "\n")
				else:
					if not "lacp" in lacp___ena[value]:
						script = "mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("\nmlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + "\n")

# here you need to specify flex-uni
	if uni___name == "FlexUni":
		script = "\n\n# STEP 3 - Configure VLANs on Flex-UNI interfaces\n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 3 - Configure VLANs on Flex-UNI interfaces \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "mgmt" in fa_mgmt_tg[value]:
					if not "fa" in fa_mgmt_tg[value]:
						if vlan____id[value]:
							if "," in vlan____id[value]:
								cvid__list = vlan____id[value].split(',')
								for cvid_value in cvid__list:
									cvid_intgr = int(cvid_value)
									try:
										script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
									except KeyError:
										print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
										print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
										quit()
									if lag_mlt_id[value]:
										if "yes" in tagged_int[value]:
											script = "c-vid " + (cvid_value) + " mlt " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("c-vid " + (cvid_value) + " mlt " + lag_mlt_id[value] + "\n")
									else:
										if "yes" in tagged_int[value]:
											script = "c-vid " + (cvid_value) + " port " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("c-vid " + (cvid_value) + " port " + intrfc__id[value] + "\n")
									script = "exit"
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("exit " + " " + "\n")
							elif vlan____id[value]:
								cvid_intgr = int(vlan____id[value])
								try:
									script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
								except KeyError:
									print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
									print("\n\t# check if the VLANid '" + str(cvid_intgr) + "' exists in dictionary file!!!" + " \n\n")
									quit()
								if lag_mlt_id[value]:
									if "yes" in tagged_int[value]:
										script = "c-vid " + str(cvid_intgr) + " mlt " + lag_mlt_id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("c-vid " + str(cvid_intgr) + " mlt " + lag_mlt_id[value] + "\n")
								else:
									if "yes" in tagged_int[value]:
										script = "c-vid " + str(cvid_intgr) + " port " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("c-vid " + str(cvid_intgr) + " port " + intrfc__id[value] + "\n")
								script = "exit"
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("exit " + " " + "\n")
# if there is a default vlanid not equal 0 defined on a tagged interface/mlt
	if uni___name == "FlexUni":
		script = "\n\n# STEP 4 - Configure untagged VLAN on tagged Flex-UNI interfaces \n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 4 - Configure untagged VLAN on tagged Flex-UNI interfaces \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			elif "0" == def_vln_id[value]:
				script = "# No untagged VLAN is defined on interface " + intrfc__id[value] + " ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No untagged VLAN is defined on interface " + intrfc__id[value] + " ** ")
			elif "yes" in tagged_int[value]:
				cvid_intgr = int(def_vln_id[value])
				script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
				if lag_mlt_id[value]:
					script = "untagged-traffic " + " mlt " + lag_mlt_id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " mlt " + lag_mlt_id[value] + "\n")
				else:
					script = "untagged-traffic " + " port " + intrfc__id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " port " + intrfc__id[value] + "\n")
				script = "exit"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit " + " " + "\n")
			else:
				cvid_intgr = int(def_vln_id[value])
				script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
				if lag_mlt_id[value]:
					script = "untagged-traffic " + " mlt " + lag_mlt_id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " mlt " + lag_mlt_id[value] + "\n")
				else:
					script = "untagged-traffic " + " port " + intrfc__id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " port " + intrfc__id[value] + "\n")
				script = "exit"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit " + " " + "\n")
# here you need to specify the script for cust-uni
	if uni___name != "FlexUni":
		script = "\n\n# STEP 3 - Configure VLANs on CVLAN-UNI or Simplified-vIST interfaces \n\n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 3 - Configure VLANs on CVLAN-UNI or Simplified-vIST interfaces \n\n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "mgmt" in fa_mgmt_tg[value]:
					if not "fa" in fa_mgmt_tg[value]:
						if vlan____id[value]:
							if "," in vlan____id[value]:
								cvid__list = vlan____id[value].split(',')
								for cvid_value in cvid__list:
									if lag_mlt_id[value]:
										if "yes" in tagged_int[value]:
											if "lacp" in lacp___ena[value]:
												# check if the lag_mlt_id is more than once in the list
												# then we have to disable lacp on the interface first
												counter = lag_mlt_id.count(lag_mlt_id[value])
												if counter >= 2:
													script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
													script = "interface gigabitethernet " + intrfc__id[value] + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
													script = "no lacp enable "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nno lacp enable")
													script = "exit "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nexit\n")
												script = "vlan member add " + (cvid_value) + " " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nvlan member add " + (cvid_value) + " " + intrfc__id[value] + "\n")

												# check if the lag_mlt_id is more than once in the list
												# then we have to enable lacp on the interface again
												counter = lag_mlt_id.count(lag_mlt_id[value])
												if counter >= 2:
													script = "interface gigabitethernet " + intrfc__id[value] + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
													script = "lacp enable "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nlacp enable")
													script = "exit "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nexit\n")
											else:
												script = "vlan mlt " + (cvid_value) + " " + lag_mlt_id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nvlan mlt " + (cvid_value) + " " + lag_mlt_id[value] + "\n")
									else:
										if "yes" in tagged_int[value]:
											script = "vlan member add " + (cvid_value) + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + (cvid_value) + " " + intrfc__id[value] + "\n")
							elif vlan____id[value]:
								cvid_intgr = int(vlan____id[value])
								if lag_mlt_id[value]:
									if "yes" in tagged_int[value]:
										if "lacp" in lacp___ena[value]:
											# check if the lag_mlt_id is more than once in the list
											# then we have to disable lacp on the interface first
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "no lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nno lacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
											script = "vlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + "\n")

											# check if the lag_mlt_id is more than once in the list
											# then we have to enable lacp on the interface again
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nlacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
										else:
											script = "vlan mlt " + str(cvid_intgr) + " " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan mlt " + str(cvid_intgr) + " " + lag_mlt_id[value] + "\n")
								else:
									if "yes" in tagged_int[value]:
										script = "vlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\nvlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + "\n")
						else:
							if lag_mlt_id[value]:
								if "no" in tagged_int[value]:
									if not "0" == def_vln_id[value]:
										if "lacp" in lacp___ena[value]:
											# check if the lag_mlt_id is more than once in the list
											# then we have to disable lacp on the interface first
											counter = lag_mlt_id.count(lag_mlt_id[value])
											print(counter)
											if counter >= 2:
												script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "no lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nno lacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
											
											script = "vlan member add " + def_vln_id[value] + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + def_vln_id[value] + " " + intrfc__id[value] + "\n")

											# check if the lag_mlt_id is more than once in the list
											# then we have to enable lacp on the interface again
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nlacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
										else:
											script = "vlan mlt " + def_vln_id[value] + " " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan mlt " + def_vln_id[value] + " " + lag_mlt_id[value] + "\n")
							else:
								if "no" in tagged_int[value]:
									if not "0" == def_vln_id[value]:
										script = "vlan member add " + def_vln_id[value] + " " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\nvlan member add " + def_vln_id[value] + " " + intrfc__id[value] + "\n")
# if there is a default vlanid not equal 0 defined on a tagged interface/mlt
	if uni___name != "FlexUni":
		script = "\n\n# STEP 4 - Configure untagged VLAN on tagged CVLAN-UNI or Simplified-vIST interfaces \n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 4 - Configure untagged VLAN on tagged CVLAN-UNI or Simplified-vIST interfaces \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "0" == def_vln_id[value]:
					if "yes" in tagged_int[value]:
						if not "mgmt" in fa_mgmt_tg[value]:
							if not "fa" in fa_mgmt_tg[value]:
								script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + " ")
								script = "default-vlan-id " + def_vln_id[value] + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\ndefault-vlan-id " + def_vln_id[value] + " ")
								script = "untag-port-default-vlan enable " + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\nuntag-port-default-vlan enable " +  " ")
								script = "exit " + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\nexit " + "\n")

	script = " " + "\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write(" " + "\n")

script = "\nend " + "\n\n"
print(script)
with open(outfil, 'a') as outfile:
	outfile.write("\nend " + "\n\n")
with open(outfil, 'a') as outfile:
	outfile.write('\n# ***** end of ' + outfil + ' ***** \n\n')

with open (filename) as f:
	reader = csv.reader(f)
	header_row = next(reader)

	answer = input("\n#### " + switch_id1 + " switch parsed succesfully\n\nPress enter to continue")
	
	fa_mgmt_tg = []
	tagged_int = []
	lag_mlt_id = []
	intrfc__id = []
	intrfc__nm = []
	lacp___ena = []
	lag_mlt_pr = []
	lag_mlt_id = []
	def_vln_id = []
	vlan____id = []

	for row in reader:
		try:
			fa_mgmt_tg.append(row[20])
			tagged_int.append(row[19])
			lag_mlt_id.append(row[22])
			intrfc__id.append(row[13])
			intrfc__nm.append(row[16])
			lacp___ena.append(row[21])
			lag_mlt_pr.append(row[9])
			def_vln_id.append(row[23])
			vlan____id.append(row[24])
            
		except IndexError:
			print("\n\n\t**** WARNING excel header not as expected!!!")
			quit()
	print("\n\n**** List data:")
	print("\t**** fa/fa-mgmt")
	fa_mgmt_tg = [x.encode("ascii", "ignore") for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.decode() for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.strip(" ") for x in fa_mgmt_tg]
	fa_mgmt_tg = [x.lower() for x in fa_mgmt_tg]
	print(fa_mgmt_tg)
	print("\n\t**** tagged")
	tagged_int = [x.encode("ascii", "ignore") for x in tagged_int]
	tagged_int = [x.decode() for x in tagged_int]
	tagged_int = [x.strip(" ") for x in tagged_int]
	tagged_int = [x.lower() for x in tagged_int]
	print(tagged_int)
	print("\n\t**** mlag/smlt id")
	lag_mlt_id = [x.encode("ascii", "ignore") for x in lag_mlt_id]
	lag_mlt_id = [x.decode() for x in lag_mlt_id]
	lag_mlt_id = [x.strip(" ") for x in lag_mlt_id]
	print(lag_mlt_id)
	print("\n\t**** mlag/smlt id from peer switch")
	lag_mlt_pr = [x.encode("ascii", "ignore") for x in lag_mlt_pr]
	lag_mlt_pr = [x.decode() for x in lag_mlt_pr]
	lag_mlt_pr = [x.strip(" ") for x in lag_mlt_pr]
	print(lag_mlt_pr)
	print("\n\t**** interface id")
	intrfc__id = [x.encode("ascii", "ignore") for x in intrfc__id]
	intrfc__id = [x.decode() for x in intrfc__id]
	intrfc__id = [x.strip(" ") for x in intrfc__id]
	print(intrfc__id)
	print("\n\t**** interface name")
	intrfc__nm = [x.encode("ascii", "ignore") for x in intrfc__nm]
	intrfc__nm = [x.decode() for x in intrfc__nm]
	intrfc__nm = [x.strip(" ") for x in intrfc__nm]
	print(intrfc__nm)
	print("\n\t**** lacp")
	lacp___ena = [x.encode("ascii", "ignore") for x in lacp___ena]
	lacp___ena = [x.decode() for x in lacp___ena]
	lacp___ena = [x.strip(" ") for x in lacp___ena]
	lacp___ena = [x.lower() for x in lacp___ena]
	print(lacp___ena)
	print("\n\t**** default vlan id")
	def_vln_id = [x.encode("ascii", "ignore") for x in def_vln_id]
	def_vln_id = [x.decode() for x in def_vln_id]
	def_vln_id = [x.strip(" ") for x in def_vln_id]
	print(def_vln_id)
	print("\n\t**** vlan id")
	vlan____id = [x.encode("ascii", "ignore") for x in vlan____id]
	vlan____id = [x.decode() for x in vlan____id]
	vlan____id = [x.strip(" ") for x in vlan____id]
	vlan____id = [x.replace("n",",") for x in vlan____id]
	vlan____id = [x.rstrip(",") for x in vlan____id]
	vlan____id = [x.replace(" ","") for x in vlan____id]
	print(vlan____id)
	print("\n\t**** vlan id (list that we have to interprete to get all vlan ids)")
	vlan_tmpid = vlan____id [:]
	vlan_nw_id = []
	print(vlan_tmpid)
	print("\n\t**** number of items in vlan id list (number of interfaces in the list)")
	lenvlan_tmpid = len(vlan_tmpid)
	print(lenvlan_tmpid)
	for vlans_int in vlan_tmpid:
		if vlans_int != '':
			print("\n\n\t**** vlan ids for the interface")
			print(vlans_int)
			vlan__list = vlans_int.split(',')
			vlan_nlist = []
			print("\t**** vlan ids as list for the interface")
			print(vlan__list)
			for vlan_value in vlan__list:
				if "-" in vlan_value:
					vlan_range = vlan_value.split('-')
					for vlan____ids in vlan_range:
						a1 = int(vlan_range[0])
						a2 = int(vlan_range[1])
						if a1 > a2:
							print("\n\n\t**** ERROR in vlan range " + str(vlan__list) + " ")
							quit()
					for vlanid in range(a1,(a2+1)):
						vlan_nlist.append(str(vlanid))
				else:
					vlan_nlist.append(vlan_value)
			print("\t**** vlan ids as complete list for the interface")
			vlan_nlist.sort()
			vlan_nlist = [int(x) for x in vlan_nlist]
			vlan_nlist.sort()
			vlan__uniq = []
			[vlan__uniq.append(x) for x in vlan_nlist if x not in vlan__uniq]
			print(vlan__uniq)
			vlan_lst = ''
			for vlnid in vlan__uniq:
				vlan_lst = vlan_lst + str(vlnid) + ','
			vlan_nw_id.append(vlan_lst)
		else:
			vlan_nw_id.append(vlans_int)
	vlan_nw_id = [x.rstrip(",") for x in vlan_nw_id]
	print("\n\n\t**** vlan id (final result)")
	print(vlan_nw_id)	
	print("\n\t**** vlan ids for each interface (final result)")
	for vlan_lst in vlan_nw_id:
		print(vlan_lst)
	vlan____id = vlan_nw_id [:]






answer = input("\nPress enter to continue")
lenfa_mgmt_tg = len(fa_mgmt_tg)
lentagged_int = len(tagged_int)
lenlag_mlt_id = len(lag_mlt_id)
lenintrfc__id = len(intrfc__id)
lenintrfc__nm = len(intrfc__nm)
lenlacp___ena = len(lacp___ena)
lenlag_mlt_pr = len(lag_mlt_pr)
lendef_vln_id = len(def_vln_id)
lenvlan____id = len(vlan____id)
print("\n\n**** Number of list entries (should be all the same):")
print(lenfa_mgmt_tg)
print(lentagged_int)
print(lenlag_mlt_id)
print(lenintrfc__id)
print(lenintrfc__nm)
print(lenlacp___ena)
print(lenlag_mlt_pr)
print(lendef_vln_id)
print(lenvlan____id)


answer = input("\nPress enter to continue with the " + switch_id2 + " switch")

if not "NONE" in switch_id2:
	outfil = "05-3-out-config-lag-mlt-int-" + switch_id2 + ".cfg"
	print("\nThe name of the out-file is " + outfil + " \n")
	answer = input("\nPress enter to continue")
	with open(outfil, 'w') as outfile:
		outfile.write('\n# ***** start of ' + outfil + ' ***** ')
	with open(outfil, 'a') as outfile:
		outfile.write('\n# ***** ' + uni___name + '-Type was selected ***** ')
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

# check if NNI in mltid -> no action
# check if an mlt-id is configured then:
#	no flex-uni on interface level; it has to be set at mlt level
#	if CVLAN-UNI and yes in tagged -> untagged-frames-discard on interface
#	if CVLAN-UNI and no in tagged -> no encapsulation dot1q
#	if Simplified-vIST -> no flex-uni commands at interface or mlt level
#	if lacp-s/lacp-l in lacp -> configure lacp on interface level
#	if lacp in lacp -> configure mltid as lacp-id
#	if lacp in lacp -> disable stp on interface
	script = "\n\n# STEP 1 - Check if MLTid is configured and modify underlying interface"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n# STEP 1 - Check if MLTid is configured and modify underlying interface \n")
	script = "#        - If no MLTid is configured then modify the interface\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("#        - If no MLTid is configured then modify the interface \n")
	for value in range(0,lenlag_mlt_id):
		if "NNI" in lag_mlt_id[value]:
			script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
		else:
			if lag_mlt_id[value]:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				if uni___name != "SimvIST":
					script = "no flex-uni enable " 
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no flex-uni enable\n")
				if uni___name != "FlexUni":
					if "yes" in tagged_int[value]:
						if "0" == def_vln_id[value]:
							script = "untagged-frames-discard " 
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("untagged-frames-discard\n")
					if "no" in tagged_int[value]:
						script = "no encapulation dot1q " 
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("no encapsulation dot1q\n")
				if "lacp-s" in lacp___ena[value]:
					script = "lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time short "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp key " + lag_mlt_id[value] + " aggregation enable timeout-time short " + " \n")
					script = "lacp enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp enable " + " \n")
					script = "# no spanning-tree mstp  force-port-state enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					script = "# y\n" + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# y\n" + "\n")
				if "lacp-l" in lacp___ena[value]:
					script = "lacp key " + lag_mlt_id[value] + " aggregation enable "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp key " + lag_mlt_id[value] + " aggregation enable " + " \n")
					script = "lacp enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("lacp enable " + " \n")
					script = "# no spanning-tree mstp  force-port-state enable " + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					script = "# y\n" + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("# y\n" + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")
			else:
				script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + "\n")
				if uni___name == "CustUni":
					script = "no flex-uni enable " 
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("no flex-uni enable\n")
				if uni___name != "FlexUni":
					if "no" in tagged_int[value]:
						script = "no encapsulation dot1q " 
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("no encapsulation dot1q\n")
				# correction for version 4.10
				# if "yes" in tagged_int[value]:
					# if "0" == def_vln_id[value]:
						# script = "untagged-frames-discard " 
						# print(script)
						# with open(outfil, 'a') as outfile:
							# outfile.write("untagged-frames-discard\n")
				if "lacp-s" in lacp___ena[value]:
					print("\n\n#### ERROR you cannot configure LACP without configuring a LACP-key value !!!" + " ")
					print("\n\t# LACP key missing on interface " + intrfc__id[value] + " in column MLAG/SMLTid !!!" + " \n\n")
					quit()
					# script = "lacp key " + str(value + 1) + " aggregation enable timeout-time short "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp key " + str(value + 1) + " aggregation enable timeout-time short " + " \n")
					# script = "lacp enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp enable " + " \n")
					# script = "# no spanning-tree mstp  force-port-state enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					# script = "# y\n" + "\n"
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# y\n" + "\n")
				if "lacp-l" in lacp___ena[value]:
					print("\n\n#### ERROR you cannot configure LACP without configuring a LACP-key value !!!" + " ")
					print("\n\t# LACP key missing on interface " + intrfc__id[value] + " in column MLAG/SMLTid !!!" + " \n\n")
					quit()
					# script = "lacp key " + str(value + 1) + " aggregation enable "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp key " + str(value + 1) + " aggregation enable " + " \n")
					# script = "lacp enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("lacp enable " + " \n")
					# script = "# no spanning-tree mstp  force-port-state enable " + " "
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# no spanning-tree mstp  force-port-state enable " + " \n")
					# script = "# y\n" + "\n"
					# print(script)
					# with open(outfil, 'a') as outfile:
						# outfile.write("# y\n" + "\n")
				if uni___name != "SimvIST":
					if "fa" in fa_mgmt_tg[value]:
						script = "fa " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa" + "\n")
						script = "fa enable" + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa enable" + "\n")
					if "mgmt" in fa_mgmt_tg[value]:
						script = "fa " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa" + "\n")
						script = "fa enable" + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("fa enable" + "\n")
						if uni___name == "FlexUni":
							if "yes" in tagged_int[value]:
								
								if vlan____id[value]:
									if "," in vlan____id[value]:
										cvid__list = vlan____id[value].split(',')
										for cvid_value in cvid__list:
											cvid_intgr = int(cvid_value)
											script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + "\n")
							if "no" in tagged_int[value]:
								
								if vlan____id[value]:
									if "," in vlan____id[value]:
										cvid__list = vlan____id[value].split(',')
										for cvid_value in cvid__list:
											cvid_intgr = int(cvid_value)
											try:
												script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + "\n")
											except KeyError:
												print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
												print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
											quit()
						if uni___name == "CustUni":
							if "yes" in tagged_int[value]:
								if vlan____id[value]:
									script = "fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + "\n")	
							if "no" in tagged_int[value]:
								
								if vlan____id[value]:
									script = "fa management i-sid " + str(fa_mgmt_is) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("fa management i-sid " + str(fa_mgmt_is) + "\n")
				script = "exit " + "\n"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit" + "\n")

	script = "\n\n# STEP 2 - Configure the MLT interface"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n\n\n# STEP 2 - Configure the MLT interface")
	script = "#        - For SMLT check if VLAN list is coherent\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\n#        - For SMLT check if the VLAN list is coherent \n")

	dup_lag_mlt_id_rght = []

	for value in range(0,lenlag_mlt_id):
		if "NNI" in lag_mlt_id[value]:
			script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
			print(script)
			with open(outfil, 'a') as outfile:
				outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
		else:
			if lag_mlt_id[value]:
				if lag_mlt_id[value] not in dup_lag_mlt_id_rght:
					dup_lag_mlt_id_rght.append(lag_mlt_id[value])
					# print (dup_lag_mlt_id_rght)
					script = "\n\nmlt " + lag_mlt_id[value] + ' enable name MLT--' + lag_mlt_id[value] + ' '
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("\n\nmlt " + lag_mlt_id[value] + ' enable name MLT--' + lag_mlt_id[value] + '\n')
					if not "lacp" in lacp___ena[value]:
						if "yes" in tagged_int[value]:
							script = "mlt " + lag_mlt_id[value] + " encapsulation dot1q " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("mlt " + lag_mlt_id[value] + " encapsulation dot1q " + "\n")
						script = "mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + "\n")
					if lag_mlt_id[value]:
						script = "\ninterface mlt " + lag_mlt_id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("\ninterface mlt " + lag_mlt_id[value] + "\n")
						if lag_mlt_id[value] in lag_mlt_pr:
							script = "smlt " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("smlt" + "\n")





# here you need to specify flex-uni
					if uni___name == "FlexUni":
						script = "flex-uni enable " + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("flex-uni enable" + "\n")
					if "lacp" in lacp___ena[value]:
						script = "lacp enable key " + lag_mlt_id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("lacp enable key " + lag_mlt_id[value] + "\n")
					if uni___name != "SimvIST":
						if "fa" in fa_mgmt_tg[value]:
							script = "fa " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa" + "\n")
							script = "fa enable" + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa enable" + "\n")
						if "mgmt" in fa_mgmt_tg[value]:
							script = "fa " + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa" + "\n")
							script = "fa enable" + " "
							print(script)
							with open(outfil, 'a') as outfile:
								outfile.write("fa enable" + "\n")
							if uni___name == "FlexUni":
								if "yes" in tagged_int[value]:
									
									if vlan____id[value]:
										if "," in vlan____id[value]:
											cvid__list = vlan____id[value].split(',')
											for cvid_value in cvid__list:
												cvid_intgr = int(cvid_value)
												try:
													script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + " c-vid " + (cvid_value) + "\n")
												except KeyError:
													print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
													print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
													quit()
								if "no" in tagged_int[value]:
									
									if vlan____id[value]:
										if "," in vlan____id[value]:
											cvid__list = vlan____id[value].split(',')
											for cvid_value in cvid__list:
												cvid_intgr = int(cvid_value)
												script = "fa management i-sid " + str(vlan__elan[cvid_intgr]) + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("fa management i-sid " + str(vlan__elan[cvid_intgr]) + "\n")	
							if uni___name == "CustUni":
								if "yes" in tagged_int[value]:
									if vlan____id[value]:
										script = "fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("fa management i-sid " + str(fa_mgmt_is) + " c-vid " + (vlan____id[value]) + "\n")	
								if "no" in tagged_int[value]:
									if vlan____id[value]:
										script = "fa management i-sid " + str(fa_mgmt_is) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("fa management i-sid " + str(fa_mgmt_is) + "\n")
					script = "exit " + "\n"
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("exit" + "\n")		
				else:
					if not "lacp" in lacp___ena[value]:
						script = "mlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + " "
						print(script)
						with open(outfil, 'a') as outfile:
							outfile.write("\nmlt " + lag_mlt_id[value] + " member " + intrfc__id[value] + "\n")

# here you need to specify flex-uni
	if uni___name == "FlexUni":
		script = "\n\n# STEP 3 - Configure VLANs on Flex-UNI interfaces \n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 3 - Configure VLANs on Flex-UNI interfaces \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "mgmt" in fa_mgmt_tg[value]:
					if not "fa" in fa_mgmt_tg[value]:
						if vlan____id[value]:
							if "," in vlan____id[value]:
								cvid__list = vlan____id[value].split(',')
								for cvid_value in cvid__list:
									cvid_intgr = int(cvid_value)
									try:
										script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
									except KeyError:
										print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
										print("\n\t# check if the VLANid '" + str(cvid_value) + "' exists in dictionary file!!!" + " \n\n")
										quit()
									if lag_mlt_id[value]:
										if "yes" in tagged_int[value]:
											script = "c-vid " + (cvid_value) + " mlt " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("c-vid " + (cvid_value) + " mlt " + lag_mlt_id[value] + "\n")
									else:
										if "yes" in tagged_int[value]:
											script = "c-vid " + (cvid_value) + " port " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("c-vid " + (cvid_value) + " port " + intrfc__id[value] + "\n")
									script = "exit"
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("exit " + " " + "\n")
							elif vlan____id[value]:
								cvid_intgr = int(vlan____id[value])
								try:
									script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
									print(script)
									with open(outfil, 'a') as outfile:
										outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
								except KeyError:
									print("\n\n#### ERROR VLAN to I-SID mapping not found !!!" + " ")
									print("\n\t# check if the VLANid '" + str(cvid_intgr) + "' exists in dictionary file!!!" + " \n\n")
									quit()
								if lag_mlt_id[value]:
									if "yes" in tagged_int[value]:
										script = "c-vid " + str(cvid_intgr) + " mlt " + lag_mlt_id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("c-vid " + str(cvid_intgr) + " mlt " + lag_mlt_id[value] + "\n")
								else:
									if "yes" in tagged_int[value]:
										script = "c-vid " + str(cvid_intgr) + " port " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("c-vid " + str(cvid_intgr) + " port " + intrfc__id[value] + "\n")
								script = "exit"
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("exit " + " " + "\n")
# if there is a default vlanid not equal 0 defined on a tagged interface/mlt
	if uni___name == "FlexUni":
		script = "\n\n# STEP 4 - Configure untagged VLAN on tagged Flex-UNI interfaces \n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 4 - Configure untagged VLAN on tagged Flex-UNI interfaces \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			elif "0" == def_vln_id[value]:
				script = "# No untagged VLAN is defined on interface " + intrfc__id[value] + " ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No untagged VLAN is defined on interface " + intrfc__id[value] + " ** ")
			elif "yes" in tagged_int[value]:
				cvid_intgr = int(def_vln_id[value])
				script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
				if lag_mlt_id[value]:
					script = "untagged-traffic " + " mlt " + lag_mlt_id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " mlt " + lag_mlt_id[value] + "\n")
				else:
					script = "untagged-traffic " + " port " + intrfc__id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " port " + intrfc__id[value] + "\n")
				script = "exit"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit " + " " + "\n")
			else:
				cvid_intgr = int(def_vln_id[value])
				script = "\ni-sid " + str(vlan__elan[cvid_intgr]) + " "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\ni-sid " + str(vlan__elan[cvid_intgr]) + " " + "\n")
				if lag_mlt_id[value]:
					script = "untagged-traffic " + " mlt " + lag_mlt_id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " mlt " + lag_mlt_id[value] + "\n")
				else:
					script = "untagged-traffic " + " port " + intrfc__id[value] + " "
					print(script)
					with open(outfil, 'a') as outfile:
						outfile.write("untagged-traffic " + " port " + intrfc__id[value] + "\n")
				script = "exit"
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("exit " + " " + "\n")
# here you need to specify the script for cust-uni
	if uni___name != "FlexUni":
		script = "\n\n# STEP 3 - Configure VLANs on CVLAN-UNI interfaces \n\n"
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 3 - Configure VLANs on CVLAN-UNI interfaces \n\n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "mgmt" in fa_mgmt_tg[value]:
					if not "fa" in fa_mgmt_tg[value]:
						if vlan____id[value]:
							if "," in vlan____id[value]:
								cvid__list = vlan____id[value].split(',')
								for cvid_value in cvid__list:
									if lag_mlt_id[value]:
										if "yes" in tagged_int[value]:
											if "lacp" in lacp___ena[value]:
												# check if the lag_mlt_id is more than once in the list
												# then we have to disable lacp on the interface first
												counter = lag_mlt_id.count(lag_mlt_id[value])
												if counter >= 2:
													script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
													script = "interface gigabitethernet " + intrfc__id[value] + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
													script = "no lacp enable "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nno lacp enable")
													script = "exit "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nexit\n")
												
												script = "vlan member add " + (cvid_value) + " " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nvlan member add " + (cvid_value) + " " + intrfc__id[value] + "\n")

												# check if the lag_mlt_id is more than once in the list
												# then we have to enable lacp on the interface again
												counter = lag_mlt_id.count(lag_mlt_id[value])
												if counter >= 2:
													script = "interface gigabitethernet " + intrfc__id[value] + " "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
													script = "lacp enable "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nlacp enable")
													script = "exit "
													print(script)
													with open(outfil, 'a') as outfile:
														outfile.write("\nexit\n")
											else:
												script = "vlan mlt " + (cvid_value) + " " + lag_mlt_id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nvlan mlt " + (cvid_value) + " " + lag_mlt_id[value] + "\n")
									else:
										if "yes" in tagged_int[value]:
											script = "vlan member add " + (cvid_value) + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + (cvid_value) + " " + intrfc__id[value] + "\n")
							elif vlan____id[value]:
								cvid_intgr = int(vlan____id[value])
								if lag_mlt_id[value]:
									if "yes" in tagged_int[value]:
										if "lacp" in lacp___ena[value]:
											# check if the lag_mlt_id is more than once in the list
											# then we have to disable lacp on the interface first
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "no lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nno lacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
											script = "vlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + "\n")

											# check if the lag_mlt_id is more than once in the list
											# then we have to enable lacp on the interface again
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nlacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
										else:
											script = "vlan mlt " + str(cvid_intgr) + " " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan mlt " + str(cvid_intgr) + " " + lag_mlt_id[value] + "\n")
								else:
									if "yes" in tagged_int[value]:
										script = "vlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\nvlan member add " + str(cvid_intgr) + " " + intrfc__id[value] + "\n")

						else:
							if lag_mlt_id[value]:
								if "no" in tagged_int[value]:
									if not "0" == def_vln_id[value]:
										if "lacp" in lacp___ena[value]:
											# check if the lag_mlt_id is more than once in the list
											# then we have to disable lacp on the interface first
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "The LACP key id " + lag_mlt_id[value] + " is used on more than one interface"
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\n# The LACP key id " + lag_mlt_id[value] + " is used on more than one interface\n")
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "no lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nno lacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
											
											script = "vlan member add " + def_vln_id[value] + " " + intrfc__id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan member add " + def_vln_id[value] + " " + intrfc__id[value] + "\n")

											# check if the lag_mlt_id is more than once in the list
											# then we have to enable lacp on the interface again
											counter = lag_mlt_id.count(lag_mlt_id[value])
											if counter >= 2:
												script = "interface gigabitethernet " + intrfc__id[value] + " "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\ninterface gigabitethernet " + intrfc__id[value] + " ")
												script = "lacp enable "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nlacp enable")
												script = "exit "
												print(script)
												with open(outfil, 'a') as outfile:
													outfile.write("\nexit\n")
										else:
											script = "vlan mlt " + def_vln_id[value] + " " + lag_mlt_id[value] + " "
											print(script)
											with open(outfil, 'a') as outfile:
												outfile.write("\nvlan mlt " + def_vln_id[value] + " " + lag_mlt_id[value] + "\n")
							else:
								if "no" in tagged_int[value]:
									if not "0" == def_vln_id[value]:
										script = "vlan member add " + def_vln_id[value] + " " + intrfc__id[value] + " "
										print(script)
										with open(outfil, 'a') as outfile:
											outfile.write("\nvlan member add " + def_vln_id[value] + " " + intrfc__id[value] + "\n")
# if there is a default vlanid not equal 0 defined on a tagged interface/mlt
	if uni___name != "FlexUni":
		script = "\n\n# STEP 4 - Configure untagged VLAN on tagged CVLAN-UNI or Simplified-vIST interfaces  "
		print(script)
		with open(outfil, 'a') as outfile:
			outfile.write("\n\n\n# STEP 4 - Configure untagged VLAN on tagged CVLAN-UNI or Simplified-vIST interfaces  \n\n")
		for value in range(0,lenlag_mlt_id):
			if "NNI" in lag_mlt_id[value]:
				script = "# No action is taken on NNI interface " + intrfc__id[value] + " detected ** "
				print(script)
				with open(outfil, 'a') as outfile:
					outfile.write("\n# No action is taken on NNI interface " + intrfc__id[value] + " detected ** ")
			else:
				if not "0" or "" == def_vln_id[value]:
					if "yes" in tagged_int[value]:
						if not "mgmt" in fa_mgmt_tg[value]:
							if not "fa" in fa_mgmt_tg[value]:
								script = "\n\ninterface gigabitethernet " + intrfc__id[value] + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\n\ninterface gigabitethernet " + intrfc__id[value] + " ")
								script = "default-vlan-id " + def_vln_id[value] + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\ndefault-vlan-id " + def_vln_id[value] + " ")
								script = "untag-port-default-vlan enable " + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\nuntag-port-default-vlan enable " +  " ")
								script = "exit " + " "
								print(script)
								with open(outfil, 'a') as outfile:
									outfile.write("\nexit " + "\n")

	script = " " + "\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write(" " + "\n")

if not "NONE" in switch_id2:
	script = "\nend " + "\n\n"
	print(script)
	with open(outfil, 'a') as outfile:
		outfile.write("\nend " + "\n\n")
	with open(outfil, 'a') as outfile:
		outfile.write('\n# ***** end of ' + outfil + ' ***** \n\n')

	print("\n#### " + switch_id2 + " switch parsed succesfully\n\n")

if not "NONE" in switch_id2:
	print ("\nThese lag/mlt ids are used on the interfaces of switch " + switch_id1 + ":")
	print(dup_lag_mlt_id_lft)
	print ("\nThese lag/mlt ids are used on the interfaces of switch " + switch_id2 + ":")
	print(dup_lag_mlt_id_rght)

	# print(catcherror)

	if str(catcherror) != "[]":
		print("\n\n\t**** WARNING the following SMLT(s) may have a different VLANs configuration: ")
		for smltid in catcherror:
			print("\tVLAN list not the same on SMLT peers for MLTid " + str(smltid) + ", PLEASE review !!!")
	else:
		print("\n\n\t**** INFORM no inconsistencies at VLAN level were found")

answer = input("\nPress enter to continue")

script = "\n ***** program end ***** " + " "
print(script)

