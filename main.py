#!/usr/bin/env python
# @author: Prahlad Yeri
# @description: Small daemon to create a wifi hotspot on linux
# @license: MIT
import sys
import os
import argparse
import cli
import fileinput
import json
import pickle
import socket
import logging
import platform
import datetime
import time

from re import sub as substr
from shutil import copy, copystat
from cli import logger as log

class Proto:
        pass


const = Proto()

#global const = Proto() #struct to hold startup parameters
#const.debug = False
#const.verbose = False
#const.command = 'start'
#const.argv = None

stores = Proto() #struct to dump misc variables
stores.running  = False

install_path = os.path.abspath(__file__)
install_dir = os.path.dirname(install_path)

# config  = ConfigParser.RawConfigParser()

def validate_ip(addr):
	try:
		socket.inet_aton(addr)
		return True # legal
	except socket.error:
		return False # Not legal


def select_interface(interfaces):
        for num, interface in enumerate(interfaces):
                print("{} {}".format(num, interface))
        while True:
                interface_num = raw_input("Enter number to select interface: ")
                try:
                        isinstance(int(interface_num), int)
                        interface_num = int(interface_num)
                        interfaces[interface_num]
                except ValueError:
                        print("Please input an integer")
                        continue
                except IndexError:
                        print("Valid entries are {}".format(range(len(interfaces))))
                        continue

                return interfaces[interface_num]


def configure():
	global wlan, ppp, IP, Netmask
	#CHECK WHETHER WIFI IS SUPPORTED OR NOT
	print('Initiating configuration..')
	wlan=''
	ppp=''

        wiface = wireless_interfaces()
        if wiface:
                if len(wiface) > 1:
                        print('Following wireless interfaces were detected, please select one.')
                        wlan = select_interface(wiface)
                else:
                        print("wlan: {}".format(wiface[0]))
                        wlan = wiface[0]
        else:
		sys.exit('Wireless interface could not be found on your system.\nPlease turn on WIFI.')

        iface = other_interfaces(wlan)
	if iface:
                print("Found interface(s): {}".format(', '.join(iface)))
                if len(iface) > 1:
                        ppp = select_interface(iface)
                else:
                        ppp = iface[0]
        else:
		sys.exit('No network interface found on your deivce to interface with the LAN')

	while True:
		IP = raw_input('Enter an IP address for your AP [192.168.45.1]: ')
		#except: continue
		#print type(IP)
		#sys.exit(0)
		if IP is None or IP == '':
			IP = '192.168.45.1'
		if not validate_ip(IP):
                        continue
		break

        # TODO: Get netmask from user
	Netmask='255.255.255.0'

	#CONFIGURE SSID, PASSWORD, ETC.
	SSID = raw_input('Enter SSID [joe_ssid]: ')
	if SSID == '': SSID = 'joe_ssid'
	password = raw_input('Enter 10 digit password [1234567890]: ')
	if password=='': password='1234567890'

	data = {'wlan': wlan,
                'inet': ppp,
                'ip': IP,
                'netmask': Netmask,
                'SSID': SSID,
                'password': password}

        with open(os.path.join(install_dir, 'samples/hostapd.conf')) as sample_hostapd:
                with open(os.path.join(install_dir, 'hostapd.conf'), 'w') as configfile:
                        subs = {"wlan0": wlan,
                                "joe_ssid": SSID,
                                "1234567890": password}
                        for line in sample_hostapd:
                                for pattern in subs.keys():
                                        if pattern in line:
                                                line = line.replace(pattern, subs[pattern])
                                configfile.write(line)

        pickle.dump(data, open(os.path.join(install_dir, 'hotspotd.data'), 'wb'), -1)
        print("Following data was saved in file hotspotd.data")
        print(data)
	print 'Configuration saved. Run "hotspotd start" to start the router.'

	#CHECK WIFI DRIVERS AND ISSUE WARNINGS


def check_dependencies():
	#CHECK FOR DEPENDENCIES
	if len(cli.check_sysfile('hostapd'))==0:
		print 'hostapd executable not found. Make sure you have installed hostapd.'
		return False
	elif len(cli.check_sysfile('dnsmasq'))==0:
		print 'dnsmasq executable not found. Make sure you have installed dnsmasq.'
		return False
	else:
		return True


def wireless_interfaces():
        w_interfaces = list()
        status, output = cli.execute_shell('iwconfig')
        cli.writelog('in wireless_interfaces')
	for line in output.splitlines():
                if 'IEEE 802.11' in line:
                        w_interfaces.append(line.split()[0])

        return w_interfaces if len(w_interfaces) > 0 else None

def other_interfaces(wlan=None):
        o_interfaces = list()
        status, output = cli.execute_shell('ip -o -4 -6 link show up')
	for line in output.splitlines():
                o_interfaces.append(line.split(':')[1].strip())

        # Remove loopback device
        if 'lo' in o_interfaces:
                o_interfaces.remove('lo')

        # Remove wlan interface used if any. This will also adds
        # ability to use one wireless interface for broadcast and
        # other providing Internet access for system having multiple
        # WIFI modules
        if wlan and wlan in o_interfaces:
                o_interfaces.remove(wlan)

        return o_interfaces if len(o_interfaces) > 0 else None

