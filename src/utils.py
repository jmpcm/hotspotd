# @author: Prahlad Yeri
# @description: Utilities for hotspotd
# @license: MIT
import logging
import logging.config
import pickle
import socket
import subprocess
import sys

from os import path

from .config import log_config

logging.config.dictConfig(log_config)
logger = logging.getLogger('hotspotd.utils')
install_path = path.abspath(__file__)
install_dir = path.dirname(install_path)


def killall(process):
    execute_shell('pkill ' + process)


def is_process_running(process):
    cmd = 'pgrep ' + process
    return execute_shell(cmd)


def check_sysfile(filename):
    if path.exists('/usr/sbin/' + filename) or path.exists('/sbin/' + filename):  # noqa
        return True
    else:
        return False


def set_sysctl(setting, value):
    return execute_shell('sysctl -w ' + setting + '=' + value)[1]


def execute_shell(command, error=''):
    logger.debug("CMD: {}".format(command))
    return execute(command, wait=True, shellexec=True, errorstring=error)


def execute(command='', errorstring='', wait=True, shellexec=False, ags=None):
    try:
        p = subprocess.Popen(command.split(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if wait and p.wait() == 0:
            return True, p.communicate()[0]
        else:
            return False, p.communicate()[0]

    except subprocess.CalledProcessError as err:
        logger.error(err)
    except Exception as err:
        logger.error(err)


def validate_ip(addr):
    try:
        socket.inet_pton(socket.AF_INET, addr)
        return True  # legal
    except socket.error as err:
        logger.error(err)
        return False  # Not legal


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


def wireless_interfaces():
    w_interfaces = list()
    status, output = execute_shell('iwconfig')
    for line in output.splitlines():
        if 'IEEE 802.11' in line:
            w_interfaces.append(line.split()[0])

    return w_interfaces if len(w_interfaces) > 0 else None


def other_interfaces(wlan=None):
    o_interfaces = list()
    status, output = execute_shell('ip -o -4 -6 link show up')
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


def configure():
    logger.info('Initiating configuration..')

    wiface = wireless_interfaces()
    if wiface:
        if len(wiface) > 1:
            print('Following wireless interfaces were detected, please select one.')  # noqa
            wlan = select_interface(wiface)
        else:
            print("wlan: {}".format(wiface[0]))
            wlan = wiface[0]
    else:
        sys.exit('Wireless interface could not be found on your system. \
        Please turn on WIFI.')

    iface = other_interfaces(wlan)
    if iface:
        print("Found interface(s): {}".format(', '.join(iface)))
        if len(iface) > 1:
            ppp = select_interface(iface)
        else:
            ppp = iface[0]
    else:
        message = 'No network interface found to interface with LAN'
        logger.error(message)
        sys.exit(message)

    while True:
        ipaddress = raw_input('Enter an IP address for your AP [192.168.45.1]: ')  # noqa
        if ipaddress is None or ipaddress == '':
            ipaddress = '192.168.45.1'
        elif validate_ip(ipaddress) is False:
            continue
        break

    # TODO: Get netmask from user
    netmask = '255.255.255.0'

    # Configure SSID, password, etc.
    ssid = raw_input('Enter SSID [joe_ssid]: ')
    if ssid == '':
        ssid = 'joe_ssid'

    password = raw_input('Enter 10 digit password [1234567890]: ')
    if password == '':
        password = '1234567890'

    data = {'wlan': wlan,
            'inet': ppp,
            'ipaddress': ipaddress,
            'netmask': netmask,
            'ssid': ssid,
            'password': password}

    with open(path.join(install_dir.strip('hotspotd'), 'samples/hostapd.conf')) as sample_hostapd:  # noqa
        with open(path.join(install_dir, 'hostapd.conf'), 'w') as configfile:  # noqa
            subs = {"wlan0": wlan,
                    "joe_ssid": ssid,
                    "1234567890": password}

            for line in sample_hostapd:
                for pattern in subs.keys():
                    if pattern in line:
                        line = line.replace(pattern, subs[pattern])
                configfile.write(line)

    pickle.dump(data, open(path.join(install_dir, 'hotspotd.data'), 'wb'), -1)  # noqa
    print("Following data was saved in file hotspotd.data")
    print(data)
    print('Configuration saved. Run "hotspotd start" to start the router.')


def pre_start():
    # oper = platform.linux_distribution()
    # if oper[0].lower()=='ubuntu' and oper[2].lower()=='trusty':
    # trusty patch
    # print 'applying hostapd workaround for ubuntu trusty.'
    # 29-12-2014: Rather than patching individual distros, lets make it a
    # default.

    # Start from most recent versions of `nmcli`
    # nmcli tool, version 1.8.2-1.fc26
    status, output = execute_shell('nmcli radio wifi off')
    if status is False:
        # nmcli tool, version 0.9.8.8
        execute_shell('nmcli nm wifi off')

    # Fedora 26 notes:
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
    # Configuratio file: /usr/lib/python2.7/site-packages/hotspotd/hostapd.conf
    # Using interface wlp3s0 with hwaddr 3a:96:67:2d:e5:4a and ssid "nubia"
    # wlp3s0: interface state UNINITIALIZED->ENABLED
    # wlp3s0: AP-ENABLED

    execute_shell('rfkill unblock wifi')
    execute_shell('sleep 1')


def check_dependencies():
    if check_sysfile('hostapd') is False:
        sys.exit('hostapd executable not found. Make sure you have \
        installed hostapd.')
    elif check_sysfile('dnsmasq') is False:
        sys.exit('dnsmasq executable not found. Make sure you have \
        installed dnsmasq.')


def load_data():
    if path.exists(path.join(install_dir, 'hotspotd.data')):
        return pickle.load(
            open(path.join(install_dir, 'hotspotd.data'),
                 'rb'))

    logger.debug("Reason: Could not load file: {}".format(
        path.join(install_dir, 'hotspotd.data')))
    sys.exit("Looks like hotspotd was never configured.\nCheck status using `hotspotd status`")  # noqa


def start_router():
    data = load_data()
    wlan = data['wlan']
    ppp = data['inet']
    ipaddress = data['ipaddress']
    netmask = data['netmask']

    print('Starting hotspot')
    check_dependencies()
    pre_start()

    # TODO: `ifconfig` is deprecated in favor of `ip`. Try to use `ip`
    s = 'ifconfig ' + wlan + ' up ' + ipaddress + ' netmask ' + netmask
    logger.info('created interface: mon.' + wlan + ' on IP: ' + ipaddress)
    status, output = execute_shell(s)
    execute_shell('sleep 2')
    i = ipaddress.rindex('.')
    ipparts = ipaddress[0:i]

    # stop dnsmasq if already running.
    killall('dnsmasq')

    # stop hostapd if already running.
    killall('hostapd')

    # enable forwarding in sysctl.
    logger.info('enabling forward in sysctl.')
    set_sysctl('net.ipv4.ip_forward', '1')

    # enable forwarding in iptables.
    logger.info('creating NAT using iptables: ' + wlan + '<->' + ppp)
    execute_shell('iptables -P FORWARD ACCEPT')

    # add iptables rules to create the NAT.
    execute_shell('iptables --table nat --delete-chain')
    execute_shell('iptables --table nat -F')
    execute_shell('iptables --table nat -X')
    execute_shell('iptables -t nat -A POSTROUTING -o ' + ppp + ' -j MASQUERADE')  # noqa
    execute_shell('iptables -A FORWARD -i ' + ppp + ' -o ' + wlan + ' -j ACCEPT -m state --state RELATED,ESTABLISHED')  # noqa
    execute_shell('iptables -A FORWARD -i ' + wlan + ' -o ' + ppp + ' -j ACCEPT')  # noqa

    # allow traffic to/from wlan
    execute_shell('iptables -A OUTPUT --out-interface ' + wlan + ' -j ACCEPT')
    execute_shell('iptables -A INPUT --in-interface ' + wlan + ' -j ACCEPT')

    # start dnsmasq
    logger.info('Running dnsmasq')
    s = 'dnsmasq --dhcp-authoritative --interface=' + wlan + ' --dhcp-range=' + ipparts + '.20,' + ipparts + '.100,' + netmask + ',4h'  # noqa
    execute_shell(s)

    # start hostapd
    logger.info('Running hostapd')
    s = 'hostapd -B ' + path.join(install_dir, 'hostapd.conf')
    execute_shell('sleep 2')
    execute_shell(s)
    print('hotspot is running.')


def stop_router():
    data = load_data()
    wlan = data['wlan']
    ppp = data['inet']

    logger.info('Stopping hotspot')
    logger.debug('Bringing down interface: {}'.format(wlan))
    execute_shell('ifconfig mon.' + wlan + ' down')

    # TODO: Find some workaround. killing hostapd brings down the
    # wlan0 interface in ifconfig.

    # stop hostapd
    # if cli.is_process_running('hostapd')>0:
    # cli.writelog('stopping hostapd')
    # cli.execute_shell('pkill hostapd')

    # Stop dependent services
    logger.info('Stopping dnsmasq')
    killall('dnsmasq')
    logger.info('Stopping hostapd')
    killall('hostapd')

    # Delete forwarding in iptables.
    logger.info('Delete forward rules in iptables.')
    execute_shell('iptables -D FORWARD -i ' + ppp + ' -o ' + wlan + ' -j ACCEPT -m state --state RELATED,ESTABLISHED')  # noqa
    execute_shell('iptables -D FORWARD -i ' + wlan + ' -o ' + ppp + ' -j ACCEPT')  # noqa

    # delete iptables rules that were added for wlan traffic.
    execute_shell('iptables -D OUTPUT --out-interface ' + wlan + ' -j ACCEPT')
    execute_shell('iptables -D INPUT --in-interface ' + wlan + ' -j ACCEPT')

    execute_shell('iptables --table nat --delete-chain')
    execute_shell('iptables --table nat -F')
    execute_shell('iptables --table nat -X')

    # disable forwarding in sysctl.
    logger.info('disabling forward in sysctl.')
    set_sysctl('net.ipv4.ip_forward', '0')

    # cli.execute_shell('ifconfig ' + wlan + ' down'  + IP + ' netmask ' + Netmask)  # noqa
    # cli.execute_shell('ip addr flush ' + wlan)
    logger.info('hotspot has stopped.')
