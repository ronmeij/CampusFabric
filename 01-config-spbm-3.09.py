##########
# Name: 		01-config-spbm.py
# Vers:			3.09
# Date: 		241203
# Auth: 		Ronald Meijer
# Pyth: 		version 3
# Dependency:	01_spbm_param_detail_TEMPLATE_v3.0
# ChangeLog:	1.92 	added snmp-server trap for authentication and login
# 				1.95 	reformatting
# 				1.96 	added auto-recover-port on NNI MLT ports
#						introduces the use of external 01-banner.txt file
#				1.97	Simplified vIST support
#							uses is_sysname as file-name
#							uses in-band ip address
#							uses clustered settings "yes" (excl i-sid)
#							uses UNI-ports exclusive MLT1
#							uses MLT1 for Simplified-vIST connection
#							uses VLACP for the Simplified-vIST connection
#							uses bmac__virt for lacp smlt-sys-id 
#				1.98	isis auth value may be empty
#				2.00	new excel lay-out
#						prompt name is used as file name for out-file
#						only segmented management is supported
#				2.01	corrected route entries to prevent error in acli
#				2.02	added quotes around authentication string for isis hello
#				2.03	added support for "auto" in ISIS link and MLT speed (version 8.9.0.0)
#				3.00	new excel lay-out, added ftp transferfile host user/password
#				3.01	including passwords for web-server
#				3.02	introduces the use of external 01-motd.txt file
#				3.03	added syslog udp-port as comment
#				3.04	added Lisbon as timezone
#				3.05	added slpp-guard-dis option, slpp-guard enable timeout 0
#				3.06	added support for domain names
#				3.07	detecting in banner and motd file if there are any empty lines
#				3.08	detects the csv file delimiter
#				3.09	added support for multi-area
##########
# script for complete spbm or simplified vIST setup
# 01-banner.txt file contains banner without quotes
# 01-motd.txt file contains motd without quotes
##########
# Variables:
#	bmac__peer 	bmac of the peer switch in cluster
#	bmac__virt 	cluster virtual bmac
#	channelize 	channelized interfaces
#	dns_domnme	ip domain name
#	dns_serv_1	name-server 1
#	dns_serv_2	name-server 2
#	dns_serv_3	name-server 3
#	dvr___func 	dvr function; 'ctrl', 'leaf' or 'none'
#	dvr_clstid 	dvr leaf cluster id
#	dvr_domain 	dvr domain id
#	is__mep_id 	isis mep id
#	is__sys_id 	isis system id
#	is_area_id 	isis area id
#	is_loopbck 	isis loopback ip address
#	is_sysname 	isis system name
#	isis__auth 	isis hello authentication string
#	ist___isid 	i-sid to which the ist vlan maps to
#	ist___name 	selected vIST type; used to determine the settings
#	ist___type 	selector for vIST or Simplified-vIST
#	ist_clustr 	switch is part of an ist cluster configuration ('yes' or 'no')
#	ist_ip_add 	ist ip address with /30
#	ist_peerip 	peer ip of ist cluster
#	ist_subnet 	subnet id of the ist subnet without /30
#	ist_vlanid 	vlan id for ist vlan
#	mgmt__clip 	management clip address x.x.x.x/32
#	mgmt__isid 	i-sid for mgmt vlan
#	mgmt__vlan 	management vlan id and i-sid
#	mgmtvlanip 	management vlan ip x.x.x.x/yy
#	mlt1____id 	mlt1 id
#	mlt1_membr 	mlt1 port members
#	mlt2____id 	mlt2 id
#	mlt2_membr 	mlt2 port member
#	mlt_metric 	l1 mlt metric (default is 100)
#	mstp__prio 	mstp bridge priority (in steps of 4069)
#	nick__name 	spbm nick-name
#	nni__ports 	nni ports (non-mlt)
#	nni_metric 	l1 interface metric (default is 200)
#	ntp_serv_1 	ntp server 1
#	ntp_serv_2 	ntp server 2
#	portmemrem 	list of ports that are to be removed from vlan 1
#	promptname 	switch prompt name
#	slpp_value 	slpp setting (integer for packet-rx-threshold or slpp-guard)
#	snmpsyscon 	snmp syscontact string
#	snmpsysloc 	snmp syslocation string
#	sysloghost 	syslog host 5 configuration
#	time__city 	city in europe used for ntp and dst
#	time__zone 	integer used to select the time zone city from the list
#	trnsfl__ip	ip address transferfile host
#	trnsfl_pwd	ftp user password for transferfile host
#	trnsfl_usr	ftp user name for transferfile host
#	uni__ports 	uni ports
#	vlacp_isis 	vlacp on nni interfaces ('yes' or 'no')
#	hm_areanme	isis home area name	
#	rm_areanme	isis remote area name
#	rm_area_id	isis remote area id
#	rm_nicknme	spbm remote area nick-name
#	rm_issysid	isis remote system-id
#	rm_ho_nnip	isis home and remote nni ports
#	rm_ex_nnip	isis remote exclusive nni ports
#	rm_ho__mlt	isis home and remote nni mlt
#
#	bannerfile	used to store the name of the banner file; 01-banner.txt
#	motd__file	used to store the name of the motd file; 01-motd.txt
#	filename	filenames in the list filename
#	location	specifies working directory
#	fileset		list of the *.csv files in working directory
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

print("\nThis script configures SPBm settings or Simplified vIST for VOSS:")

# select SPBm or Simplified vIST configuration mode
while True:
	try:
		ist___type = int(input("\n\nSelect the IST-type:\n 1 for Simplified-vIST setup (NO SPBm, for PIM deployments)\n 2 for vIST setup (SPBm, for Campus Fabric deployments)\n  : [2] ") or "2")
	except ValueError:
		print("Should be a value from 1 to 2")
		continue
	else:
		if ist___type <= 0:
			print("\nPlease select a value between 1 and 2")
			continue
		if ist___type >= 3:
			print("\nPlease select a value between 1 and 2")
			continue
		# SPBm or Simplified vIST mode was succesfully parsed
		break
if ist___type == 1:
	ist___name = "SimpIST"
elif ist___type == 2:
	ist___name = "NormIST"
print("\n")
# ist-name was successfully set
print ("\nFile(s) found in local directory:")
fileset = [file for file in glob.glob("01*.csv", recursive=False)]

for file in fileset:
	print(" " + file)

filename = input("\nPlease enter the filename: ")

if (filename != ""):
	filename = filename.strip()
else:
	print ("\n\t**** WARNING no file was selected...")
	quit()

if re.findall (".csv", filename):
	print ("\n\tFile name format correct")
else:
	suffix = ".csv"
	filename = filename + suffix
	print ("\n\tFile name format corrected; suffix .csv added")

if os.path.isfile(filename):
	print("\n\t**** INFORM file found\n")
	with open(filename) as f:
		dialect = csv.Sniffer().sniff(f.read(100))
		print("\t**** The delimiter used in the csv file is '" + dialect.delimiter + "' \n\n")
	answer ()
	print("\nColumn \t Header")
else:
	print ("Cannot open file")
	quit()