def check_interfaces():
	global wlan, ppp
	print 'Verifying interfaces'
	status, output = cli.execute_shell('ifconfig')
	lines = output.splitlines()
	bwlan = False
	bppp  = False

	for line in lines:
		if not line.startswith(' ') and len(line)>0:
			text=line.split(' ')[0]
			if text.startswith(wlan):
				bwlan = True
			elif text.startswith(ppp):
				bppp = True

	if not bwlan:
		print wlan + ' interface was not found. Make sure your wifi is on.'
		return False
	elif not bppp:
		print ppp + ' interface was not found. Make sure you are connected to the internet.'
		return False
	else:
		print 'done.'
		return True

def pre_start():
	# oper = platform.linux_distribution()
	# if oper[0].lower()=='ubuntu' and oper[2].lower()=='trusty':
	# trusty patch
	# print 'applying hostapd workaround for ubuntu trusty.'
	#29-12-2014: Rather than patching individual distros, lets make it a default.

        # Start from most recent versions of `nmcli`
        # nmcli tool, version 1.8.2-1.fc26
	status, output = cli.execute_shell('nmcli radio wifi off')
        if status is False:
                # nmcli tool, version 0.9.8.8
	        cli.execute_shell('nmcli nm wifi off')

        # Fedora 26 notes
        # - Need to install rfkill on f26
        # - Need to disable wpa_supplicant service
        # `rfkill list` (output)
        # 0: tpacpi_bluetooth_sw: Bluetooth
	# Soft blocked: yes
	# Hard blocked: no
        # 1: phy0: Wireless LAN
	# Soft blocked: yes
	# Hard blocked: no
        #
        # `rfkill unblock wifi`
	# Soft blocked: yes
	# Hard blocked: no
        # 1: phy0: Wireless LAN
	# Soft blocked: no
	# Hard blocked: no
        #
        # `hostapd -B /usr/lib/python2.7/site-packages/hotspotd/hostapd.conf`
        # Configuration file: /usr/lib/python2.7/site-packages/hotspotd/hostapd.conf
        # Using interface wlp3s0 with hwaddr 3a:96:67:2d:e5:4a and ssid "nubia"
        # wlp3s0: interface state UNINITIALIZED->ENABLED
        # wlp3s0: AP-ENABLED

	cli.execute_shell('rfkill unblock wifi')
	cli.execute_shell('sleep 1')


def start_router():
        data = load_data()
        wlan = data['wlan']
        ppp = data['inet']
        IP = data['ip']
        Netmask = data['netmask']

        cli.writelog('Starting hotspot')
	if not check_dependencies():
		return
	pre_start()
        # wireless_interfaces()

        # NOTE: `ifconfig` is deprecated in favor of `ip`
	s = 'ifconfig ' + wlan + ' up ' + IP + ' netmask ' + Netmask
	print('created interface: mon.' + wlan + ' on IP: ' + IP)
	status, output = cli.execute_shell(s)
	cli.writelog(output)
	#cli.writelog('sleeping for 2 seconds.')
	cli.execute_shell('sleep 2')
	i = IP.rindex('.')
	ipparts=IP[0:i]

	#stop dnsmasq if already running.
	cli.killall('dnsmasq')

	#stop hostapd if already running.
	cli.killall('hostapd')

	#enable forwarding in sysctl.
	print 'enabling forward in sysctl.'
	r=cli.set_sysctl('net.ipv4.ip_forward','1')
	print r.strip()

	#enable forwarding in iptables.
	print 'creating NAT using iptables: ' + wlan + '<->' + ppp
	cli.execute_shell('iptables -P FORWARD ACCEPT')

	#add iptables rules to create the NAT.
	cli.execute_shell('iptables --table nat --delete-chain')
        cli.execute_shell('iptables --table nat -F')
        cli.execute_shell('iptables --table nat -X')
        cli.execute_shell('iptables -t nat -A POSTROUTING -o ' + ppp +  ' -j MASQUERADE')
        cli.execute_shell('iptables -A FORWARD -i ' + ppp + ' -o ' + wlan + ' -j ACCEPT -m state --state RELATED,ESTABLISHED')
        cli.execute_shell('iptables -A FORWARD -i ' + wlan + ' -o ' + ppp + ' -j ACCEPT')

	#allow traffic to/from wlan
	cli.execute_shell('iptables -A OUTPUT --out-interface ' + wlan + ' -j ACCEPT')
        cli.execute_shell('iptables -A INPUT --in-interface ' + wlan +  ' -j ACCEPT')

	#start dnsmasq
        cli.writelog('running dnsmasq')
	s = 'dnsmasq --dhcp-authoritative --interface=' + wlan + ' --dhcp-range=' + ipparts + '.20,' + ipparts +'.100,' + Netmask + ',4h'
	r = cli.execute_shell(s)

	#~ f = open(os.getcwd() + '/hostapd.tem','r')
	#~ lout=[]
	#~ for line in f.readlines():
		#~ lout.append(line.replace('<SSID>',SSID).replace('<PASS>',password))
		#~
	#~ f.close()
	#~ f = open(os.getcwd() + '/hostapd.conf','w')
	#~ f.writelines(lout)
	#~ f.close()

	#writelog('created: ' + os.getcwd() + '/hostapd.conf')

        #start hostapd
        cli.writelog('running hostapd')
	#s = 'hostapd -B ' + os.path.abspath('run.conf')
	s = 'hostapd -B ' + os.path.join(install_dir, 'hostapd.conf')
	cli.execute_shell('sleep 2')
	cli.execute_shell(s)
	print 'hotspot is running.'
	return

