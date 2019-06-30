#!/usr/bin/env bash

set -ex

sudo apt-get install -y \
    libudev-dev libical-dev libreadline-dev libdbus-1-dev libasound2-dev \
    build-essential

cd /tmp 
wget https://mirrors.edge.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
tar -xf bluez-5.50.tar.xz

cd bluez-5.50
./configure --enable-midi --with-systemdsystemunitdir=/etc/systemd/system
make
sudo make install
sudo apt-get install --reinstall bluez