from netmiko import ConnectHandler, ssh_exception
from paramiko.ssh_exception import SSHException
from datetime import datetime
from getpass import getpass
import os
import subprocess
import re
import sys

print("Mac Search at KK\n")
print("We are not handling access points, if you get an error, please call noc")

#### Ask for mac address ###########
mcaddress = input('mac address: ').strip()
#print (mcaddress)
macpt = re.compile(r"[a-f0-9]{4,4}\.[a-f0-9]{4,4}\.[a-f0-9]{4,4}")
checkmac = macpt.search(mcaddress)
if checkmac == None:
    print("Mac address not given or not in correct format!")
    print("Example: xxxx.yyyy.zzzz with Cisco notation, chars in a-f and numbers in 0-9 ranges")
    sys.exit(1)
#### Ask for starting switch ip address ###########
startswitchip = input('switch to start from: ').strip()
ippt = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
checkip = ippt.search(startswitchip)
if checkip == None:
    print("IP address not given or not in correct format!")
    print("Example: 0-255.0-255.0-255.0-255 with IPv4 ranges")
    sys.exit(1)

user = input('username:')
passwd = getpass()

ipaddress = startswitchip
platform = "6509"
addresstype = "dynamic"
vlanid = ""

while ("STATIC" not in addresstype) and ("static" not in addresstype):
    if "2950" not in platform:
        contype = "cisco_ios_ssh"
        cmdstring = "sh mac address-table | in " + mcaddress
        if "6509" in platform:
            portpt = re.compile(r"\s+(?P<vlanid>\S+)\s+\S+\s+(?P<addresstype>\S+)\s+\S+\s+\S+\s+(?P<port>\S+)")
        else:
            portpt = re.compile(r"\s+(?P<vlanid>\S+)\s+\S+\s+(?P<addresstype>\S+)\s+(?P<port>\S+)")
    else:
        contype = "cisco_ios_telnet"
        cmdstring = "sh mac-address-table | in " + mcaddress
        portpt = re.compile(r"\s+(?P<vlanid>\S+)\s+\S+\s+(?P<addresstype>\S+)\s+(?P<port>\S+)")

    swcon = {
        'device_type': contype,
        'ip': ipaddress,
        'username': user,
        'password': passwd,
    }

    try:
        net_connect = ConnectHandler(**swcon)
    except SSHException:
        print ("can't connect to last device")
        sys.exit(1)
    except ssh_exception.NetMikoTimeoutException:
        print("  SSH Timed out")
        sys.exit(1)
    except ssh_exception.NetMikoAuthenticationException:
        print("Invalid Credentials: ", ipaddress)
        sys.exit(1)

    output = net_connect.send_command_timing(cmdstring).strip("*")

    findport = portpt.search(output)

    if findport == None:
        print("Address not found")
        addresstype = "STATIC"
        net_connect.disconnect()
        break

    portfound = findport.group('port')
    addresstype = findport.group('addresstype')
    vlanid = findport.group('vlanid')

    print ()
    print ("Mac port:", portfound)
    print ("Address Type:", addresstype)

    if ("dynamic" not in addresstype) and ("DYNAMIC" not in addresstype):
        print("\nWe found it!")
        #output = net_connect.send_command_timing("sh run int " + portfound +"\n")
        print ("Mac port:", portfound, "on vlan", vlanid, "at", ipaddress)
    else:
        print("\nIt's on another switch, we need to look further through", portfound)
        cmdstring = "sh cdp neighbors " + portfound +" detail"
        output = net_connect.send_command_timing(cmdstring)

        ######### Find ip address and plaform for CDP Neighbor ################
        ippt = re.compile(r"\s+IP address:\s+(?P<ipaddress>\d+\.+\d+\.\d+\.\d+)")
        platformpt = re.compile(r"Platform: cisco WS-C(?P<platform>\w+)")

        findaddress = ippt.search(output)
        findplatform = platformpt.search(output)

        ipaddress = findaddress.group('ipaddress')
        platform = findplatform.group('platform')
        print ("Next Neightbor IP Address:", ipaddress)
        print ("Next Neighbor Platform:", platform)

    net_connect.disconnect()

print ('done testing')
