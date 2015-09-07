# Yandex DNS Updater for Asuswrt-Merlin
A Python script to update Yandex DNS records IP address.

## Prerequisites
* [Asuswrt-Merlin](https://github.com/RMerl/asuswrt-merlin) installed on your router
* Python 2 or Python 3 may be installed through
    * Optware: `ipkg install python python-expat python-openssl`
    * Optware-ng: `ipkg install python27 py27-openssl` or `ipkg install python3 py3-openssl`
    * Entware: `opkg install python python-openssl`
* Git may be installed through:
    * Optware & Optware-ng: `ipkg install git`
    * Entware: `opkg install git`
* JFFS partition with custom scripts enabled

## Installing
Modify values to match your specific installation

    # SSH to your router
    ssh -p port username@router
    # Move to USB directory
    cd /tmp/mnt/FLASH
    # Clone a repository to it
    git clone https://github.com/kovalexal/yandexdns.git
    # Edit a YANDEXDNS variable to math correct path
    nano ./yandexdns/ddns-start
    # Edit a config file
    cp ./yandexdns/settings.conf.example ./yandexdns/settings.conf; nano ./yandexdns/settings.conf
    # Copy custom ddns script to jffs partition
    cp ./yandexdns/ddns-start /jffs/scripts
    chmod 777 /jffs/scripts/ddns-start