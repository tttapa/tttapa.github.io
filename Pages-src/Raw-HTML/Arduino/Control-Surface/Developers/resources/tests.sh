#!/usr/bin/env bash

set -ex

# Install the GCC 9 compiler, GNU Make, CMake and Git
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test  # Repository for GCC 9
sudo apt update
sudo apt install -y gcc-9 g++-9 make cmake git

# Clone the Control Surface repository, including submodules
git clone --recursive https://github.com/tttapa/Control-Surface.git

# Create a directory to build everything
mkdir -p Control-Surface/build && cd Control-Surface/build

# Export the compiler to use
export CC=gcc-9
export CXX=g++-9

# Run CMake to generate the Makefiles
cmake ..

# Build Control Surface and run the tests
make -j$[$(nproc) * 2] check