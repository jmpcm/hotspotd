# Introduction

**hotspotd** is a daemon to create a wifi hotspot on GNU/Linux. It
depends on `hostapd` for AP provisioning and `dnsmasq` to assign IP
addresses to devices.

## Install


### Install dependencies on Ubuntu:

```
sudo apt-get install hostapd dnsmasq -y
```

### Install dependencies on RHEL/CentOS:

```
sudo yum install hostapd dnsmasq rfkill -y
```

To install hotspotd,
```
wget https://github.com/prahladyeri/hotspotd/raw/master/dist/hotspotd-latest.tar.gz
tar xvf hotspotd-latest.tar.gz
cd hotspotd-latest/
sudo python setup.py install
```

## Uninstall/Remove
To uninstall hotspotd,
```
sudo python setup.py uninstall
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

- To start hotspot:

	```
	sudo hotspotd start
	```

- To stop hotspot:

	```
	sudo hotspotd stop
	```


## Troubleshooting

- `hotspotd` creates following log file for troubleshooting
  - `hotspotd_info.log`: The text you see on screen.
  - `hotspotd_error.log`: Typically will catch any *python* error.
  - `hotspotd_debug.log`: Will log everything

* hotspotd creates the NAT by manipulating iptables rules. So if you have any other firewall software that manipulates the iptables rules (such as the firewalld on fedora), make sure you disable that.


* To create a hotspot, your wifi must support AP mode. To find that out, use this process:

	* Find your kernel driver module in use by issuing the below command:

		```lspci -k | grep -A 3 -i network```

		(example module: ath9k)

	* Now, use the below command to find out your wifi capabilities (replace ath9k by your kernel driver):

		```modinfo ath9k | grep depend```

	* If the above output includes “mac80211” then it means your wifi card will support the AP mode.

#Testing status
This package has been tested on Qualcomm Atheros adapter on the following distros:

* Ubuntu 12.04 LTS
* Ubuntu 14.04 LTS

In theory, it should work with all other distros too (on machines having wifi adapters supported by hostapd), but you will have to try that out and tell me!

#Notes
* Replace `sudo` with `su` or `su -c` if you manage superuser access in that manner.
* PyPI home page could be found at https://pypi.python.org/pypi/hotspotd.
* I need someone to test this daemon across various linux distros. If you are interested in testing of open-source apps, please contact me.
