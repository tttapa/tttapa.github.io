#!/usr/bin/env bash

# Script to download and install GoogleTest

set -ex

version="release-1.10.0" # Release tag on GitHub
builddir="/tmp"
prefix="$HOME/.local"

cd /tmp
# Download
git clone --single-branch --depth=1 --branch $version \
    https://github.com/google/googletest.git
mkdir googletest/build && cd $_
# Configure
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/.local -DCMAKE_BUILD_TYPE=Release
# Build
make -j$(nproc)
# Install
make install