with open (filename) as f:
	reader = csv.reader(f, delimiter=dialect.delimiter)
	header_row = next(reader)
	for index, column_header in enumerate(header_row):
		print(index, column_header.strip())
	answer()

	while True:
		try:
			time__zone = int(input("\nSelect your city for time-zone:\n" + 
			" 1 for Europe Amsterdam\n 2 for Europe Berlin\n 3 for Europe Lisbon\n" +
			" 4 for Europe London\n 5 for Europe Madrid\n" +
			" 6 for Europe Paris\n 7 for Europe Rome\n" +
			" 8 for Europe Zurich\n 9 for Africa Nairobi\n  : [5] ") or "5")
		except ValueError:
			print("Should be a value from 1 to 9")
			continue
		else:
			if time__zone <= 0:
				print("\nPlease select a value between 1 and 9")
				continue
			if time__zone >= 10:
				print("\nPlease select a value between 1 and 9")
				continue
			#time-zone number was succesfully parsed
			break
	if time__zone == 1:
		time__city = "Europe Amsterdam"
	elif time__zone == 2:
		time__city = "Europe Berlin"
	elif time__zone == 3:
		time__city = "Europe Lisbon"
	elif time__zone == 4:
		time__city = "Europe London"
	elif time__zone == 5:
		time__city = "Europe Madrid"
	elif time__zone == 6:
		time__city = "Europe Paris"
	elif time__zone == 7:
		time__city = "Europe Rome"
	elif time__zone == 8:
		time__city = "Europe Zurich"
	elif time__zone == 9:
		time__city = "Africa Nairobi"
	#time-city was successfully set

	bmac__peer = []
	bmac__virt = []
	channelize = []
	dns_domnme = []
	dns_serv_1 = []
	dns_serv_2 = []
	dns_serv_3 = []
	dvr___func = []
	dvr_clstid = []
	dvr_domain = []
	hm_areanme = []
	is__mep_id = []
	is__sys_id = []
	is_area_id = []
	is_loopbck = []
	is_sysname = []
	isis__auth = []
	ist___isid = []
	ist_clustr = []
	ist_ip_add = []
	ist_peerip = []
	ist_subnet = []
	ist_vlanid = []
	mgmt__clip = []
	mgmt__isid = []
	mgmt__vlan = []
	mgmtvlanip = []
	mlt1____id = []
	mlt1_membr = []
	mlt2____id = []
	mlt2_membr = []
	mlt_metric = []
	mstp__prio = []
	nick__name = []
	nni__ports = []
	nni_metric = []
	ntp_serv_1 = []
	ntp_serv_2 = []
	portmemrem = []
	promptname = []
	rm_areanme = []
	rm_area_id = []
	rm_nicknme = []
	rm_issysid = []
	rm_ho_nnip = []
	rm_ex_nnip = []
	rm_ho__mlt = []
	slpp_value = []
	snmpsyscon = []
	snmpsysloc = []
	sysloghost = []
	trnsfl__ip = []
	trnsfl_pwd = []
	trnsfl_usr = []
	uni__ports = []
	vlacp_isis = []
	for row in reader:
		try:
			bmac__peer.append(row[31])
			bmac__virt.append(row[30])
			channelize.append(row[5])
			dns_domnme.append(row[49])
			dns_serv_1.append(row[50])
			dns_serv_2.append(row[51])
			dns_serv_3.append(row[52])
			dvr___func.append(row[23])
			dvr_clstid.append(row[34])
			dvr_domain.append(row[24])
			hm_areanme.append(row[53])
			is__mep_id.append(row[27])
			is__sys_id.append(row[28])
			is_area_id.append(row[25])
			is_loopbck.append(row[17])
			is_sysname.append(row[14])
			isis__auth.append(row[45])
			ist___isid.append(row[33])
			ist_clustr.append(row[29])
			ist_ip_add.append(row[35])
			ist_peerip.append(row[36])
			ist_subnet.append(row[37])
			ist_vlanid.append(row[32])
			mgmt__clip.append(row[21])
			mgmt__isid.append(row[20])
			mgmt__vlan.append(row[19])
			mgmtvlanip.append(row[18])
			mlt1____id.append(row[11])
			mlt1_membr.append(row[10])
			mlt2____id.append(row[13])
			mlt2_membr.append(row[12])
			mlt_metric.append(row[42])
			mstp__prio.append(row[43])
			nick__name.append(row[26])
			nni__ports.append(row[9])
			nni_metric.append(row[41])
			ntp_serv_1.append(row[38])
			ntp_serv_2.append(row[39])
			portmemrem.append(row[6])
			promptname.append(row[0])
			rm_areanme.append(row[54])
			rm_area_id.append(row[55])
			rm_nicknme.append(row[56])
			rm_issysid.append(row[57])
			rm_ho_nnip.append(row[58])
			rm_ex_nnip.append(row[59])
			rm_ho__mlt.append(row[60])
			slpp_value.append(row[8])
			snmpsyscon.append(row[16])
			snmpsysloc.append(row[15])
			sysloghost.append(row[40])
			uni__ports.append(row[7])
			trnsfl__ip.append(row[46])
			trnsfl_pwd.append(row[48])
			trnsfl_usr.append(row[47])
			vlacp_isis.append(row[44])
		except IndexError:
			print("\n\n\t**** WARNING excel header not as expected!!!")
			quit()
	print("\n\n**** List data from excel.csv file:")
	print("\t**** PromptName:")
	promptname = [x.strip(" ") for x in promptname]
	print(promptname)
	print("n\t**** ISIS-SysName:")
	is_sysname = [x.strip(" ") for x in is_sysname]
	print(is_sysname)
	print("\n\t**** SNMP system location:")
	snmpsysloc = [x.strip(" ") for x in snmpsysloc]
	print(snmpsysloc)
	print("\n\t**** SNMP system contact:")
	snmpsyscon = [x.strip(" ") for x in snmpsyscon]
	print(snmpsyscon)
	print("\n\t**** ip domain-name:")
	dns_domnme = [x.strip(" ") for x in dns_domnme]
	print(dns_domnme)
	print("\n\t**** ip name-server primary:")
	dns_serv_1 = [x.strip(" ") for x in dns_serv_1]
	print(dns_serv_1)
	print("\n\t**** ip name-server secondary:")
	dns_serv_2 = [x.strip(" ") for x in dns_serv_2]
	print(dns_serv_2)
	print("\n\t**** ip name-server tertiary:")
	dns_serv_3 = [x.strip(" ") for x in dns_serv_3]
	print(dns_serv_3)
	print("\n\t**** NTP server 1:")
	ntp_serv_1 = [x.strip(" ") for x in ntp_serv_1]
	print(ntp_serv_1)
	print("\n\t**** NTP server 2:")
	ntp_serv_2 = [x.strip(" ") for x in ntp_serv_2]
	print(ntp_serv_2)
	print("\n\t**** Syslog host:")
	sysloghost = [x.strip(" ") for x in sysloghost]
	print(sysloghost)
	print("\n\t**** TransferFile host IP:")
	trnsfl__ip = [x.strip(" ") for x in trnsfl__ip]
	print(trnsfl__ip)
	print("\n\t**** TransferFile FTP User:")
	trnsfl_usr = [x.strip(" ") for x in trnsfl_usr]
	print(trnsfl_usr)
	print("\n\t**** TransferFile FTP password:")
	trnsfl_pwd = [x.strip(" ") for x in trnsfl_pwd]
	print(trnsfl_pwd)
	print("\n\t**** Channelized interfaces:")
	channelize = [x.strip(" ") for x in channelize]
	channelize = [x.replace("n",",") for x in channelize]
	print(channelize)
	print("\n\t**** All switch interfaces to be removed from vlan 1:")
	portmemrem = [x.strip(" ") for x in portmemrem]
	portmemrem = [x.replace("n",",") for x in portmemrem]
	print(portmemrem)
	print("\n\t**** Switch UNI interfaces:")
	uni__ports = [x.strip(" ") for x in uni__ports]
	uni__ports = [x.replace("n",",") for x in uni__ports]
	print(uni__ports)
	print("\n\t**** SLPP setup on UNI interfaces (slpp-guard, slpp-guard with timeout 0 or slpp packet-rx-threhold):")
	slpp_value = [x.strip(" ") for x in slpp_value]
	slpp_value = [x.lower() for x in slpp_value]
	print(slpp_value)
	print("\n\t**** Switch NNI interfaces:")
	nni__ports = [x.strip(" ") for x in nni__ports]
	nni__ports = [x.replace("n",",") for x in nni__ports]
	print(nni__ports)
	print("\n\t**** Switch NNI MLT-1 port members:")
	mlt1_membr = [x.strip(" ") for x in mlt1_membr]
	mlt1_membr = [x.replace("n",",") for x in mlt1_membr]
	print(mlt1_membr)
	print("\n\t**** Switch NNI MLT-2 port members:")
	mlt2_membr = [x.strip(" ") for x in mlt2_membr]
	mlt2_membr = [x.replace("n",",") for x in mlt2_membr]
	print(mlt2_membr)
	print("\n\t**** Switch NNI MLT-1 id:")
	mlt1____id = [x.strip(" ") for x in mlt1____id]
	print(mlt1____id)
	print("\n\t**** Switch NNI MLT-2 id:")
	mlt2____id = [x.strip(" ") for x in mlt2____id]
	print(mlt2____id)
	print("\n\t**** ISIS metric on NNI interfaces:")
	nni_metric = [x.strip(" ") for x in nni_metric]
	nni_metric = [x.lower() for x in nni_metric]
	print(nni_metric)
	print("\n\t**** ISIS metric on NNI MLT interfaces:")
	mlt_metric = [x.strip(" ") for x in mlt_metric]
	mlt_metric = [x.lower() for x in mlt_metric]
	print(mlt_metric)
	print("\n\t**** Enable VLACP on NNI interfaces (yes/no):")
	vlacp_isis = [x.strip(" ") for x in vlacp_isis]
	vlacp_isis = [x.lower() for x in vlacp_isis]
	print(vlacp_isis)
	print("\n\t**** ISIS hello authentication string for hmac-sha-256:")
	isis__auth = [x.strip(" ") for x in isis__auth]
	print(isis__auth)
	print("\n\t**** Switch is part of a cluster (yes/no):")
	ist_clustr = [x.strip(" ") for x in ist_clustr]
	ist_clustr = [x.lower() for x in ist_clustr]
	print(ist_clustr)
	print("\n\t**** vIST VLAN IP address:")
	ist_ip_add = [x.strip(" ") for x in ist_ip_add]
	print(ist_ip_add)
	print("\n\t**** vIST subnet address:")
	ist_subnet = [x.strip(" ") for x in ist_subnet]
	print(ist_subnet)
	print("\n\t**** vIST peer IP address:")
	ist_peerip = [x.strip(" ") for x in ist_peerip]
	print(ist_peerip)
	print("\n\t**** vIST VLAN id:")
	ist_vlanid = [x.strip(" ") for x in ist_vlanid]
	print(ist_vlanid)
	print("\n\t**** vIST VLAN I-SID:")
	ist___isid = [x.strip(" ") for x in ist___isid]
	print(ist___isid)
	print("\n\t**** ISIS nick-name:")
	nick__name = [x.strip(" ") for x in nick__name]
	nick__name = [x.lower() for x in nick__name]
	print(nick__name)
	print("\n\t**** ISIS system ID (BMAC address):")
	is__sys_id = [x.strip(" ") for x in is__sys_id]
	print(is__sys_id)
	print("\n\t**** Virtual BMAC address:")
	bmac__virt = [x.strip(" ") for x in bmac__virt]
	bmac__virt = [x.lower() for x in bmac__virt]
	print(bmac__virt)
	print("\n\t**** vIST peer BMAC address:")
	bmac__peer = [x.strip(" ") for x in bmac__peer]
	print(bmac__peer)
	print("\n\t**** ISIS source IP address (loopback):")
	is_loopbck = [x.strip(" ") for x in is_loopbck]
	print(is_loopbck)
	print("\n\t**** ISIS area id:")
	is_area_id = [x.strip(" ") for x in is_area_id]
	print(is_area_id)
	print("\n\t**** ISIS MEP-id:")
	is__mep_id = [x.strip(" ") for x in is__mep_id]
	print(is__mep_id)
	print("\n\t**** DVR switch function (none, ctrl, leaf):")
	dvr___func = [x.strip(" ") for x in dvr___func]
	dvr___func = [x.lower() for x in dvr___func]
	print(dvr___func)
	print("\n\t**** DVR domain id:")
	dvr_domain = [x.strip(" ") for x in dvr_domain]
	print(dvr_domain)
	print("\n\t**** DVR cluster id:")
	dvr_clstid = [x.strip(" ") for x in dvr_clstid]
	print(dvr_clstid)
	print("\n\t**** Management CLIP address:")
	mgmt__clip = [x.strip(" ") for x in mgmt__clip]
	print(mgmt__clip)
	print("\n\t**** Management VLAN IP address:")
	mgmtvlanip = [x.strip(" ") for x in mgmtvlanip]
	print(mgmtvlanip)
	print("\n\t**** Management VLAN id:")
	mgmt__vlan = [x.strip(" ") for x in mgmt__vlan]
	print(mgmt__vlan)
	print("\n\t**** Management VLAN I-SID:")
	mgmt__isid = [x.strip(" ") for x in mgmt__isid]
	print(mgmt__isid)
	print("\n\t**** MSTP bridge priority:")
	mstp__prio = [x.strip(" ") for x in mstp__prio]
	print(mstp__prio)
	print("\n\t**** Multi-area HOME area-name")
	hm_areanme = [x.strip(" ") for x in hm_areanme]
	print(hm_areanme)
	print("\n\t**** Multi-area REMOTE area-name")
	rm_areanme = [x.strip(" ") for x in rm_areanme]
	print(rm_areanme)
	print("\n\t**** Multi-area REMOTE area-id")
	rm_area_id = [x.strip(" ") for x in rm_area_id]
	print(rm_area_id)
	print("\n\t**** Multi-area REMOTE nick-name")
	rm_nicknme = [x.strip(" ") for x in rm_nicknme]
	print(rm_nicknme)
	print("\n\t**** Multi-area REMOTE ISIS-sys-id")
	rm_issysid = [x.strip(" ") for x in rm_issysid]
	print(rm_issysid)
	print("\n\t**** Multi-area HOME & REMOTE interfaces")
	rm_ho_nnip = [x.strip(" ") for x in rm_ho_nnip]
	print(rm_ho_nnip)
	print("\n\t**** Multi-area REMOTE exclusively interfaces")
	rm_ex_nnip = [x.strip(" ") for x in rm_ex_nnip]
	print(rm_ex_nnip)
	print("\n\t**** Multi-area HOME & REMOTE MLT-id")
	rm_ho__mlt = [x.strip(" ") for x in rm_ho__mlt]
	print(rm_ho__mlt)
