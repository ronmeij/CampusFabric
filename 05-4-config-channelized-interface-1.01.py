##########
# Name: 		config-channelized-interface.py
# Vers:			1.01
# Date: 		230716
# Auth: 		Ronald Meijer
# Pyth: 		version 3
# Dependency:	
# ChangeLog:	1.00 	initial release
##########
# script for channelizing an interface
##########
# Variables:
#	
#	
#	filename	filenames in the list filename
#	location	specifies working directory
#	interface	interface to channelize in x/y-x/z format
#	out_file	name of the out-file 
##########
# Run:      python3 01-config-spbm-x.xx.py
##########

import csv
import glob
# 'location' specifies working directory
# location = 'c:/test/temp/'
import os.path
import re

def answer():
	answer = input("Press enter to continue")

print("\nThis script configures a channelized interface for VOSS:")

# select the interface
interface = (input("\n\nSelect the interface:\n for the channelization\n format is x/y \n or x/y-x/z \n  : [1/10] ") or "1/10")
print("\n")

print("\n**** interface")
interface = interface.strip(" ")
interface = interface.replace(" ","")

print(interface)
out_file = "05-4-channelize-interface.cfg"
print("\nThe name of the out-file is " + out_file + " \n")
with open(out_file, 'w') as outfile:
	outfile.write('\n# ***** start of 05-4-channelize-interface.cfg ***** ')
with open(out_file, 'a') as outfile:
	outfile.write('\n\n')

script = "# user/password: " + " "
print (script)
with open(out_file, 'a') as outfile:
	outfile.write("# user/password \n")
script = "rwa"
print(script)
with open(out_file, 'a') as outfile:
	outfile.write("rwa\n")
script = "rwa"
print(script)
with open(out_file, 'a') as outfile:
	outfile.write("rwa\n")
script = "enable " + " \n"
print (script)
with open(out_file, 'a') as outfile:
	outfile.write("enable " + "\n\n")

script = "configure terminal " + " \n"
print (script)
with open(out_file, 'a') as outfile:
	outfile.write("configure terminal\n\n")

if "-" in interface:
	int_range = interface.split('-')
	# print(int_range)
	int_a1 = (int_range[0])
	int_a2 = (int_range[1])
	# print(int_a1)
	# print(int_a2)
	
	int_b_range = int_a1.split('/')
	# print(int_b_range)
	slt_b = (int_b_range[0])
	int_b = (int_b_range[1])
	# print(slt_b)
	# print(int_b)
	int_c_range = int_a2.split('/')
	# print(int_c_range)
	slt_c = (int_c_range[0])
	int_c = (int_c_range[1])
	# print(slt_c)
	# print(int_c)
	if slt_b != slt_c:
		print("\n\n\t**** ERROR in slot range " + (interface) + " ")
		quit()
	if int(int_b) >= int(int_c):
		print("\n\n\t**** ERROR in interface range " + (interface) + " ")
		quit()
	script = "int gig " + interface + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("int gig " + interface + " \n\n")
	script = "chan enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("chan enable " + " \n")
	int_b = int(int_b)
	int_c = int(int_c)
	for int in range(int_b,(int_c+1)):
		script = "y"
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("y" + "\n")
	script = " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write(" " + "\n")
	for int in range(int_b,(int_c+1)):
		script = "vlan members remove 1 " + slt_b + "/" + str(int) + "/2-" + slt_b + "/" + str(int) + "/4 "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("vlan members remove 1 " + slt_b + "/" + str(int) + "/2-" + slt_b + "/" + str(int) + "/4 \n")
	for int in range(int_b,(int_c+1)):
		script = "\nint gig " + slt_b + "/" + str(int) + "/2-" + slt_b + "/" + str(int) + "/4 "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("\nint gig " + slt_b + "/" + str(int) + "/2-" + slt_b + "/" + str(int) + "/4 \n")
		script = "encap dot1q " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("encap dot1q " + " \n")
		script = "auto-recover enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("auto-recover enable " + " \n")
		script = "sppoof-detect enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spoof-detect enable " + " \n")
		script = "default-vlan 0 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("default-vlan 0 " + " \n")
		script = "flex-uni enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("flex-uni enable " + " \n")
		script = 'name "UNI-port" ' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('name "UNI-port"' + " \n")
		script = "no shutdown " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("no shutdown " + " \n")
		script = "slpp-guard enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("slpp-guard enable " + " \n")
		script = "no spanning-tree mstp  force-port-state enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("no spanning-tree mstp  force-port-state enable " + " \n")
		script = "y" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("y" + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n")

else:
	script = "int gig " + interface + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("int gig " + interface + " \n\n")
	
	script = "chan enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("chan enable " + " \n")
	script = "y"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("y" + "\n")
	
	script = "\nvlan members remove 1 " + interface + "/2-" + interface + "/4 \n"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("\nvlan members remove 1 " + interface + "/2-" + interface + "/4 " + " \n\n")
	
	script = "int gig " + interface + "/2-" + interface + "/4 "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("int gig " + interface + "/2-" + interface + "/4 \n")
	
	script = "encap dot1q " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("encap dot1q " + " \n")
	script = "auto-recover enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("auto-recover enable " + " \n")
	script = "sppoof-detect enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("spoof-detect enable " + " \n")
	script = "default-vlan 0 " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("default-vlan 0 " + " \n")
	script = "flex-uni enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("flex-uni enable " + " \n")
	script = 'name "UNI-port" ' + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write('name "UNI-port"' + " \n")
	script = "no shutdown " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("no shutdown " + " \n")
	script = "slpp-guard enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("slpp-guard enable " + " \n")
	script = "no spanning-tree mstp  force-port-state enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("no spanning-tree mstp  force-port-state enable " + " \n")
	script = "y" + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("y" + " \n")
	script = "exit " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("exit " + " \n")

script = "\nend " + " "
print(script)
with open(out_file, 'a') as outfile:
	outfile.write("\nend " + "\n\n")
script = "save config " + " "
print (script)
with open(out_file, 'a') as outfile:
	outfile.write("save config " + " \n\n")
script = "backup configure 05-4-channelize " + " "
print (script)
with open(out_file, 'a') as outfile:
	outfile.write("backup configure 05-4-channelize " + " \n\n")
with open(out_file, 'a') as outfile:
	outfile.write('# ***** end of 05-4-channelize-interface.cfg ***** \n\n')
script = "\n ***** program end ***** " + " "
print(script)