def stop_router():
        data = load_data()
        wlan = data['wlan']
        ppp = data['inet']

        cli.writelog('Stopping hotspot')
        cli.writelog('Bringing down interface: {}'.format(wlan))
        cli.execute_shell('ifconfig mon.' + wlan + ' down')
        # logger.info('ifconfig mon.' + wlan + ' down')

	#TODO: Find some workaround. killing hostapd brings down the wlan0 interface in ifconfig.
	#~ #stop hostapd
	#~ if cli.is_process_running('hostapd')>0:
		#~ cli.writelog('stopping hostapd')
		#~ cli.execute_shell('pkill hostapd')

        # Stop dependent services
	cli.writelog('Stopping dnsmasq')
	cli.killall('dnsmasq')
        cli.writelog('Stopping hostapd')
	cli.killall('hostapd')

	#Delete forwarding in iptables.
	cli.writelog('Delete forward rules in iptables.')
        cli.execute_shell('iptables -D FORWARD -i ' + ppp + ' -o ' + wlan + ' -j ACCEPT -m state --state RELATED,ESTABLISHED')
        cli.execute_shell('iptables -D FORWARD -i ' + wlan + ' -o ' + ppp + ' -j ACCEPT')


	#delete iptables rules that were added for wlan traffic.
	if wlan != None:
		cli.execute_shell('iptables -D OUTPUT --out-interface ' + wlan + ' -j ACCEPT')
	        cli.execute_shell('iptables -D INPUT --in-interface ' + wlan +  ' -j ACCEPT')

	cli.execute_shell('iptables --table nat --delete-chain')
        cli.execute_shell('iptables --table nat -F')
        cli.execute_shell('iptables --table nat -X')

        #disable forwarding in sysctl.
        cli.writelog('disabling forward in sysctl.')
	r = cli.set_sysctl('net.ipv4.ip_forward','0')
	print r.strip()
	#cli.execute_shell('ifconfig ' + wlan + ' down'  + IP + ' netmask ' + Netmask)
	#cli.execute_shell('ip addr flush ' + wlan)
	print 'hotspot has stopped.'
	return


def load_data():
        if os.path.exists(os.path.join(install_dir, 'hotspotd.data')):
                return pickle.load(
                        open(os.path.join(install_dir, 'hotspotd.data'),
                             'rb'))
        cli.writelog("Looks like hotspotd was never configured.\nReason: Could not load file: {}".format(os.path.join(install_dir, 'hotspotd.data')))
        sys.exit("Looks like hotspotd was never configured.\nCheck status using `hotspotd status`")


def main(args):
	global wlan, ppp, IP, Netmask
	the_version = open("VERSION").read().strip()
	print "****"
	print "Hotspotd " + the_version
	print "A simple daemon to create wifi hotspot on Linux!"
	print "****"
	print "Copyright (c) 2014-2016"
	print "Prahlad Yeri<prahladyeri@yahoo.com>\n"

	# scpath = os.path.realpath(__file__)
        # print(scpath)
	# realdir = os.path.dirname(scpath)
	# os.chdir(realdir)
	#print 'changed directory to ' + os.path.dirname(scpath)
	#if an instance is already running, then quit
	#const.verbose = args.verbose
	#const.command = args.command
	#const.blocking = args.blocking
	#const.argv = [os.getcwd() + '/server.py'] + sys.argv[1:]


	cli.arguments = args #initialize

	if len(cli.check_sysfile('hostapd'))==0:
		print "hostapd is not installed on your system. \
                This package will not work without it.\nTo install \
                hostapd, run 'sudo apt-get install hostapd'\nor \
                refer to http://wireless.kernel.org/en/users/\
                Documentation/hostapd after this installation gets over."
		time.sleep(2)

	# wlan = dc['wlan']
	# ppp = dc['inet']
	# IP=dc['ip']
	# Netmask=dc['netmask']
	# SSID = dc['SSID']
	# password = dc['password']

	if args.command == 'configure':
		configure()
	elif args.command == 'status':
                if (cli.is_process_running('hostapd')[0] is False and cli.is_process_running('dnsmasq')[0] is False):
                        print('hostspotd is not running')
                else:
                        print('Either hostapd or dnsmasq or both are running')
	elif args.command == 'stop':
		stop_router()
	elif args.command == 'start':
		if (cli.is_process_running('hostapd') is False or cli.is_process_running('dnsmasq') is False):
			print('hotspot is already running')
		else:
                        if not os.path.exists(os.path.join(install_dir, 'hotspotd.data')):
		                configure()
			start_router()