print("\nInput data was correctly parsed from the excel.csv file\n")
answer()
lenbmac__peer = len(bmac__peer)
lenbmac__virt = len(bmac__virt)
lenchannelize = len(channelize)
lendns_domnme = len(dns_domnme)
lendns_serv_1 = len(dns_serv_1)
lendns_serv_2 = len(dns_serv_2)
lendns_serv_3 = len(dns_serv_3)
lendvr___func = len(dvr___func)
lendvr_clstid = len(dvr_clstid)
lendvr_domain = len(dvr_domain)
lenhm_areanme = len(hm_areanme)
lenis__mep_id = len(is__mep_id)
lenis__sys_id = len(is__sys_id)
lenis_area_id = len(is_area_id)
lenis_loopbck = len(is_loopbck)
lenis_sysname = len(is_sysname)
lenisis__auth = len(isis__auth)
lenist___isid = len(ist___isid)
lenist_clustr = len(ist_clustr)
lenist_ip_add = len(ist_ip_add)
lenist_peerip = len(ist_peerip)
lenist_subnet = len(ist_subnet)
lenist_vlanid = len(ist_vlanid)
lenmgmt__clip = len(mgmt__clip)
lenmgmt__isid = len(mgmt__isid)
lenmgmt__vlan = len(mgmt__vlan)
lenmgmtvlanip = len(mgmtvlanip)
lenmlt1____id = len(mlt1____id)
lenmlt1_membr = len(mlt1_membr)
lenmlt2____id = len(mlt2____id)
lenmlt2_membr = len(mlt2_membr)
lenmlt_metric = len(mlt_metric)
lenmstp__prio = len(mstp__prio)
lennick__name = len(nick__name)
lennni__ports = len(nni__ports)
lennni_metric = len(nni_metric)
lenntp_serv_1 = len(ntp_serv_1)
lenntp_serv_2 = len(ntp_serv_2)
lenportmemrem = len(portmemrem)
lenpromptname = len(promptname)
lenrm_areanme = len(rm_areanme)
lenrm_area_id = len(rm_area_id)
lenrm_nicknme = len(rm_nicknme)
lenrm_issysid = len(rm_issysid)
lenrm_ho_nnip = len(rm_ho_nnip)
lenrm_ex_nnip = len(rm_ex_nnip)
lenrm_ho__mlt = len(rm_ho__mlt)
lenslpp_value = len(slpp_value)
lensnmpsyscon = len(snmpsyscon)
lensnmpsysloc = len(snmpsysloc)
lensysloghost = len(sysloghost)
lentrnsfl__ip = len(trnsfl__ip)
lentrnsfl_pwd = len(trnsfl_pwd)
lentrnsfl_usr = len(trnsfl_usr)
lenuni__ports = len(uni__ports)
lenvlacp_isis = len(vlacp_isis)
print(lenbmac__peer)
print(lenbmac__virt)
print(lenchannelize)
print(lendns_domnme)
print(lendns_serv_1)
print(lendns_serv_2)
print(lendns_serv_3)
print(lendvr___func)
print(lendvr_clstid)
print(lendvr_domain)
print(lenhm_areanme)
print(lenis__mep_id)
print(lenis__sys_id)
print(lenis_area_id)
print(lenis_loopbck)
print(lenis_sysname)
print(lenisis__auth)
print(lenist___isid)
print(lenist_clustr)
print(lenist_ip_add)
print(lenist_peerip)
print(lenist_subnet)
print(lenist_vlanid)
print(lenmgmt__clip)
print(lenmgmt__isid)
print(lenmgmt__vlan)
print(lenmgmtvlanip)
print(lenmlt1____id)
print(lenmlt1_membr)
print(lenmlt2____id)
print(lenmlt2_membr)
print(lenmlt_metric)
print(lenmstp__prio)
print(lennick__name)
print(lennni__ports)
print(lennni_metric)
print(lenntp_serv_1)
print(lenntp_serv_2)
print(lenportmemrem)
print(lenpromptname)
print(lenrm_areanme)
print(lenslpp_value)
print(lensnmpsyscon)
print(lensnmpsysloc)
print(lensysloghost)
print(lentrnsfl__ip)
print(lentrnsfl_pwd)
print(lentrnsfl_usr)
print(lenuni__ports)
print(lenvlacp_isis)
print(lenrm_areanme)
print(lenrm_area_id)
print(lenrm_nicknme)
print(lenrm_issysid)
print(lenrm_ho_nnip)
print(lenrm_ex_nnip)
print(lenrm_ho__mlt)
print("\n**** Number of switches in excel.csv file (all numbers above must be equal):")
answer()

