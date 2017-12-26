# Introduction

**hotspotd** is a daemon to create a wifi hotspot on GNU/Linux. It
depends on `hostapd` for AP provisioning and `dnsmasq` to assign IP
addresses to devices.

## Install


### Install dependencies on Ubuntu:

```
sudo apt-get install hostapd dnsmasq  rfkill -y
```

### Install dependencies on RHEL/CentOS/Fedora:

```
sudo yum install hostapd dnsmasq rfkill -y
```

### Other distros
Make sure to have following packages installed:
- `dnsmasq`
- `hostapd`
- `rfkill`
- Python-3.6 with `setuptools`

To install hotspotd,
```
sudo pip install https://github.com/psachin/hotspotd/raw/py3/dist/hotspotd-0.1.8.tar.gz
```

## Uninstall/Remove

```
sudo pip uninstall hotspotd
```

Following dependencies should be removed manually(Optional)
- `dnsmasq`
- `hostapd`
- `rfkill`

## Usage

- Configure

	Please configure `hotspot` before you start for first time using,
	```
	sudo hotspotd configure
	```
	*Note: Everytime 'configure' is run, new settings will take effect.*

- To start hotspot:

	```
	sudo hotspotd start
	```

- To stop hotspot:

	```
	sudo hotspotd stop
	```


## Troubleshooting

* `hotspotd` will dump logs on `/var/log/hotspotd.log`. Use for
  debugging and attaching logs while openinig issues.

* `hotspotd` creates the NAT by manipulating iptables rules. So if you
  have any other firewall software that manipulates the iptables rules
  (such as the firewalld on fedora), make sure you disable that.


* To create a hotspot, your wifi must support AP mode. To find that
  out, use this process:

	* Find your kernel driver module in use by issuing the below command:

		```
		lspci -k | grep -A 3 -i network
		```

		(example module: `ath9k`)

	* Now, use the below command to find out your wifi capabilities
      (replace `ath9k` by your kernel mmodule):

		```
		modinfo ath9k | grep depend
		```

	* If the above output includes `mac80211` then it means your wifi
      card will support the AP mode.

## Test status

This package has been tested on the following GNU/Linux distributions:

* Ubuntu 12.04 LTS(Qualcomm Atheros adapter)
* Ubuntu 14.04 LTS(Qualcomm Atheros adapter)
* Slackware 14.1(Broadcom Corporation BCM4313 802.11b/g/n Wireless LAN Controller)
* Fedora 26 & 27(Intel Corporation Wireless 7260)
* Manjaro-4.14.x(Arch Linux). Need to install `wireless_tools` &
  `hostapd` using `pacman -S wireless_tools hostapd`
* RaspberryPi 2(Model B V1.1) with [raspbian](https://www.raspberrypi.org/downloads/raspbian/)

In theory, it should work with all other distros too (on machines
having wifi adapters supported by hostapd), but you will have to try
that out and tell me!

## Notes
* Replace `sudo` with `su` or `su -c` if you manage superuser access
  in that manner.
* PyPI home page could be found at https://pypi.python.org/pypi/hotspotd
* I need someone to test this daemon across various linux distros. If
  you are interested in testing of open-source apps, please create an [issue](https://github.com/prahladyeri/hotspotd/issues/new)
