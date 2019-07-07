# findmacaddress
Python script to search for certain mac address in Legacy Cisco enabled Campus LAN 
Assumptions: 
You are working as a network admin on a company that has legacy cisco equipment on a campus lan (like Catalyst 65k for core, 2950s and 2960s for access). Your help desk team often connects workstations to the LAN but the available access ports are on a dummy vlan, so you need to locate the port the workstation is connected to in order to change that access vlan to a working one. If your cabling is well structured, you should be able to know exactly which switch port you are connecting the workstation to. But what if it's not?

This is a script that will automate locating that mac addresses on a campus lan fast. That involves locating the access switch and the access port that the workstation has connected to and changing the access vlan.

This part of the code is written in Python and handles the locating the mac address part. Up to this point, it’s usefull for the network admins, gaining some time to complete what they already know how to do by themselves. 
It would be better if it was part of a larger project, providing a secured web based access to this tool so that it can be run on a self-service basis.

Obviously the script depends largely on the local infrastructure and has to be adjusted before it can be used elsewhere. It basically starts on a core switch where the mac address will show up when connected anywhere on the campus Lan. It then follows the mac address through CDP until the final access switch is found where the address is shown on the mac address table as type STATIC. It uses regular expressions to do a few things like checking for the mac address input, locating the info from the mac address table (vlan, port, address type) and also some info from the cdp neighbour command (neighbour ip address and platform). It also checks for connection failure and the event that the mac address is not found anywhere. I am sure you can add things on your own and provide improvements. It’s just an idea, I am sure a lot of people can do a lot better. I changed some data for confidentiality issues.

Finally the script uses regex but for grabbig command output, buttextfsm and ntc-templates can be used instead with minimal modifications.