for value in range(0,lenpromptname):

	if promptname[value] == "":
		print("\n\n\t**** DATA error: switch must have a prompt name -> excel.csv line " + str(value + 2) + " ")
		quit()
	else:
		out_file = "01-out-spbm-" + promptname[value] + ".cfg"
		print("\nThe name of the out-file is " + out_file + " \n")
		with open(out_file, 'w') as outfile:
			outfile.write('\n# ***** start of 01-out-spbm-' + promptname[value] + '.cfg ***** ')
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
	script = "enable " + " "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("enable " + "\n\n")

	script = "configure terminal " + " "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("configure terminal\n\n")

	script = "prompt " + promptname[value] + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("prompt " + promptname[value] + " \n\n")

	if ist___name == "NormIST":
		script = "spbm " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spbm " + " \n")
		script = "spbm ethertype 0x8100 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spbm ethertype 0x8100 " + " \n")

	script = "sys mtu 9600 " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("sys mtu 9600 " + " \n")

	script = "clock time-zone " + time__city + " "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("clock time-zone " + time__city + " \n")

	if snmpsyscon[value]:
		script = 'snmp-server contact "' + snmpsyscon[value] + '" '
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write('snmp-server contact "' + snmpsyscon[value] + '" \n')
	if snmpsysloc[value]:
		script = 'snmp-server location "' + snmpsysloc[value] + '" ' 
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write('snmp-server location "' + snmpsysloc[value] + '" \n\n')

	script = "snmp-server authentication-trap enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("snmp-server authentication-trap enable " + " \n")
	script = "snmp-server login-success-trap enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("snmp-server login-success-trap enable " + " \n\n")

	script = "web-server enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("web-server enable " + " \n")
	script = "password"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("password" + "\n")
	script = "password"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("password" + "\n")
	script = "12345678"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("12345678" + "\n")
	script = "12345678"
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("12345678" + "\n")
	script = "web-server secure-only " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("web-server secure-only " + " \n\n")

	if sysloghost[value]:
		script = "# web-server help-tftp " + sysloghost[value] + ":/FabricEnginev9.0.0_HELP_EDM "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("# web-server help-tftp " + sysloghost[value] + ":/FabricEnginev9.0.0_HELP_EDM \n\n")

	if trnsfl__ip[value]:
		script = "logging transferFile 1 address " + trnsfl__ip[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("logging transferFile 1 address " + trnsfl__ip[value] + " \n")
		script = "logging transferFile 1 filename-prefix " + promptname[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("logging transferFile 1 filename-prefix " + promptname[value] + " \n\n")
		if trnsfl_usr[value]:
			script = 'boot config host user "' + trnsfl_usr[value] + '" '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('boot config host user "' + trnsfl_usr[value] + '" \n')
			if trnsfl_pwd[value] == "":
				print("\n\n\t**** DATA error: transferfile ftp user without password is not supported -> excel.csv line " + str(value + 2) + " ")
				quit()
			else:				
				script = 'boot config host password "' + trnsfl_pwd[value] + '" '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('boot config host password "' + trnsfl_pwd[value] + '" \n\n')

	if sysloghost[value]:
		script = "syslog host 5 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("syslog host 5 " + " \n")
		script = "syslog host 5 address " + sysloghost[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("syslog host 5 address " + sysloghost[value] + " \n")
# UniBern requires udp-port 529
		# script = "syslog host 5 udp-port 529 " + " "
		# print (script)
		# with open(out_file, 'a') as outfile:
			# outfile.write("syslog host 5 udp-port 529 " + " \n")
		script = "syslog host 5 severity info warning error fatal " + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("syslog host 5 severity info warning error fatal " + " \n")
		script = "syslog host 5 enable " + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("syslog host 5 enable " + " \n\n")

	if dns_domnme[value]:
		script = 'ip domain-name "' + dns_domnme[value] + '" '
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('ip domain-name "' + dns_domnme[value] + '" \n')
		if dns_serv_1[value]:
			script = "ip name-server primary " + dns_serv_1[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ip name-server primary " + dns_serv_1[value] + " \n")
		if dns_serv_2[value]:
			script = "ip name-server secondary " + dns_serv_2[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ip name-server secondary " + dns_serv_2[value] + " \n")
		if dns_serv_3[value]:
			script = "ip name-server tertiary " + dns_serv_3[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ip name-server tertiary " + dns_serv_3[value] + " \n\n")

	if ntp_serv_1[value]:
		script = "ntp server " + ntp_serv_1[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("ntp server " + ntp_serv_1[value] + " \n")
		if ntp_serv_2[value]:
			script = "ntp server " + ntp_serv_2[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ntp server " + ntp_serv_2[value] + " \n")
			script = "ntp " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ntp " + " \n\n")
		else:
			script = "ntp " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ntp " + " \n\n")

	bannerfile = '01-banner.txt'
	try:
		with open(bannerfile, encoding='utf-8') as f_obj:
			script = "banner custom " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("banner custom " + " \n")
			for line in f_obj:
				if line.strip() == "":
					script = "# empty line in 01-banner.txt file is suppressed"
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("# empty line in 01-banner.txt file is suppressed \n")
				else:
					script = 'banner "' + line.strip() + '"'
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('banner "' + line.strip() + '"\n')
			with open(out_file, 'a') as outfile:
				outfile.write(" \n")
	except FileNotFoundError:
		script = "# no custom 01-banner.txt file found in directory"
		print(script)
		answer()
		with open(out_file, 'a') as outfile:
			outfile.write("# no custom 01-banner.txt file found in directory" + " \n\n")

	motd__file = '01-motd.txt'
	try:
		with open(motd__file, encoding='utf-8') as f_obj:
			script = "banner displaymotd " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("banner displaymotd " + " \n")
			for line in f_obj:
				if line.strip() == "":
					script = "# empty line in 01-motd.txt file is suppressed"
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("# empty line in 01-motd.txt file is suppressed \n")
				else:
					script = 'banner motd "' + line.strip() + '"'
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('banner motd "' + line.strip() + '"\n')
			with open(out_file, 'a') as outfile:
				outfile.write(" \n")
	except FileNotFoundError:
		script = "# no custom 01-motd.txt file found in directory"
		print(script)
		answer()
		with open(out_file, 'a') as outfile:
			outfile.write("# no custom 01-motd.txt file found in directory" + " \n\n")

	script = "no password access-level l1 " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("no password access-level l1 " + " \n")
	script = "no password access-level l2 " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("no password access-level l2 " + " \n")
	script = "no password access-level l3 " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("no password access-level l3 " + " \n\n")

	script = "vlacp enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("vlacp enable " + " \n\n")

	script = "lacp enable " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("lacp enable " + " \n")
	if "yes" in ist_clustr[value]:
		if bmac__virt[value]:
			script = "lacp smlt-sys-id " + bmac__virt[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("lacp smlt-sys-id " + bmac__virt[value] + " \n\n")
		else:
			print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify a virtual bmac -> excel.csv line " + str(value + 2) + " ")
			quit()

	if channelize[value]:
		script = "interface gigabitethernet " + channelize[value]
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("interface gigabitethernet " + channelize[value] + " \n")
		script = "channelize enable" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("channelize enable" + " \n")
		chan__list = channelize[value].split(',')
		channelint = len(chan__list)
		for chan_value in chan__list:
			script = "y "
			print(script)
			with open(out_file, 'a') as outfile:
			    outfile.write("y" + "\n")
		with open(out_file, 'a') as outfile:
			outfile.write(" " + "\n")

	if portmemrem[value]:
		script = "vlan members remove 1 " + portmemrem[value] + " portmember"
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("vlan members remove 1 " + portmemrem[value] + " portmember \n\n")
	else:
		print("\n\n\t**** DATA error: all switch ports (including channelized) must be removed from vlan 1 -> excel.csv line " + str(value + 2) + " ")
		quit()

	if mstp__prio[value]:
		script = "spanning-tree mstp priority " + mstp__prio[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spanning-tree mstp priority " + mstp__prio[value] + " \n\n")
	else:
		script = "spanning-tree mstp priority 28672" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spanning-tree mstp priority 28672" + " \n\n")

	script = "auto-recover-delay 300" + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("auto-recover-delay 300" + " \n\n")

	if mgmt__clip[value]:
		script = "mgmt clip vrf GlobalRouter" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("mgmt clip vrf GlobalRouter" + " \n")
		script = "ip address " + mgmt__clip[value] + "/32 "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("ip address " + mgmt__clip[value] + "/32 \n")
		script = "enable " + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("enable " + " \n")
		script = "force-topology-ip " + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("force-topology-ip " + " \n")
		script = "exit " + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")

	if mgmtvlanip[value]:
		if mgmt__vlan[value] == "":
			print("\n\n\t**** DATA error: with mgmt vlan ip you must specify a mgmt vlan id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:		
			if mgmt__isid[value] == "":
				print("\n\n\t**** DATA error: with mgmt vlan ip you must specify an i-sid for mgmt vlan -> excel.csv line " + str(value + 2) + " ")
				quit()
			else:
				if "leaf" in dvr___func[value]:
					script = "mgmt vlan i-sid " + mgmt__isid[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("mgmt vlan i-sid " + mgmt__isid[value] + " \n")
					script = "ip address " + mgmtvlanip[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("ip address " + mgmtvlanip[value] + " \n")
					script = "# ip route <net>/<mask> next-hop <nhop> [weight val]" + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("# ip route <net>/<mask> next-hop <nhop> [weight val]" + " \n")
					script = "enable " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("enable " + " \n")
					script = "# force-topology-ip " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("# force-topology-ip " + " \n")
					script = "exit " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("exit " + " \n\n")
				else:
					script = 'vlan create ' + mgmt__vlan[value] + ' name "mgmt vlan" type port-mstprstp 0 '
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('vlan create ' + mgmt__vlan[value] + ' name "mgmt vlan" type port-mstprstp 0 \n')
					script = "vlan i-sid " + mgmt__vlan[value] + " " + mgmt__isid[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("vlan i-sid " + mgmt__vlan[value] + " " + mgmt__isid[value] + " \n\n")
					script = "slpp vid " + mgmt__vlan[value] + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("slpp vid " + mgmt__vlan[value] + " \n\n")
					script = "mgmt vlan " + mgmt__vlan[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("mgmt vlan " + mgmt__vlan[value] + " \n")
					script = "ip address " + mgmtvlanip[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("ip address " + mgmtvlanip[value] + " \n")
					script = "# ip route <net>/<mask> next-hop <nhop> [weight val]" + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("# ip route <net>/<mask> next-hop <nhop> [weight val]" + " \n")
					script = "enable " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("enable " + " \n")
					script = "# force-topology-ip " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("# force-topology-ip " + " \n")
					script = "exit " + " "
					print (script)
					with open(out_file, 'a') as outfile:
						outfile.write("exit " + " \n\n")

		script = "no mgmt dhcp-client" + " "
		print (script)
		with open(out_file, 'a') as outfile:
			outfile.write("no mgmt dhcp-client" + " \n\n")

	if mlt1_membr[value]:
		if mlt1____id[value] == "":
			print("\n\n\t**** DATA error: mlt-1 has members but no mlt id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:
			script = "mlt " + mlt1____id[value] + " enable"
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt1____id[value] + " enable \n")
			script = "mlt " + mlt1____id[value] + " member " + mlt1_membr[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt1____id[value] + " member " + mlt1_membr[value] + " \n")
			script = "mlt " + mlt1____id[value] + " encapsulation dot1q"
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt1____id[value] + " encapsulation dot1q \n\n")

	if mlt2_membr[value]:
		if mlt2____id[value] == "":
			print("\n\n\t**** DATA error: mlt-2 has members but no mlt id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:
			script = "mlt " + mlt2____id[value] + " enable"
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt2____id[value] + " enable \n")
			script = "mlt " + mlt2____id[value] + " member " + mlt2_membr[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt2____id[value] + " member " + mlt2_membr[value] + " \n")
			script = "mlt " + mlt2____id[value] + " encapsulation dot1q"
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("mlt " + mlt2____id[value] + " encapsulation dot1q \n\n")

	if not "leaf" in dvr___func[value]:
		script = "ip arp request-threshold 100 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("ip arp request-threshold 100 " + " \n\n")
		script = "slpp enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("slpp enable " + " \n\n")

	if ist___name == "NormIST":
		script = "router isis " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("router isis " + " \n")
		script = "spbm 1 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spbm 1 " + " \n")
		if nick__name[value] == "":
			print("\n\n\t**** DATA error: for spbm configurations you must specify a unique nick-name -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:		
			script = "spbm 1 nick-name " + nick__name[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spbm 1 nick-name " + nick__name[value] + " \n")
		script = "spbm 1 b-vid " + "4051" + "-" + "4052" + " primary " + "4051" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spbm 1 b-vid " + "4051" + "-" + "4052" + " primary " + "4051" + " \n")
		if not "leaf" in dvr___func[value]:
			script = "spbm 1 multicast enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spbm 1 multicast enable " + " \n")
		if is_loopbck[value]:
			script = "spbm 1 ip enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spbm 1 ip enable " + " \n")
		if "yes" in ist_clustr[value]:
			if bmac__virt[value] == "":
				print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify a virtual bmac -> excel.csv line " + str(value + 2) + " ")
				quit()
			else:		
				script = "spbm 1 smlt-virtual-bmac " + bmac__virt[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("spbm 1 smlt-virtual-bmac " + bmac__virt[value] + " \n")
			if bmac__peer[value] == "":
				print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify the peer system-id -> excel.csv line " + str(value + 2) + " ")
				quit()
			else:		
				script = "spbm 1 smlt-peer-system-id " + bmac__peer[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("spbm 1 smlt-peer-system-id " + bmac__peer[value] + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")

	if ist___name == "NormIST":
		if not "leaf" in dvr___func[value]:
			if "yes" in ist_clustr[value]:
				if ist_subnet[value]:
					script = 'ip prefix-list "vIST" ' + ist_subnet[value] + " id 1 ge 30 le 30 "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('ip prefix-list "vIST" ' + ist_subnet[value] + " id 1 ge 30 le 30 \n\n")
				else:
					print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify the ist subnet -> excel.csv line " + str(value + 2) + " ")
					quit()					
				if ist_vlanid[value]:
					script = "vlan create " + ist_vlanid[value] + " name VLAN-vIST type port-mstprstp 0"
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("vlan create " + ist_vlanid[value] + " name VLAN-vIST type port-mstprstp 0 \n")
				else:
					print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify the ist vlan id -> excel.csv line " + str(value + 2) + " ")
					quit()					
				if ist___isid[value]:
					script = "vlan i-sid " + ist_vlanid[value] + ' ' + ist___isid[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("vlan i-sid " + ist_vlanid[value] + ' ' + ist___isid[value] + " \n")
				else:
					print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify the ist vlan i-sid -> excel.csv line " + str(value + 2) + " ")
					quit()
				script = "interface vlan " + ist_vlanid[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("interface vlan " + ist_vlanid[value] + " \n")
				if ist_ip_add[value]:
					script = "ip address " + ist_ip_add[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("ip address " + ist_ip_add[value] + " \n")
				else:
					print("\n\n\t**** DATA error: for switch vIST (cluster) you must specify the ist vlan ip address -> excel.csv line " + str(value + 2) + " ")
					quit()
				script = "exit " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("exit " + " \n\n")

# setup for simplified vist - ist vlan
	if ist___name == "SimpIST":
		if "yes" in ist_clustr[value]:
			if ist_subnet[value]:
				script = 'ip prefix-list "vIST" ' + ist_subnet[value] + " id 1 ge 30 le 30 "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('ip prefix-list "vIST" ' + ist_subnet[value] + " id 1 ge 30 le 30 \n\n")
			else:
				print("\n\n\t**** DATA error: for switch IST (cluster) you must specify the ist subnet -> excel.csv line " + str(value + 2) + " ")
				quit()	
			if ist_vlanid[value]:
				script = "vlan create " + ist_vlanid[value] + " name VLAN-IST type port-mstprstp 0"
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("vlan create " + ist_vlanid[value] + " name VLAN-IST type port-mstprstp 0 \n")
			else:
				print("\n\n\t**** DATA error: for switch IST (cluster) you must specify the ist vlan id -> excel.csv line " + str(value + 2) + " ")
				quit()
			script = "interface vlan " + ist_vlanid[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("interface vlan " + ist_vlanid[value] + " \n")
			if ist_ip_add[value]:
				script = "ip address " + ist_ip_add[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("ip address " + ist_ip_add[value] + " \n")
			else:
				print("\n\n\t**** DATA error: for switch IST (cluster) you must specify the ist vlan ip address -> excel.csv line " + str(value + 2) + " ")
				quit()
			script = "exit " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("exit " + " \n\n")

	if ist___name == "NormIST":
		script = "vlan create " + "4051" + ' name "B-VLAN-1" type spbm-bvlan '
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("vlan create " + "4051" + ' name "B-VLAN-1" type spbm-bvlan \n')
		script = "vlan create " + "4052" + ' name "B-VLAN-2" type spbm-bvlan '
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("vlan create " + "4052" + ' name "B-VLAN-2" type spbm-bvlan \n\n')

	if not "leaf" in dvr___func[value]:
		if "yes" in ist_clustr[value]:
			if ist_peerip[value]:
				script = 'virtual-ist peer-ip ' + ist_peerip[value] + " vlan " + ist_vlanid[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('virtual-ist peer-ip ' + ist_peerip[value] + " vlan " + ist_vlanid[value] + " \n\n")
			else:
				print("\n\n\t**** DATA error: for switch (v)IST (cluster) you must specify the peer ist ip address -> excel.csv line " + str(value + 2) + " ")
				quit()

	if uni__ports[value]:
		script = "interface gigabitethernet " + uni__ports[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("interface gigabitethernet " + uni__ports[value] + " \n")
		script = "encapsulation dot1q " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("encapsulation dot1q " + " \n")
		script = 'name "UNI-Port"' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('name "UNI-port"' + " \n")
		script = "spoof-detect enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spoof-detect enable " + " \n")
		script = "auto-recover-port enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("auto-recover-port enable " + " \n")
		if "slpp-guard-dis" in slpp_value[value]:
			script = "slpp-guard enable timeout 0" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("slpp-guard enable timeout 0 " + " \n")
		elif "slpp-guard" in slpp_value[value]:
			script = "slpp-guard enable" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("slpp-guard enable " + " \n")
		else:
			script = "slpp packet-rx-threshold" + slpp_value[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("slpp packet-rx-threshold " + slpp_value[value] + " \n")
			script = "slpp packet-rx " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("slpp packet-rx " + " \n")
		script = 'default-vlan-id 0' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('default-vlan-id 0' + " \n")
		if ist___name == "NormIST":
			script = "flex-uni enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("flex-uni enable " + " \n")
			script = "no shutdown " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("no shutdown " + " \n")
			script = "no spanning-tree mstp force-port-state enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("no spanning-tree mstp force-port-state enable " + " \n")
			script = "y"
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("y\n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")
	else:
		print("\n\n\t**** DATA warning: no uni ports are defined on this switch -> excel.csv line " + str(value + 2) + " ")
		answer()

	if "ctrl" in dvr___func[value]:
		if dvr_domain[value] == "":
			print("\n\n\t**** DATA error: if the switch is a dvr controller you must specify a dvr domain id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:
			script = "dvr controller " + dvr_domain[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("dvr controller " + dvr_domain[value] + " \n\n")

	if "leaf" in dvr___func[value]:
		if dvr_domain[value] == "":
			print("\n\n\t**** DATA error: if the switch is a dvr leaf you must specify the dvr domain id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:
			script = "dvr leaf " + dvr_domain[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("dvr leaf " + dvr_domain[value] + " \n\n")
		if "yes" in ist_clustr[value]:
			if ist_peerip[value]:
				script = "dvr leaf virtual-ist " + ist_ip_add[value] + ' peer-ip ' + ist_peerip[value] + ' cluster-id ' + dvr_clstid[value] + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("dvr leaf virtual-ist " + ist_ip_add[value] + ' peer-ip ' + ist_peerip[value] + ' cluster-id ' + dvr_clstid[value] + ' \n\n')
			else:
				print("\n\n\t**** DATA error: for a dvr leaf vIST (cluster) you must specify the peer ist ip address -> excel.csv line " + str(value + 2) + " ")
				quit()

	if nni__ports[value]:
		script = "interface gigabitethernet " + nni__ports[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("interface gigabitethernet " + nni__ports[value] + " \n")
		script = "encapsulation dot1q " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("encapsulation dot1q " + " \n")
		script = "untagged-frames-discard " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("untagged-frames-discard " + " \n")
		script = 'name "NNI-Port"' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('name "NNI-port"' + " \n")
		script = "spoof-detect enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spoof-detect enable " + " \n")
		script = "auto-recover-port enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("auto-recover-port enable " + " \n")
		if "yes" in vlacp_isis[value]:
			script = 'vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' \n')
			script = 'vlacp enable ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('vlacp enable ' + ' \n')
		script = 'default-vlan-id 0' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('default-vlan-id 0' + " \n")
		script = "no shutdown " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("no shutdown " + " \n")
		script = "isis " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis " + " \n")
		script = "isis spbm 1" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis spbm 1" + " \n")
		if "auto" in nni_metric[value]:
			script = "isis spbm 1 l1-metric " + "auto" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + "auto" + " \n")
		elif nni_metric[value]:
			script = "isis spbm 1 l1-metric " + nni_metric[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + nni_metric[value] + " \n")
		else:
			script = "isis spbm 1 l1-metric " + "200" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + "200" + " \n")
		if isis__auth[value]:
			script = 'isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
		script = "isis enable" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis enable" + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")
	else:
		print("\n\n\t**** DATA warning: no nni ports are defined on this switch -> excel.csv line " + str(value + 2) + " ")
		answer()

	if ist___name == "NormIST":
		if mlt1_membr[value]:
			script = "interface mlt " + mlt1____id[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("interface mlt " + mlt1____id[value] + " \n")
			script = "isis " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis " + " \n")
			script = "isis spbm 1" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1" + " \n")
			if "auto" in mlt_metric[value]:
				script = "isis spbm 1 l1-metric " + "auto" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis spbm 1 l1-metric " + "auto" + " \n")
			elif mlt_metric[value]:
				script = "isis spbm 1 l1-metric " + mlt_metric[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis spbm 1 l1-metric " + mlt_metric[value] + " \n")
			else:
				script = "isis spbm 1 l1-metric " + "100" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis spbm 1 l1-metric " + "100" + " \n")
			if isis__auth[value]:
				script = 'isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
			script = "isis enable" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis enable" + " \n")
			script = "exit " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("exit " + " \n\n")

# setup for simplified vist - ist mlt setup
	if ist___name == "SimpIST":
		if "yes" in ist_clustr[value]:
			if mlt1_membr[value]:
				script = "interface mlt " + mlt1____id[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("interface mlt " + mlt1____id[value] + " \n")
				script = "virtual-ist enable " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("virtual-ist enable " + " \n")
				script = "exit " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("exit " + " \n\n")

	if mlt2_membr[value]:
		script = "interface mlt " + mlt2____id[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("interface mlt " + mlt2____id[value] + " \n")
		script = "isis " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis " + " \n")
		script = "isis spbm 1" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis spbm 1" + " \n")
		if "auto" in mlt_metric[value]:
			script = "isis spbm 1 l1-metric " + "auto" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + "auto" + " \n")
		elif mlt_metric[value]:
			script = "isis spbm 1 l1-metric " + mlt_metric[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + mlt_metric[value] + " \n")
		else:
			script = "isis spbm 1 l1-metric " + "100" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("isis spbm 1 l1-metric " + "100" + " \n")
		if isis__auth[value]:
			script = 'isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('isis hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
		script = "isis enable" + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("isis enable" + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")

	if ist___name == "NormIST":
		if mlt1_membr[value]:
			script = "interface gigabitethernet " + mlt1_membr[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("interface gigabitethernet " + mlt1_membr[value] + " \n")
			script = "spoof-detect enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spoof-detect enable " + " \n")
			script = "auto-recover-port enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("auto-recover-port enable " + " \n")
			script = 'name "NNI-MLT' + mlt1____id[value] + '" '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('name "NNI-MLT' + mlt1____id[value] + '" \n')
			script = "untagged-frames-discard " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("untagged-frames-discard " + " \n")
			if "yes" in vlacp_isis[value]:
				script = 'vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' \n')
				script = 'vlacp enable ' + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('vlacp enable ' + ' \n')
			script = 'default-vlan-id 0' + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('default-vlan-id 0' + " \n")
			script = "no shutdown " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("no shutdown " + " \n")
			script = "exit " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("exit " + " \n\n")

# setup for simplified vist - mlt interfaces
	if ist___name == "SimpIST":
		if mlt1_membr[value]:
			script = "interface gigabitethernet " + mlt1_membr[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("interface gigabitethernet " + mlt1_membr[value] + " \n")
			script = "spoof-detect enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spoof-detect enable " + " \n")
			script = "auto-recover-port enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("auto-recover-port enable " + " \n")
			script = 'name "vIST-MLT' + mlt1____id[value] + '" '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('name "vIST-MLT' + mlt1____id[value] + '" \n')
			script = "untagged-frames-discard " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("untagged-frames-discard " + " \n")
			if "yes" in vlacp_isis[value]:
				script = 'vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' \n')
				script = 'vlacp enable ' + ' '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('vlacp enable ' + ' \n')
			script = 'default-vlan-id 0' + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('default-vlan-id 0' + " \n")
			script = "no shutdown " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("no shutdown " + " \n")
			script = "exit " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("exit " + " \n\n")

	if mlt2_membr[value]:
		script = "interface gigabitethernet " + mlt2_membr[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("interface gigabitethernet " + mlt2_membr[value] + " \n")
		script = "spoof-detect enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("spoof-detect enable " + " \n")
		script = "auto-recover-port enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("auto-recover-port enable " + " \n")
		script = 'name "NNI-MLT' + mlt2____id[value] + '" '
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('name "NNI-MLT' + mlt2____id[value] + '" \n')
		script = "untagged-frames-discard " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("untagged-frames-discard " + " \n")
		if "yes" in vlacp_isis[value]:
			script = 'vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('vlacp fast-periodic-time 500 timeout short timeout-scale 5 funcmac-addr 01:80:c2:00:00:0f ' + ' \n')
			script = 'vlacp enable ' + ' '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('vlacp enable ' + ' \n')
		script = 'default-vlan-id 0' + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write('default-vlan-id 0' + " \n")
		script = "no shutdown " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("no shutdown " + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")

	if not "leaf" in dvr___func[value]:
		if "yes" in ist_clustr[value]:
			script = 'route-map "suppressIST" 1'
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('route-map "suppressIST" 1 \n')
			script = 'no permit'
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('no permit \n')
			script = 'enable '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('enable \n')
			script = 'match network "vIST" '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('match network "vIST" \n')
			script = 'route-map "suppressIST" 2 '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('route-map "suppressIST" 2 \n')
			script = 'permit '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('permit \n')
			script = 'enable '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('enable \n')
			script = 'match protocol local '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('match protocol local \n')
			script = 'exit '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('exit \n\n')

	if ist___name == "NormIST":
		if not "leaf" in dvr___func[value]:
			if is_loopbck[value]:
				script = 'interface loopback 1'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('interface loopback 1 \n')
				script = 'ip address 1 ' + is_loopbck[value] + '/32'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('ip address 1 ' + is_loopbck[value] + '/32 \n')
				script = 'exit '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('exit \n\n')
			else:
				print("\n\n\t**** DATA warning: for a spbm switch it is recommended to have an isis ip-source (loopback) address -> excel.csv line " + str(value + 2) + " ")
				answer()

	if ist___name == "NormIST":
		script = "router isis " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("router isis " + " \n")
		if is_sysname[value] == "":
			script = "sys-name " + promptname[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("sys-name " + promptname[value] + " \n")
		else:		
			script = "sys-name " + is_sysname[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("sys-name " + is_sysname[value] + " \n")
		if not "leaf" in dvr___func[value]:
			script = "ip-source-address " + is_loopbck[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("ip-source-address " + is_loopbck[value] + " \n")
		script = "is-type l1 " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("is-type l1 " + " \n")
		script = "system-id " + is__sys_id[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("system-id " + is__sys_id[value] + " \n")
		script = "manual-area " + is_area_id[value] + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("manual-area " + is_area_id[value] + " \n")		
		if hm_areanme[value]:
			script = "# **** Multi-area configuration is detected" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("# **** Multi-area configuration is detected" + " \n")
			script = "area-name " + hm_areanme[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("area-name " + hm_areanme[value] + " \n")
		script = "exit " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("exit " + " \n\n")

		script = "router isis enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("router isis enable " + " \n\n")

		if hm_areanme[value]:
			script = "# **** Multi-area configuration is detected" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("# **** Multi-area configuration is detected" + " \n\n")
			script = "router isis remote" + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("router isis remote" + " \n")
			script = "spbm 1 nick-name " + rm_nicknme[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("spbm 1 nick-name " + rm_nicknme[value] + " \n")
			script = "system-id " + rm_issysid[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("system-id " + rm_issysid[value] + " \n")
			script = "manual-area " + rm_area_id[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("manual-area " + rm_area_id[value] + " \n")		
			script = "area-name " + rm_areanme[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("area-name " + rm_areanme[value] + " \n")
			script = "exit " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("exit " + " \n\n")
			script = "router isis remote enable " + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("router isis remote enable " + " \n\n")		

			if rm_ho_nnip[value]:
				script = "interface gigabitethernet " + rm_ho_nnip[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("interface gigabitethernet " + rm_ho_nnip[value] + " \n")
				script = "isis remote" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote" + " \n")
				script = "isis remote spbm 1" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote spbm 1" + " \n")
				if "auto" in nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + "auto" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + "auto" + " \n")
				elif nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + nni_metric[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + nni_metric[value] + " \n")
				else:
					script = "isis spbm 1 l1-metric " + "100" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis spbm 1 l1-metric " + "100" + " \n")
				if isis__auth[value]:
					script = 'isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
				script = "isis remote enable" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote enable" + " \n")
				script = "exit " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("exit " + " \n\n")

			if rm_ex_nnip[value]:
				script = "interface gigabitethernet " + rm_ex_nnip[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("interface gigabitethernet " + rm_ex_nnip[value] + " \n")
				script = "no isis enable" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("no isis enable" + " \n")
				script = "no isis spbm 1" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("no isis spbm 1" + " \n")
				script = "no isis" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("no isis " + " \n")
				script = "isis remote" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote" + " \n")
				script = "isis remote spbm 1" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote spbm 1" + " \n")
				if "auto" in nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + "auto" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + "auto" + " \n")
				elif nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + nni_metric[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + nni_metric[value] + " \n")
				else:
					script = "isis spbm 1 l1-metric " + "100" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis spbm 1 l1-metric " + "100" + " \n")
				if isis__auth[value]:
					script = 'isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
				script = "isis remote enable" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote enable" + " \n")
				script = "exit " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("exit " + " \n\n")

			if rm_ho__mlt[value]:
				script = "interface mlt " + rm_ho__mlt[value] + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("interface mlt " + rm_ho__mlt[value] + " \n")
				script = "isis remote" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote" + " \n")
				script = "isis remote spbm 1" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote spbm 1" + " \n")
				if "auto" in nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + "auto" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + "auto" + " \n")
				elif nni_metric[value]:
					script = "isis remote spbm 1 l1-metric " + nni_metric[value] + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis remote spbm 1 l1-metric " + nni_metric[value] + " \n")
				else:
					script = "isis spbm 1 l1-metric " + "200" + " "
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write("isis spbm 1 l1-metric " + "200" + " \n")
				if isis__auth[value]:
					script = 'isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' '
					print(script)
					with open(out_file, 'a') as outfile:
						outfile.write('isis remote hello-auth type hmac-sha-256 key "' + isis__auth[value] + '" key-id 182 ' + ' \n')
				script = "isis remote enable" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("isis remote enable" + " \n")
				script = "exit " + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("exit " + " \n\n")

		if is__mep_id[value] == "":
			print("\n\n\t**** DATA error: for spbm a switch you must specify a mep-id -> excel.csv line " + str(value + 2) + " ")
			quit()
		else:		
			script = "cfm spbm mepid " + is__mep_id[value] + " "
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write("cfm spbm mepid " + is__mep_id[value] + " \n")
		script = "cfm spbm enable " + " "
		print(script)
		with open(out_file, 'a') as outfile:
			outfile.write("cfm spbm enable " + " \n\n")

	if ist___name == "NormIST":
		if not "leaf" in dvr___func[value]:
			script = 'router isis '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('router isis \n')
			script = 'redistribute direct'
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('redistribute direct \n')
			if "yes" in ist_clustr[value]:
				script = 'redistribute direct route-map "suppressIST" '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('redistribute direct route-map "suppressIST" \n')
			script = 'redistribute direct enable '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('redistribute direct enable \n')
			script = 'exit'
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('exit \n\n')

			script = 'isis apply redistribute direct '
			print(script)
			with open(out_file, 'a') as outfile:
				outfile.write('isis apply redistribute direct \n\n')

			if hm_areanme[value]:
				script = "# **** Multi-area configuration L2VSN redistribution" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("# **** Multi-area configuration L2VSN redistribution" + " \n\n")
				script = 'router isis '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('router isis \n')
				script = 'multi-area l2 redistribute i-sid permit-all'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('multi-area l2 redistribute i-sid permit-all \n')
				script = 'exit'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('exit \n\n')
	
				script = 'isis multi-area l2 apply redistribute i-sid'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('isis multi-area l2 apply redistribute i-sid \n\n')

			if hm_areanme[value]:
				script = "# **** Multi-area configuration IP-shortcut redistribution" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("# **** Multi-area configuration IP-shortcut redistribution" + " \n\n")
				script = 'router isis '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('router isis \n')
				script = 'multi-area ip redistribute unicast'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('multi-area ip redistribute unicast \n')
				script = 'exit'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('exit \n\n')
	
				script = 'isis multi-area ip apply redistribute unicast'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('isis multi-area ip apply redistribute unicast \n\n')

			if hm_areanme[value]:
				script = "# **** Multi-area configuration VRF example redistribution" + " "
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write("# **** Multi-area configuration VRF example redistribution" + " \n\n")
				script = '# router vrf green '
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('# router vrf green \n')
				script = '# isis multi-area ip redistribute unicast'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('# isis multi-area ip redistribute unicast \n')
				script = '# exit'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('# exit \n\n')
	
				script = '# isis multi-area ip apply redistribute unicast vrf green'
				print(script)
				with open(out_file, 'a') as outfile:
					outfile.write('# isis multi-area ip apply redistribute unicast vrf green \n\n')

	script = "\nend " + " "
	print(script)
	with open(out_file, 'a') as outfile:
		outfile.write("\nend " + "\n\n")
	script = "save config " + " "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("save config " + " \n\n")
	script = "backup configure 01-spbm-basic " + " "
	print (script)
	with open(out_file, 'a') as outfile:
		outfile.write("backup configure 01-spbm-basic " + " \n\n")
	with open(out_file, 'a') as outfile:
		outfile.write('\n# ***** end of 01-out-spbm-' + promptname[value] + '.cfg ***** \n\n')
	script = "\n ***** program end ***** " + " "
	print(script)
