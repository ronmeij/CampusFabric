# CampusFabric
This project provides a way to generate configuration scripts for the setup of a complex Campus Fabric solution.

The configuration is based on a modular approach; for each module a separate excel file (xlsx) is required.
There are 5 modules:
- 01 SPBm parameters 
- 02 VRF configuration settings
- 03 VLAN and IP settings 
- 04 VRF circuitless IP addresses 
- 05 Interface configuration (VLAN/I-SID assignments)

For the setup of switch Clusters (IST/vIST); two options are supported:
- vIST setup for SPBm deployment (default)
- Simplified IST for legacy deployment


Current supported features are:
  
  01 SPBm paramaters:
  - Cluster setup (SPB switch, DVR CTRL and DVR LEAF)
  - external banner file (01-banner.txt)
  - external motd file (01-motd.txt)
  - ISIS hello authentication
  - ISIS loopback IP
  - ISIS metric (auto or manual)
  - MSTP bridge priority
  - NNI MLT support (2 MLTs per switch)
  - Multi-area support
  - NTP server (2) support
  - Segmented management for CLIP, VLAN and OoB
  - SLPP setup (slpp-guard (timeout default 60s), slpp-guard-dis (timeout set to 0) or slpp-packet-rx values)
  - SNMP basics (sysLocation, sysContact)
  - Syslog host support
  - TransferHost setup
  - VLACP on NNI

  02 VRF configuration settings:
  - ISIS redistribution settings
  - VRF L3VSN, id and name
  - VRF/GRT IP unicast/multicast settings

  03 VLAN and IP settings (12 switches per sheet):
  - DHCP relay (4 agents)
  - Anycast-gateway (IP and one-IP)
  - DVR (ip and one-IP)
  - IGMP, multicast and multicast config-lite
  - OSPF passive interface
  - RSMLT (edge support)
  - VLAN id, name, L2VSN and VRF
  - VRRP (2 instances per VLAN)
  - Wake on LAN (directed broadcast)
  - If the field 'IP address' under the switch name is left empty the VLAN is created as L2-VSN
  - If 'nocreate' instead 'IP address' is used the VLAN is not created on the switch
  - If 'mc-config-lite' instead 'IP address' is used the VLAN is created for 'mc-config-lite'
  - With 'd' before the IP netmask the IP interface is created in state-disabled
  - A file is created with the required 'ip interface enable' commands

  04 VRF circuitless IP addresses (12 switches per sheet)
  - VRF circuitless IP address
  
  05 Interface configuration (VLAN/I-SID assignments)
  - Fabric Attach support (with or without mgmt VLAN)
  - Interface name and description
  - Interface/switch migration documentation support
  - LACP (long or short timers) and 802.3ad static support
  - SMLT support (VLANid check build-in)
  - SNMP linktrap
  - Tagging (802.1Q)
  - UNI types supported are Switched-UNI (Flex-UNI) and C-VLAN UNI
  - VLAN list support (with dashes)

