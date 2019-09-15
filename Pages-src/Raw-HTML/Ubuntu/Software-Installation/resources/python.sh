#!/usr/bin/env bash

# Script to download and build Python 3 from source

set -ex

version="3.7.4"
builddir="/tmp"
python="Python-$version"
prefix="$HOME/.local"

# Install dependencies and build tools
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install -y \
	zlib1g-dev libbz2-dev libssl-dev uuid-dev libffi-dev libreadline-dev \
	libsqlite3-dev tk-dev libbz2-dev libncurses5-dev libreadline6-dev \
	libgdbm-dev liblzma-dev \
	wget make gcc-9 g++-9

# For Ubuntu 18.04 and later, another dependency is required for GNU dbm
source /etc/os-release
if (( $(echo "$VERSION_ID >= 18.04" | bc -l) ));
then
	sudo apt-get install libgdbm-compat-dev
fi

# Download and extract the Python source code
mkdir -p "$builddir"
cd $builddir
if [ ! -d "$python" ]
then
	wget "https://www.python.org/ftp/python/$version/$python.tgz"
	tar xf $python.tgz
fi

cd "$python"
./configure --prefix="$prefix" \
	--enable-ipv6 \
	--enable-shared --with-lto --enable-optimizations \
	CC=gcc-9 CXX=g++-9 \
	'LDFLAGS=-Wl,-rpath,\$$ORIGIN/../lib'

make -j$[$(nproc) * 2]
make altinstall